import logging
import os
from django.http import HttpResponseRedirect
from apps.users.tasks import (
    send_app_registration_verification_email,
    send_user_credential_reset_email,
    send_user_registration_verification_email,
)
from utils.error_handler import process_error_response
from utils.generics import add_request_data_to_span
from apps.users import serializers
from apps.users.models import User, UserType
from apps.users.signals import role_assignment_signal
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status
from utils.auth import (
    create_client_id_and_secret,
    get_tokens_for_user,
    has_expected_permissions,
    verify_user_token,
)
from opentelemetry import trace
from django.contrib.auth.models import Group

logger = logging.getLogger("app_logger")
tracer = trace.get_tracer(__name__)


class CreateUser(CreateAPIView):
    serializer_class = serializers.UserFetchSerializer
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.UserCreationSerializer},
        responses={201: serializers.UserFetchSerializer},
    )
    # IP restricted endpoint
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(
                f"Initiating user creation with username {request.data['username']}"
            )

            serializer = serializers.UserCreationSerializer(data=request.data)
            if serializer.is_valid():
                resp = serializer.save()
                role_name = (
                    request.data.get("role")
                    if request.data.get("role")
                    else "fuatilia_verifier"
                )

                user = User.objects.get(id=resp.id)

                # Don't do celery stuff in pytest mode -Git actions
                if os.environ.get("ENVIRONMENT", "") != "test":
                    send_user_registration_verification_email.delay(
                        resp.username, role_name
                    )

                    role_assignment_signal.send(
                        sender=self.__class__,
                        user=user,
                        role_name=role_name,
                    )

                return Response(
                    {"data": self.serializer_class(resp).data},
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED
            )

        except Exception as e:
            return process_error_response(e)


class CreateApp(CreateAPIView):
    serializer_class = serializers.UserFetchSerializer
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.AppCreationPayloadSerializer},
        responses={201: serializers.UserFetchSerializer},
    )
    # IP restricted endpoint
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)
            logger.info(f"Initiating app creation with details {request.data}")

            data = request.data.copy()
            app_credentials = create_client_id_and_secret(request.data["username"])
            data["user_type"] = UserType.APP
            #  client_app will be the default role for apps
            data["client_id"] = app_credentials["client_id"]
            data["client_secret"] = app_credentials["client_secret"]

            serializer = serializers.AppCreationSerializer(data=data)

            if serializer.is_valid():
                resp = serializer.save()
                app_data = self.serializer_class(resp).data
                logger.info(f"Successfully created app with details {app_data}")
                user = User.objects.get(id=app_data["id"])

                #  Don't do celery stuff in pytest mode -Git actions
                if os.environ.get("ENVIRONMENT", "") != "test":
                    send_app_registration_verification_email.delay(app_data["username"])

                    role_assignment_signal.send(
                        sender=self.__class__,
                        user=user,
                        role_name=request.data.get("role") or "client_app",
                    )
                return Response(
                    {
                        "message": "Kindly copy your client ID and Secret and save them securely",
                        "data": {
                            **app_data,
                            "client_id": app_credentials["client_id"],
                            "client_secret": app_credentials["client_secret_str"],
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"error": serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED
            )
        except Exception as e:
            return process_error_response(e)


class FilterUsers(GenericAPIView):
    """
    Filter users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    @extend_schema(tags=["Users"], parameters=[serializers.UserFilterSerializer])
    @has_expected_permissions(["view_user"])
    def get(self, request):
        return self.get_queryset()

    def get_serializer(self, *args, **kwargs):
        # Add check for Admins
        if self.request.user.is_authenticated:
            return serializers.FullUserFetchSerializer
        return serializers.UserFetchSerializer

    def get_queryset(
        self,
    ):
        """
        Return a list of users.
        """
        span = trace.get_current_span()
        add_request_data_to_span(span, self.request)

        filter_params = {}

        if self.request.GET.get("first_name"):
            filter_params["first_name__contains"] = self.request.GET.get("first_name")
        if self.request.GET.get("last_name"):
            filter_params["last_name__contains"] = self.request.GET.get("last_name")
        if self.request.GET.get("user_type"):
            filter_params["user_type"] = self.request.GET.get("user_type")
        if self.request.GET.get("username"):
            filter_params["username__contains"] = self.request.GET.get("username")
        if self.request.GET.get("email"):
            filter_params["email"] = self.request.GET.get("email")
        if self.request.GET.get("phone_number"):
            filter_params["phone_number__contains"] = self.request.GET.get(
                "phone_number"
            )
        if self.request.GET.get("parent_organization"):
            filter_params["parent_organization__contains"] = self.request.GET.get(
                "parent_organization"
            )
        if self.request.GET.get("created_at_start"):
            filter_params["created_at__gte"] = self.request.GET.get("created_at_start")
        if self.request.GET.get("created_at_end"):
            filter_params["created_at__lte"] = self.request.GET.get("created_at_end")
        if self.request.GET.get("updated_at_start"):
            filter_params["updated_at__gte"] = self.request.GET.get("updated_at_start")
        if self.request.GET.get("updated_at_end"):
            filter_params["updated_at__lte"] = self.request.GET.get("updated_at_end")
        if self.request.GET.get("is_active"):
            filter_params["is_active"] = self.request.GET.get("is_active")

        serializer = self.get_serializer()

        page = int(self.request.GET.get("page", "1"))
        items_per_page = int(self.request.GET.get("items_per_page", "10"))
        offset = (page - 1) * items_per_page

        queryset = User.objects.filter(**filter_params)[
            offset : (offset + items_per_page)
        ]

        return Response(
            {"data": serializer(queryset, many=True).data}, status=status.HTTP_200_OK
        )


class GUDUser(GenericAPIView):
    serializer_class = serializers.UserFetchSerializer

    @extend_schema(
        tags=["Users"],
        responses={201: serializers.UserFetchSerializer},
    )
    @has_expected_permissions(["view_user"])
    def get(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f'Getting user with ID {kwargs.get("id")}')
            user_data = User.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(user_data).data
            response["role"] = list(user_data.groups.values_list("name", flat=True))

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Users"],
        responses={204: {"message": "User succesfully deleted"}},
    )
    @has_expected_permissions(["delete_user"])
    def delete(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f'Deleting user with ID {kwargs.get("id")}')
            rep = User.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return Response(
                    {
                        "message": "User succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return process_error_response(e)

    @extend_schema(tags=["Users"], responses={200: serializers.UserFetchSerializer})
    @has_expected_permissions(["change_user"])
    def patch(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f'Updating user with ID {kwargs.get("id")}')
            user_to_update = User.objects.get(pk=kwargs.get("id"))

            update_serializer = serializers.UserUpdateSerializer(
                data=request.data, partial=True
            )
            if update_serializer.is_valid():
                update_serializer.update(user_to_update, request.data)
                return Response(
                    {
                        "data": self.serializer_class(user_to_update).data,
                        "message": "User succesfully updated",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": update_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return process_error_response(e)


class UserLogin(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    input_serializer_class = serializers.UserLoginSerializer

    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"], request={"application/json": serializers.UserLoginSerializer}
    )
    def post(self, request):
        try:
            req_serializer = self.input_serializer_class(data=request.data)
            if req_serializer.is_valid():
                user = User.objects.get(username=request.data.get("username"))
                if user.user_type == UserType.USER:
                    credentials_match = user.check_password(
                        request.data.get("password")
                    )
                elif user.user_type == UserType.APP:
                    credentials_match = user.verify_app_credentials(request.data)

                if credentials_match:
                    response = get_tokens_for_user(user, "token_login")
                    return Response(
                        response,
                        status=200,
                        headers={"X_AUTHENTICATED_USERNAME": user.username},
                    )

                logger.info(
                    f"Failed to authenticate user with username {user.username}"
                )
            else:
                return Response(
                    data={"error": req_serializer.errors},
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

            return Response(
                data={"error": "Invalid username or credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return process_error_response(e)


class AppLogin(UserLogin):
    authentication_classes = []
    permission_classes = []
    input_serializer_class = serializers.AppLoginSerializer

    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"], request={"application/json": serializers.AppLoginSerializer}
    )
    def post(self, request):
        try:
            return super().post(request)
        except Exception as e:
            return process_error_response(e)


class UpdateUserRoles(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.UserRoleUpdateSerializer},
    )
    @has_expected_permissions(["update_user_roles"])
    def put(self, request):
        try:
            user = User.objects.get(id=request.data["user_id"])
            group = Group.objects.get(name=request.data["role_name"])
            user.groups.add(group)

            return Response(
                {"message": f"User role(s) updated to {user.groups.get()}"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return process_error_response(e)


class VerifyUser(GenericAPIView):
    authentication_classes = []
    permission_classes = []

    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"],
    )
    def get(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            username = kwargs.get("username")
            logger.info(f"Verifying email for user {username}")
            token = kwargs.get("token")
            user = User.objects.get(username=username)
            verification_response = verify_user_token(token, user)
            if (
                verification_response["verified"]
                and verification_response["scope"] == "email_verification"
            ):
                user.is_active = True
                user.save()
                return HttpResponseRedirect("https://www.fuatilia.africa/")
            if (
                verification_response["verified"]
                and verification_response["scope"] == "user_credential_reset"
            ):
                user.is_active = False
                user.save()
                return HttpResponseRedirect("https://www.fuatilia.africa/")

        except Exception as e:
            return process_error_response(e)


class CredentialUpdate(GenericAPIView):
    authentication_classes = []
    permission_classes = []

    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"],
    )
    def get(self, request, **kwargs):
        span = trace.get_current_span()
        add_request_data_to_span(span, self.request)
        try:
            # For get requests the token will indicate what kind oc change is happening  ie.g reset,update,suspend e.t.c
            logger.info(
                f"Credential {kwargs["token"]} has been initiaed for {kwargs["username"]}"
            )

            # Epdate the email to be sent to match the "token"
            send_user_credential_reset_email.delay(kwargs["username"])
            return Response(
                {
                    "message": "Credential reset has been initiated. You should receive an email with further instructions."
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.UserCredentialUpdateSerializer},
    )
    def post(self, request, **kwargs):
        span = trace.get_current_span()
        add_request_data_to_span(span, self.request)

        try:
            token = kwargs.get("token")
            username = kwargs.get("username")
            user = User.objects.get(username=username)
            verification_response = verify_user_token(token, user)

            if (
                user.user_type == UserType.APP
                and verification_response["verified"]
                and verification_response["scope"] == "user_credential_reset"
            ):
                credential_response = create_client_id_and_secret(user.username)
                user.is_active = True
                user.client_id = credential_response["client_id"]
                user.client_secret = credential_response["client_secret"]
                user.save()
                return Response(
                    {
                        "message": "Kindly copy your client ID and Secret and save them securely",
                        "data": {
                            "client_id": credential_response["client_id"],
                            "client_secret": credential_response["client_secret_str"],
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            elif (
                user.user_type == UserType.USER
                and verification_response["verified"]
                and verification_response["scope"] == "user_credential_reset"
            ):
                user.is_active = True
                user.password = request.data["password"]
                user.save()
                return Response(
                    {"message": "Password Reset Successful"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as err:
            logger.error(err)
            return Response(
                {"error": err.__str__()}, status=status.HTTP_400_BAD_REQUEST
            )
