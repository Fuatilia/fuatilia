import os
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from apps.bills.models import Bill
from utils.enum_utils import FileTypeEnum
from utils.file_utils.generic_file_utils import file_upload
from apps.bills import serializers
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger("app_logger")


class CreateBill(CreateAPIView):
    serializer_class = serializers.BillCreationSerializer

    @extend_schema(tags=["Bills"], request=serializers.BillCreationSerializer)
    def post(self, request):
        try:
            logger.info(f"Initiating bill creation for {request.data}")
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                resp = serializer.save().__dict__
                del resp["_state"]
                return JsonResponse({"data": resp}, status=status.HTTP_201_CREATED)
            else:
                logger.error(serializer.errors)
                return JsonResponse(
                    {
                        "error": serializer.errors,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"error": e.__repr__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilterBills(GenericAPIView):
    serializer_class = serializers.FullFetchBillSerilizer

    @extend_schema(tags=["Bills"], parameters=[serializers.BillFilterSerializer])
    def get(self, request):
        return self.get_queryset()

    def get_queryset(self):
        filter_params = {}

        logger.info(f"Filtering Bills with {self.request.GET.dict()}")

        if self.request.GET.get("title"):
            filter_params["title__contains"] = self.request.GET.get("title")
        if self.request.GET.get("status"):
            filter_params["status"] = self.request.GET.get("status")
        if self.request.GET.get("sponsored_by"):
            filter_params["sponsored_by"] = self.request.GET.get("sponsored_by")
        if self.request.GET.get("house"):
            filter_params["house"] = self.request.GET.get("house")
        if self.request.GET.get("supported_by"):
            filter_params["supported_by"] = self.request.GET.get("supported_by")
        if self.request.GET.get("summary"):
            filter_params["summary__contains"] = self.request.GET.get("summary")
        if self.request.GET.get("summary_created_by"):
            filter_params["summary_created_by"] = self.request.GET.get(
                "summary_created_by"
            )
        if self.request.GET.get("summary_upvoted_by"):
            filter_params["summary_upvoted_by"] = self.request.GET.get(
                "summary_upvoted_by"
            )
        if self.request.GET.get("summary_downvoted_by"):
            filter_params["summary_downvoted_by"] = self.request.GET.get(
                "summary_downvoted_by"
            )
        if self.request.GET.get("final_date_voted"):
            filter_params["final_date_voted"] = self.request.GET.get("final_date_voted")
        if self.request.GET.get("topics_in_the_bill"):
            filter_params["topics_in_the_bill__contains"] = self.request.GET.get(
                "topics_in_the_bill"
            )
        if self.request.GET.get("final_date_voted_start"):
            filter_params["final_date_voted__gte"] = self.request.GET.get(
                "final_date_voted_start"
            )
        if self.request.GET.get("final_date_voted_end"):
            filter_params["final_date_voted__lte"] = self.request.GET.get(
                "final_date_voted_end"
            )
        if self.request.GET.get("created_at_start"):
            filter_params["created_at__gte"] = self.request.GET.get("created_at_start")
        if self.request.GET.get("created_at_end"):
            filter_params["created_at__lte"] = self.request.GET.get("created_at_end")
        if self.request.GET.get("updated_at_start"):
            filter_params["updated_at__gte"] = self.request.GET.get("updated_at_start")
        if self.request.GET.get("updated_at_end"):
            filter_params["updated_at__lte"] = self.request.GET.get("updated_at_end")

        page = int(self.request.GET.get("page"))
        items_per_page = int(self.request.GET.get("items_per_page"))
        offset = (page - 1) * items_per_page

        queryset = Bill.objects.filter(**filter_params)[
            offset : (offset + items_per_page)
        ]

        return JsonResponse(
            {
                "data": self.serializer_class(queryset, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class GetOrDeleteBill(GenericAPIView):
    # TODO , change serializer class for Admins
    serializer_class = serializers.FullFetchBillSerilizer

    @extend_schema(
        tags=["Bills"],
        responses={201: serializers.FullFetchBillSerilizer},
    )
    def get(self, request, **kwargs):
        response_data = Bill.objects.get(pk=kwargs.get("id"))
        response = self.serializer_class(response_data).data

        return JsonResponse(
            {"data": response},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Bills"],
        responses={204: {"message": "Bill succesfully deleted"}},
    )
    def delete(self, request, **kwargs):
        try:
            rep = Bill.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return JsonResponse(
                    {
                        "message": "Bill succesfully deleted",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"error": e.__str__()},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddBillFile(CreateAPIView):
    # Removes --> should either include a `serializer_class` attribute, or override the `get_serializer_class()` method.
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(tags=["Bills"], request=serializers.BillFileUploadSerializer)
    def post(self, request):
        try:
            response_data = Bill.objects.get(pk=request.data["id"])
            if response_data.id:
                bills_data_bucket_name = os.environ.get("BILLS_DATA_BUCKET_NAME")
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
                    bills_data_bucket_name,
                    FileTypeEnum[request.data.get("file_type")],
                    "bills",
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
                    file_url = f"s3://{bills_data_bucket_name}/bills/{response_data.house}/{folder_name}/{file_name}"
                    response_data.file_url = file_url
                    response_data.save()
                    response = {
                        "file_url": file_url,
                    }

                    final_status = status.HTTP_200_OK
                else:
                    final_status = status.HTTP_500_INTERNAL_SERVER_ERROR

            return JsonResponse({"data": response}, status=final_status)

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {
                    "error": e.__dict__ or e.__str__(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
