import logging
import os
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from apps.bills.models import Bill
from utils.file_utils.models import GenericFileUploadSerilizer
from utils.file_utils.generic_file_utils import file_upload, get_file_data
from utils.general import add_request_data_to_span
from utils.auth import CustomTokenAuthentication
from apps.votes.models import Vote
from apps.votes import serializers
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from opentelemetry import trace


tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateVote(CreateAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(tags=["Votes"], request=serializers.VoteCreationSerializer)
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            creation_serializer = serializers.VoteCreationSerializer(data=request.data)
            if creation_serializer.is_valid():
                votes_data = creation_serializer.save()
                data = self.serializer_class(votes_data).data

                logger.info(f" Created cote with detail : {data}")
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


class FilterVotes(GenericAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(tags=["Votes"], parameters=[serializers.VotesFilterSerializer])
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

            page = int(self.request.GET.get("page"))
            items_per_page = int(self.request.GET.get("items_per_page"))
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


class GetOrDeleteVote(GenericAPIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]
    # TODO , change serializer class for Admins
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(
        tags=["Votes"],
        responses={201: serializers.FullFetchVoteSerializer},
    )
    def get(self, request, **kwargs):
        try:
            logger.info(f"Getting vote with ID {kwargs.get("id")}")
            response_data = Vote.objects.get(pk=kwargs.get("id"))
            response = self.serializer_class(response_data).data

            return Response(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception(e)
            if e.__class__ == Vote.DoesNotExist:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Votes"],
        responses={204: {"message": "Vote succesfully deleted"}},
    )
    def delete(self, request, **kwargs):
        try:
            logger.info(f"Deleting vote with ID {kwargs.get("id")}")
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
            logger.exception(e)
            if e.__class__ == Vote.DoesNotExist:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UploadVoteFile(GenericAPIView):
    @extend_schema(tags=["Votes"], request=GenericFileUploadSerilizer)
    def post(self, request, **kwargs):
        """
        file_type : should be set to VOTE to upload vote JSON
        """
        try:
            vote = Vote.objects.get(pk=kwargs.get("id"))
            bill = Bill.objects.get(pk=vote.id)

            metadata = {
                "source": request.data.get("file_source") or "",
                "extension": request.data["file_extension"],
            }

            response = file_upload(
                os.environ.get("VOTES_DATA_BUCKET_NAME"),
                request.data["file_type"],
                request.data["file_name"],
                request.data["base64_encoding"],
                metadata=metadata,
                house=vote.house.lower(),
                folder=bill.title,
            )

            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            if e.__class__ in [Vote.DoesNotExist, Bill.DoesNotExist]:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetVoteFile(GenericAPIView):
    @extend_schema(tags=["Votes"], responses={200: "Vote file foud"})
    def get(self, request, **kwargs):
        try:
            response_data = Vote.objects.get(pk=kwargs.get("id"))
            file_data = get_file_data(os.environ.get(), response_data.file_url)

            return Response({"data": file_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
