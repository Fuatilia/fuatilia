import base64
import logging
import os
from utils.error_handler import process_error_response
from utils.auth import has_expected_permissions
from utils.generics import add_request_data_to_span
from utils.enum_utils import FileTypeEnum
from utils.file_utils.generic_file_utils import file_upload_to_s3, get_s3_file_data
from apps.representatives.models import Representative
from apps.representatives import serializers
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status
from opentelemetry import trace


tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateRepresentative(CreateAPIView):
    serializer_class = serializers.UserFetchRepresentativeSerializer

    @extend_schema(
        tags=["Representatives"],
        request={"application/json": serializers.RepresentativeCreationSerializer},
        responses={201: serializer_class},
    )
    @has_expected_permissions(["add_representative"])
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(f"Representative creation with details :: {request.data}")

            rep_serializer = serializers.RepresentativeCreationSerializer(
                data=request.data
            )
            if not rep_serializer.is_valid():
                return Response(
                    rep_serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED
                )

            created_representative = rep_serializer.save()

            return Response(
                {"data": self.serializer_class(created_representative).data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return process_error_response(e)


class FilterRepresentatives(GenericAPIView):
    serializer_class = serializers.UserFetchRepresentativeSerializer

    @extend_schema(
        tags=["Representatives"], parameters=[serializers.RepresentativeFilterSerilizer]
    )
    @has_expected_permissions(["view_representative"])
    def get(self, request):
        span = trace.get_current_span()
        add_request_data_to_span(span, request)
        return self.get_queryset()

    def get_queryset(
        self,
    ):
        """
        Return a list of users.
        """

        filter_params = {}

        logger.info(f"Filtering Reps with {self.request.GET.dict()}")

        if self.request.GET.get("full_name"):
            filter_params["full_name__icontains"] = self.request.GET.get("full_name")
        if self.request.GET.get("position"):
            filter_params["position__icontains"] = self.request.GET.get("position")
        if self.request.GET.get("position_type"):
            filter_params["position_type__icontains"] = self.request.GET.get(
                "position_type"
            )
        if self.request.GET.get("house"):
            filter_params["house"] = self.request.GET.get("house")
        if self.request.GET.get("area_represented"):
            filter_params["area_represented__icontains"] = self.request.GET.get(
                "area_represented"
            )
        if self.request.GET.get("phone_number"):
            filter_params["phone_number__icontains"] = self.request.GET.get(
                "phone_number"
            )
        if self.request.GET.get("gender"):
            filter_params["gender"] = self.request.GET.get("gender")
        if self.request.GET.get("updated_by"):
            filter_params["updated_by__icontains"] = self.request.GET.get("updated_by")
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

        page = int(self.request.GET.get("page", "1"))
        items_per_page = int(self.request.GET.get("items_per_page", "10"))
        offset = (page - 1) * items_per_page

        queryset = Representative.objects.filter(**filter_params)[
            offset : (offset + items_per_page)
        ]

        return Response(
            {
                "data": self.serializer_class(queryset, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class GetOrDeleteRepresentative(GenericAPIView):
    # TODO , change serializer class for Admins
    serializer_class = serializers.FullFetchRepresentativeSerializer

    @extend_schema(
        tags=["Representatives"],
        responses={201: serializers.FullFetchRepresentativeSerializer},
    )
    @has_expected_permissions(["view_representative"])
    def get(self, request, **kwargs):
        try:
            logger.info(f"Getting represenatative with ID {kwargs.get('id')}")
            response_data = Representative.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Representatives"],
        responses={204: {"message": "Representative succesfully deleted"}},
    )
    @has_expected_permissions(["delete_representative"])
    def delete(self, request, **kwargs):
        try:
            logger.info(f"Deleting representative with ID {kwargs.get('id')}")
            rep = Representative.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return Response(
                    {
                        "message": "Representative succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )

        except Exception as e:
            return process_error_response(e)


class AddRepresentativeFile(GenericAPIView):
    # Removes --> should either include a `serializer_class` attribute, or override the `get_serializer_class()` method.
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Representatives"],
        request={"application/json": serializers.RepresentativeFileUploadSerializer},
    )
    @has_expected_permissions(["add_representative_file"])
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            response_data = Representative.objects.get(pk=request.data["id"])
            if response_data.id:
                reps_data_bucket_name = os.environ.get("REPS_DATA_BUCKET_NAME")
                file_name = request.data.get("file_name")

                logger.info(
                    f"Initiating representative file upload --- > to S3 for {response_data.full_name}"
                )
                metadata = {
                    "rep_id": str(response_data.id),
                    "creation_date": response_data.created_at.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "source": request.data.get("image_source") or "",
                    "representative_name": response_data.full_name,
                    "content_type": request.data["file_extension"],
                    "string_encoding_fmt": request.data["string_encoding_fmt"],
                }

                # # File path should allow for replacement of images
                response = file_upload_to_s3(
                    reps_data_bucket_name,
                    FileTypeEnum[request.data.get("file_type")],
                    file_name,
                    request.data.get("base64_encoding"),
                    id=str(response_data.id),
                    metadata=metadata,
                    folder="representatives",
                )

                if (
                    response.get("ResponseMetadata")
                    and response["ResponseMetadata"]["HTTPStatusCode"] == 200
                ):
                    response_data.image_url = response["file_url"]
                    response_data.save()
                    response = {
                        "message": "Image successfully uploaded",
                        "url": response["file_url"],
                    }

                    final_status = status.HTTP_200_OK
                else:
                    final_status = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response({"data": response}, status=final_status)

        except Exception as e:
            return process_error_response(e)


class GetRepresentativeFilesList(GenericAPIView):
    @extend_schema(
        tags=["Representatives"], responses={200: "Representative file found"}
    )
    @has_expected_permissions(["view_representative_file"])
    def get(self, request, **kwargs):
        try:
            response_data = Representative.objects.get(pk=kwargs.get("id"))
            if kwargs.get("file_type") == FileTypeEnum.IMAGE.lower():
                file_url = response_data.image_url

            file_data = get_s3_file_data(
                os.environ.get("REPS_DATA_BUCKET_NAME"), file_url
            )

            return Response({"data": file_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return process_error_response(e)


class GetRepresentativeFile(GenericAPIView):
    @extend_schema(
        tags=["Representatives"], responses={200: "Representative file found"}
    )
    @has_expected_permissions(["view_representative_file"])
    def get(self, request, **kwargs):
        try:
            if kwargs.get("file_type") and kwargs.get("file_name"):
                id = kwargs.get("id")
                file_url = f'representatives/{id}/{kwargs.get("file_type")}s/{kwargs.get("file_name")}'
                file_data = get_s3_file_data(
                    os.environ.get("REPS_DATA_BUCKET_NAME"), file_url
                )
                # Bytes Object
                file_data = base64.b64decode(file_data.encode("utf-8"))
                return Response({"data": file_data}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invalid argument for <file_type>"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return process_error_response(e)
