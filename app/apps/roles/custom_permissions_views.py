import logging
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from utils.general import add_request_data_to_span
from apps.roles import serializers
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from opentelemetry import trace
from django.contrib.auth.models import Permission

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateCustomPermission(CreateAPIView):
    serializer_class = serializers.FetchPermissionsSerializers

    @extend_schema(
        tags=["Roles"],
        request={"application/json": serializers.PermissionCreationSerializer},
    )
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            creation_serializer = serializers.PermissionCreationSerializer(
                data=request.data
            )
            if creation_serializer.is_valid():
                permission_data = creation_serializer.save()
                data = self.serializer_class(permission_data).data

                logger.info(f" Created permission with detail : {data}")
                return Response({"data": data}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {
                        "Error": creation_serializer.errors,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": e.__repr__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilterPermissions(GenericAPIView):
    serializer_class = serializers.FetchPermissionsSerializers

    @extend_schema(tags=["Roles"], parameters=[serializers.PermissionFilterSerializer])
    def get(self, request):
        return self.get_queryset()

    def get_queryset(self):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            filter_params = {}

            logger.info(f"Filtering permissions with {self.request.GET.dict()}")

            if self.request.GET.get("permission_name"):
                filter_params["codename__contains"] = self.request.GET.get("rule")
            if self.request.GET.get("definition"):
                filter_params["name__contains"] = self.request.GET.get("definition")
            if self.request.GET.get("created_at_start"):
                filter_params["created_at__gte"] = self.request.GET.get(
                    "created_at_start"
                )
            if self.request.GET.get("created_at_end"):
                filter_params["created_at__lte"] = self.request.GET.get(
                    "created_at_end"
                )
            if self.request.GET.get("updated_at_start"):
                filter_params["updated_at__gte"] = self.request.GET.get(
                    "updated_at_start"
                )
            if self.request.GET.get("updated_at_end"):
                filter_params["updated_at__lte"] = self.request.GET.get(
                    "updated_at_end"
                )

            page = int(self.request.GET.get("page", "1"))
            items_per_page = int(self.request.GET.get("items_per_page", "10"))
            offset = (page - 1) * items_per_page

            queryset = Permission.objects.filter(**filter_params)[
                offset : (offset + items_per_page)
            ]

            return Response(
                {
                    "data": self.serializer_class(queryset, many=True).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetOrDeletePermissions(GenericAPIView):
    serializer_class = serializers.FetchPermissionsSerializers

    @extend_schema(
        tags=["Roles"],
        responses={201: serializers.FetchPermissionsSerializers},
    )
    def get(self, request, **kwargs):
        try:
            logger.info(f"Getting permission with ID {kwargs.get("id")}")
            response_data = Permission.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception(e)
            if e.__class__ == Permission.DoesNotExist:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Roles"],
        responses={204: {"message": "Permission succesfully deleted"}},
    )
    def delete(self, request, **kwargs):
        try:
            logger.info(f"Deleting permission with ID {kwargs.get("id")}")
            rep = Permission.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return Response(
                    {
                        "message": "Permission succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            logger.exception(e)
            if e.__class__ == Permission.DoesNotExist:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
