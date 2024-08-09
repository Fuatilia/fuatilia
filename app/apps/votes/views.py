from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
from apps.votes.models import Vote
from apps.votes import serializers
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger("app_logger")


class CreateVote(CreateAPIView):
    serializer_class = serializers.VoteCreationSerializer

    @extend_schema(tags=["Votes"], request=serializers.VoteCreationSerializer)
    def post(self, request):
        try:
            if self.serializer_class.is_valid(request.data):
                votes_data = self.serializer_class.create(request.data)
                return JsonResponse(
                    {"data": votes_data.__dict__}, status=status.HTTP_201_CREATED
                )
            else:
                return JsonResponse(
                    {
                        "data": votes_data.__dict__,
                    },
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"error": e.__repr__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilterVotes(GenericAPIView):
    serializer_class = serializers.FullFetchVoteSerializer

    @extend_schema(tags=["Votes"], parameters=[serializers.VotesFilterSerializer])
    def get(self, request):
        return self.get_queryset()

    def get_queryset(self):
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
            filter_params["created_at_start__gte"] = self.request.GET.get(
                "created_at_start"
            )
        if self.request.GET.get("created_at_end"):
            filter_params["created_at_end__lte"] = self.request.GET.get(
                "created_at_end"
            )
        if self.request.GET.get("updated_at_start"):
            filter_params["updated_at_start__gte"] = self.request.GET.get(
                "updated_at_start"
            )
        if self.request.GET.get("updated_at_end"):
            filter_params["updated_at_end__lte"] = self.request.GET.get(
                "updated_at_end"
            )

        page = int(self.request.GET.get("page"))
        items_per_page = int(self.request.GET.get("items_per_page"))
        offset = (page - 1) * items_per_page

        queryset = Vote.objects.filter(**filter_params)[
            offset : (offset + items_per_page)
        ]

        return JsonResponse(
            {
                "data": self.serializer_class(queryset, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class GetOrDeleteVote(GenericAPIView):
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

            return JsonResponse(
                {"data": response},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception(e)
            if e.__class__ == Vote.DoesNotExist:
                return JsonResponse(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return JsonResponse(
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
                return JsonResponse(
                    {
                        "message": "Vote succesfully deleted",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            logger.exception(e)
            if e.__class__ == Vote.DoesNotExist:
                return JsonResponse(
                    {"error": e.__str__()},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return JsonResponse(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
