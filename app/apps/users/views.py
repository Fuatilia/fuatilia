import logging
from django.http import JsonResponse
from apps.users import serializers
from apps.users.models import User, UserRole
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status

logger = logging.getLogger("app_logger")


class CreateUser(CreateAPIView):
    serializer_class = serializers.UserFetchSerializer

    @extend_schema(
        tags=["Users"],
        request=serializers.UserCreationSerializer,
        responses={201: serializers.UserFetchSerializer},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            resp = serializer.save().__dict__
            del resp["_state"]
            return JsonResponse({"data": resp}, status=status.HTTP_200_OK)
        return JsonResponse(
            {"error": serializer.errors}, status=status.HTTP_417_EXPECTATION_FAILED
        )


class CreateApp(CreateAPIView):
    @extend_schema(
        tags=["Users"],
        request=serializers.AppCreationSerializer,
        responses={201: serializers.UserFetchSerializer},
    )
    def post(self, request):
        serializer = serializers.AppCreationSerializer(request)
        return serializer(request.data)


class FilterUsers(GenericAPIView):
    """
    Filter users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Users"], parameters=[serializers.UserFilterSerializer])
    def get(self, request):
        return self.get_queryset()

    def get_serializer(self):
        print(self.request.user)
        if (
            self.request.user.is_authenticated
            and self.request.user.role == UserRole.ADMIN
        ):
            return serializers.AdminUserFetchSerializer
        return serializers.UserFetchSerializer

    def get_queryset(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        user_type: str | None = None,
        username: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        parent_organization: str | None = None,
        created_at_start: str | None = None,
        created_at_end: str | None = None,
        updated_at_start: str | None = None,
        updated_at_end: str | None = None,
        is_active: bool | None = None,
    ):
        """
        Return a list of users.
        """
        filter_params = {}

        if first_name:
            filter_params["first_name"] = first_name
        if last_name:
            filter_params["last_name"] = last_name
        if user_type:
            filter_params["user_type"] = user_type
        if username:
            filter_params["username"] = username
        if email:
            filter_params["email"] = email
        if phone_number:
            filter_params["phone_number"] = phone_number
        if parent_organization:
            filter_params["parent_organization"] = parent_organization
        if created_at_start:
            filter_params["created_at__gte"] = created_at_start
        if created_at_end:
            filter_params["created_at__lte"] = created_at_end
        if updated_at_start:
            filter_params["updated_at__gte"] = updated_at_start
        if updated_at_end:
            filter_params["updated_at__lte"] = updated_at_end
        if is_active:
            filter_params["is_active"] = is_active

        serializer = self.get_serializer()

        queryset = User.objects.filter(**filter_params)
        return Response(serializer(queryset, many=True).data)


class GetOrDeleteUser(GenericAPIView):
    @extend_schema(
        tags=["Users"],
        responses={201: serializers.UserFetchSerializer},
    )
    def get(self, request, id):
        return User.objects.filter(user__pk=id)

    @extend_schema(
        tags=["Users"],
        responses={204: {"message": "User succesfully deleted"}},
    )
    def delete(self, request, id):
        return {"id to delete": id}
