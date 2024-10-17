import logging
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from utils.error_handler import process_error_response
from utils.auth import has_expected_permissions
from utils.generics import add_request_data_to_span
from django.contrib.auth.models import Group
from apps.roles import serializers
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from opentelemetry import trace
from django.contrib.auth.models import Permission


tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateCustomRole(CreateAPIView):
    serializer_class = serializers.FetchRoleSerializers

    @extend_schema(
        tags=["Roles"], request={"application/json": serializers.RoleCreationSerializer}
    )
    @has_expected_permissions(["add_group"])
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            creation_serializer = serializers.RoleCreationSerializer(data=request.data)
            if creation_serializer.is_valid():
                role_data = creation_serializer.save()
                data = self.serializer_class(role_data).data

                logger.info(f" Created role with detail : {data}")
                return Response({"data": data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {
                        "Error": creation_serializer.errors,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)


class UpdateRolePermissions(GenericAPIView):
    serializer_class = serializers.FetchRoleSerializers

    @extend_schema(
        tags=["Roles"], request={"application/json": serializers.RoleCreationSerializer}
    )
    @has_expected_permissions(["change_group"])
    def put(self, request):
        try:
            creation_serializer = serializers.RoleCreationSerializer(data=request.data)
            if creation_serializer.is_valid():
                validated_data = creation_serializer.validated_data
                permissions = Permission.objects.filter(
                    codename__in=validated_data["permissions"]
                )
                if len(permissions) < 1:
                    raise ValueError("Specified permission(s) not found")

                group = Group.objects.get(
                    name=validated_data["role_name"],
                )
                if validated_data["action"] == "add":
                    for permission in permissions:
                        group.permissions.add(permission)
                else:
                    for permission in permissions:
                        group.permissions.remove(permission)

                data = self.serializer_class(group).data

                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "Error": creation_serializer.errors,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)


class FilterRoles(GenericAPIView):
    serializer_class = serializers.FetchRoleSerializers

    @extend_schema(tags=["Roles"], parameters=[serializers.RoleFilterSerializer])
    @has_expected_permissions(["view_group"])
    def get(self, request):
        return self.get_queryset()

    def get_queryset(self):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            filter_params = {}

            logger.info(f"Filtering roles with {self.request.GET.dict()}")

            if self.request.GET.get("role_name"):
                filter_params["name__contains"] = self.request.GET.get("role_name")

            page = int(self.request.GET.get("page", "1"))
            items_per_page = int(self.request.GET.get("items_per_page", "10"))
            offset = (page - 1) * items_per_page

            queryset = Group.objects.filter(**filter_params)[
                offset : (offset + items_per_page)
            ]

            return Response(
                {
                    "data": self.serializer_class(queryset, many=True).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return process_error_response(e)


class GetOrDeleteRole(GenericAPIView):
    serializer_class = serializers.FetchRoleSerializers

    @extend_schema(
        tags=["Roles"],
        responses={201: serializers.RoleFilterSerializer},
    )
    @has_expected_permissions(["view_group"])
    def get(self, request, **kwargs):
        try:
            logger.info(f"Getting role with ID {kwargs.get('id')}")
            response_data = Group.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Roles"],
        responses={204: {"message": "Role succesfully deleted"}},
    )
    @has_expected_permissions(["add_group"])
    def delete(self, request, **kwargs):
        try:
            logger.info(f"Deleting role with ID {kwargs.get('id')}")
            rep = Group.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return Response(
                    {
                        "message": "Role succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return process_error_response(e)
