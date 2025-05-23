import base64
import io
import json
import logging
import os
from django.http import FileResponse, StreamingHttpResponse
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from utils.error_handler import process_error_response
from utils.auth import has_expected_permissions
from utils.enum_utils import FileTypeEnum
from apps.bills.models import Bill
from utils.file_utils.models import GenericFileUploadSerilizer
from utils.file_utils.generic_file_utils import (
    file_upload_to_s3,
    get_s3_file_data,
    stream_s3_file_data,
)
from utils.generics import add_request_data_to_span
from apps.votes.models import Vote
from apps.votes import serializers
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from opentelemetry import trace

from django.db.models import Count


tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateVote(CreateAPIView):
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(
        tags=["Votes"], request={"application/json": serializers.VoteCreationSerializer}
    )
    @has_expected_permissions(["add_vote"])
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            creation_serializer = serializers.VoteCreationSerializer(data=request.data)
            if creation_serializer.is_valid():
                votes_data = creation_serializer.save()
                data = self.serializer_class(votes_data).data

                logger.info(f" Created vote with detail : {data}")
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


class FilterVotes(GenericAPIView):
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(tags=["Votes"], parameters=[serializers.VotesFilterSerializer])
    @has_expected_permissions(["view_vote"])
    def get(self, request):
        return self.get_queryset()

    def get_queryset(self):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            filter_params = {}

            logger.info(f"Filtering Votes with {self.request.GET.dict()}")

            if self.request.GET.get("bill_id"):
                filter_params["bill_id"] = self.request.GET.get("bill_id")
            if self.request.GET.get("representative_id"):
                filter_params["representative_id"] = self.request.GET.get(
                    "representative_id"
                )
            if self.request.GET.get("house"):
                filter_params["house"] = self.request.GET.get("house")
            if self.request.GET.get("vote_type"):
                filter_params["vote_type"] = self.request.GET.get("vote_type")
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

            queryset = Vote.objects.filter(**filter_params)[
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


class GUDVote(GenericAPIView):
    # TODO , change serializer class for Admins
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(
        tags=["Votes"],
        responses={201: serializers.FullFetchVoteSerializer},
    )
    @has_expected_permissions(["view_vote"])
    def get(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f"Getting vote with ID {kwargs.get('id')}")
            response_data = Vote.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Votes"],
        responses={204: {"message": "Vote succesfully deleted"}},
    )
    @has_expected_permissions(["delete_vote"])
    def delete(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f"Deleting vote with ID {kwargs.get('id')}")
            rep = Vote.objects.get(pk=kwargs.get("id"))
            if rep:
                rep.delete()
                return Response(
                    {
                        "message": "Vote succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Votes"], request={"application/json": serializers.VoteUpdateSerializer}
    )
    @has_expected_permissions(["change_vote"])
    def patch(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, self.request)

            logger.info(f'Updating vote with ID {kwargs.get("id")}')
            vote_to_update = Vote.objects.get(pk=kwargs.get("id"))

            update_serializer = serializers.VoteUpdateSerializer(
                data=request.data, partial=True
            )
            if update_serializer.is_valid():
                update_serializer.update(vote_to_update, request.data)
                return Response(
                    {
                        "data": self.serializer_class(vote_to_update).data,
                        "message": "Vote succesfully updated",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": update_serializer.errors,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )
        except Exception as e:
            return process_error_response(e)


class UploadVoteFile(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(
        tags=["Votes"], request={"application/json": GenericFileUploadSerilizer}
    )
    @has_expected_permissions(["add_votes_file"])
    def post(self, request, **kwargs):
        """
        Uploads votes files in json formart

        file_type : should be set to VOTE to upload vote JSON
        """
        try:
            bill = Bill.objects.get(pk=kwargs.get("bill_id"))

            metadata = {
                "source": request.data.get("file_source") or "",
                "extension": request.data["file_extension"],
                "string_encoding_fmt": request.data["string_encoding_fmt"],
            }

            logger.info(
                f"Initiating vote file upload --- > to S3 for {bill.title} --> {request.data['file_name']}"
            )

            response = file_upload_to_s3(
                os.environ.get("VOTES_DATA_BUCKET_NAME"),
                FileTypeEnum[request.data.get("file_type")],
                request.data["file_name"],
                request.data["base64_encoding"],
                metadata=metadata,
                house=bill.house.lower(),
                folder=bill.title,
            )

            if response.get("error"):
                return Response(
                    {"error": response["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return process_error_response(e)


class GetVoteFileData(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(tags=["Votes"], responses={200: "Vote file found"})
    @has_expected_permissions(["view_votes_file"])
    def get(self, request, **kwargs):
        """
        Gets vote file tied to a bill.
        The same bill will have different ID's in Senate and in National Assembly
        """
        try:
            bill_data = Bill.objects.get(pk=kwargs.get("bill_id"))
            file_url = f"votes/{bill_data.house.lower()}/{bill_data.title}/{kwargs.get('file_name')}"
            file_data = get_s3_file_data(
                os.environ.get("VOTES_DATA_BUCKET_NAME"), file_url
            )
            file_data = base64.b64decode(file_data).decode("utf-8")

            return Response({"data": json.loads(file_data)}, status=status.HTTP_200_OK)
        except Exception as e:
            return process_error_response(e)


class DownloadVoteFile(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(tags=["Votes"])
    @has_expected_permissions(["view_votes_file"])
    def get(self, request, **kwargs):
        """
        Allows browsers to download
        Uses get file functionality but with the download header dispositions for files
        Download vote file tied to a bill.
        """
        try:
            bill_data = Bill.objects.get(pk=kwargs.get("bill_id"))
            file_url = f"votes/{bill_data.house.lower()}/{bill_data.title}/{kwargs.get('file_name')}"
            file_data = get_s3_file_data(
                os.environ.get("VOTES_DATA_BUCKET_NAME"), file_url
            )
            file_data = base64.b64decode(file_data.decode("utf-8"))

            filename = f"{bill_data.title} - {kwargs.get('file_name')}"

            response = FileResponse(
                io.BytesIO(file_data),
                content_type="application/json",
                status=status.HTTP_200_OK,
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            return response
        except Exception as e:
            return process_error_response(e)


class StreamVoteFile(GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return

    @extend_schema(tags=["Votes"])
    @has_expected_permissions(["view_votes_file"])
    async def get(self, request, **kwargs):
        """
        Similar to download Votes file but allows for stream response
        Ideal for larger files
        """
        try:
            bill_data = Bill.objects.get(pk=kwargs.get("bill_id"))
            file_url = f"votes/{bill_data.house.lower()}/{bill_data.title}/{kwargs.get('file_name')}"
            file_data = await stream_s3_file_data(
                os.environ.get("VOTES_DATA_BUCKET_NAME"), file_url
            )
            file_data = base64.b64decode(file_data.read().decode("utf-8"))

            filename = f"{bill_data.title} - {kwargs.get('file_name')}"

            response = StreamingHttpResponse(
                io.BytesIO(file_data),
                content_type="application/x-ndjson,text/event-stream",
                status=status.HTTP_200_OK,
            )
            response["Content-Disposition"] = f'inline; filename="{filename}"'

            return response
        except Exception as e:
            return process_error_response(e)


class VoteSummaries(GenericAPIView):
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(tags=["Votes"], parameters=[serializers.VotesFilterSerializer])
    @has_expected_permissions(["view_vote_summary"])
    def get(self, *args, **kwargs):
        id_type = self.request.GET.get("id_type")
        id = self.request.GET.get("id")

        if id_type == "bill":
            # Aggregates all votes of a bill per house
            queryset = Vote.objects.filter(bill_id=id)
            q = queryset.values("house", "vote").annotate(bill_votes=Count("vote"))
        elif id_type == "rep":
            # Aggregates all votes a rep has done into a count of the vote values (yes/no/missing etc.)
            queryset = Vote.objects.filter(representative_id=id)
            q = queryset.values("house", "vote").annotate(bill_votes=Count("vote"))
        else:
            # Aggregates all votes of a house grouping them by bill id and vote value
            queryset = Vote.objects.filter(house=id)
            q = queryset.values("house", "bill_id", "vote").annotate(
                bill_votes=Count("vote")
            )

        return Response(data=q)
