import logging
import os
from utils.enum_utils import FileTypeEnum
from utils.file_utils.generic_file_utils import file_upload
from apps.representatives.models import Representative
from apps.representatives import serializers
from rest_framework.generics import CreateAPIView, GenericAPIView
from drf_spectacular.utils import extend_schema
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger("app_logger")


class CreateRepresentative(CreateAPIView):
    serializer_class = serializers.RepresentativeCreationSerializer

    @extend_schema(
        tags=["Representatives"],
        request=serializers.RepresentativeCreationSerializer,
        responses={201: serializers.RepresentativeCreationSerializer},
    )
    def post(self, request):
        try:
            logger.info(f"Representative creation with details :: {request.data}")

            rep_serializer = serializers.RepresentativeCreationSerializer(
                data=request.data
            )
            if not rep_serializer.is_valid():
                return JsonResponse(rep_serializer.errors, status=400)

            rep_serializer.save()

            logger.info(
                f"==========================\n{rep_serializer.data}\n=========================="
            )

            response = self.serializer_class(rep_serializer).data

            return JsonResponse({"data": response})

        except Exception as e:
            logger.exception(e)
            return JsonResponse({"error": e.__repr__()}, status=500)


class FilterRepresenatatives(GenericAPIView):
    serializer_class = serializers.FullFetchRepresentativeSerializer

    @extend_schema(
        tags=["Representatives"], parameters=[serializers.RepresentativeFilterSerilizer]
    )
    def get(self, request):
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

        page = int(self.request.GET.get("page"))
        items_per_page = int(self.request.GET.get("items_per_page"))
        offset = (page - 1) * items_per_page

        queryset = Representative.objects.filter(**filter_params)[
            offset : (offset + items_per_page)
        ]

        return JsonResponse(
            {
                "status_code": status.HTTP_200_OK,
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
    def get(self, request, **kwargs):
        response_data = Representative.objects.get(pk=kwargs.get("id"))
        response = self.serializer_class(response_data).data

        return JsonResponse(
            {"status_code": status.HTTP_200_OK, "data": response},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Representatives"],
        responses={204: {"message": "Representative succesfully deleted"}},
    )
    def delete(self, request, **kwargs):
        try:
            rep = Representative.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return JsonResponse(
                    {
                        "status_code": status.HTTP_204_NO_CONTENT,
                        "message": "Representative succesfully deleted",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"status_code": status.HTTP_404_NOT_FOUND, "message": e.__str__()},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddRepresentativeFile(GenericAPIView):
    # Removes --> should either include a `serializer_class` attribute, or override the `get_serializer_class()` method.
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Representatives"], request=serializers.RepresentativeFileUploadSerializer
    )
    def post(self, request):
        try:
            response_data = Representative.objects.get(pk=request.data["id"])
            if response_data.id:
                reps_data_bucket_name = os.environ.get("REPS_DATA_BUCKET_NAME")
                file_name = request.data.get("file_name")

                logger.info(
                    f"Initiating file upload --- > to S3 for {response_data.full_name}"
                )
                metadata = {
                    "rep_id": str(response_data.id),
                    "creation_date": response_data.created_at.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "source": request.data.get("image_source") or "",
                    "version": request.data["version"],
                    "representative_name": response_data.full_name,
                    "content_type": request.data["file_extension"],
                }

                # # File path should allow for replacement of images
                response = file_upload(
                    reps_data_bucket_name,
                    FileTypeEnum[request.data.get("file_type")],
                    "representatives",
                    file_name,
                    request.data.get("base64_encoding"),
                    id=str(response_data.id),
                    metadata=metadata,
                )

                if (
                    response.get("ResponseMetadata")
                    and response["ResponseMetadata"]["HTTPStatusCode"] == 200
                ):
                    folder_name = request.data.get("file_type").lower() + "s"
                    image_url = f"s3://{reps_data_bucket_name}/representatives/{response_data.id}/{folder_name}/{file_name}"
                    response_data.image_url = image_url
                    response_data.save()
                    response = {
                        "image_url": image_url,
                    }

                    final_status = status.HTTP_200_OK
                else:
                    final_status = status.HTTP_500_INTERNAL_SERVER_ERROR

            return JsonResponse(
                {"status_code": final_status, "data": response}, status=final_status
            )

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "data": e.__dict__ or e.__str__(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
