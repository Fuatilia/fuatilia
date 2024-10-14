import logging
from django.http import HttpResponseRedirect
from apps.users.tasks import send_user_registration_verification_email
from utils.error_handler import process_error_response
from utils.generics import add_request_data_to_span
from apps.users import serializers
from apps.users.models import User, UserType
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

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.UserCreationSerializer},
        responses={201: serializers.UserFetchSerializer},
    )
    @has_expected_permissions(["add_user"])
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

                send_user_registration_verification_email.delay(resp.username)

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

    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.AppCreationPayloadSerializer},
        responses={201: serializers.UserFetchSerializer},
    )
    @has_expected_permissions(["add_user"])
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)
            logger.info(f"Initiating app creation with details {request.data}")

            data = request.data.copy()
            app_credentials = create_client_id_and_secret(request.data["username"])
            data["user_type"] = UserType.APP
            data["client_id"] = app_credentials["client_id"]
            data["client_secret"] = app_credentials["client_secret"]
            serializer = serializers.AppCreationSerializer(data=data)

            if serializer.is_valid():
                resp = serializer.save()
                app_data = self.serializer_class(resp).data
                logger.info(f"Successfully created app with details {app_data}")
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
        if self.request.user.is_authenticated and self.request.user.role == "admin":
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


class GetOrDeleteUser(GenericAPIView):
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
            response_data = User.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

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


class UserLogin(GenericAPIView):
    authentication_classes = []
    permission_classes = []

    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Users"], request={"application/json": serializers.UserLoginSerializer}
    )
    def post(self, request):
        try:
            user = User.objects.get(username=request.data.get("username"))
            if user.user_type == UserType.USER:
                credentials_match = user.check_password(request.data.get("password"))
            elif user.user_type == UserType.APP:
                credentials_match = user.verify_app_credentials(request.data)

            if credentials_match:
                response = get_tokens_for_user(user)
                return Response(
                    response,
                    status=200,
                    headers={"X_AUTHENTICATED_USERNAME": user.username},
                )

            logger.info(f"Failed to authenticate user with username {user.username}")
            return Response(
                {"error": "Invalid username or credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return process_error_response(e)


class AppLogin(UserLogin):
    authentication_classes = []
    permission_classes = []

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
    @extend_schema(
        tags=["Users"],
        request={"application/json": serializers.UserRoleUpdateSerializer},
    )
    @has_expected_permissions(["update_user_roles"])
    def put(self, request):
        try:
            user = User.objects.get(id=request.data["user_id"])
            group = Group.objects.get(name=request.data["role"])
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
            if verify_user_token(token, user)["verified"]:
                user.is_active = True
                user.save()
                return HttpResponseRedirect("https://www.fuatilia.africa/")

        except Exception as e:
            return process_error_response(e)
