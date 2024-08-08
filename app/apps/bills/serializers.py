from rest_framework import serializers

from utils.enum_utils import HouseChoices
from apps.bills.models import BillStatus
from apps.votes.models import Vote
from utils.file_utils.models import GenericFileUploadSerilizer


class FullFetchBillSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"


class BillCreationSerializer(serializers.Serializer):
    title = serializers.CharField(default="Finance Bill 2024")
    status = serializers.ChoiceField(choices=BillStatus, default=BillStatus.IN_PROGRESS)
    sponsored_by = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9"
    )  # rep name/ID
    supported_by = serializers.CharField(default="6134fc82-0faa-4bed-b7a2-edbcf541a3c1")
    house = serializers.ChoiceField(
        choices=HouseChoices.choices, default=HouseChoices.NATIONAL
    )
    summary = serializers.CharField(required=False)
    summary_created_by = serializers.CharField(required=False)  # Id of portal user)
    summary_upvoted_by = serializers.CharField(required=False)
    summary_downvoted_by = serializers.CharField(required=False)
    final_date_voted = serializers.CharField(required=False)
    topics_in_the_bill = serializers.CharField(required=True)
    file_url = serializers.CharField(required=False)

    def create(self, validated_data):
        representative = Vote.objects.create(**validated_data)
        return representative


class BillFilterSerializer(serializers.Serializer):
    title = serializers.CharField(
        required=False,
    )
    status = serializers.CharField(required=False)
    sponsored_by = serializers.CharField(required=False)
    house = serializers.ChoiceField(required=False, choices=HouseChoices.choices)
    supported_by = serializers.CharField(required=False)
    summary = serializers.CharField(required=False)
    summary_created_by = serializers.CharField(required=False)  # Id of portal user)
    summary_upvoted_by = serializers.CharField(required=False)
    summary_downvoted_by = serializers.CharField(required=False)
    final_date_voted = serializers.CharField(required=False)
    topics_in_the_bill = serializers.CharField(required=False)
    final_date_voted_start = serializers.DateTimeField(required=False)
    final_date_voted_end = serializers.DateTimeField(required=False)
    created_at_start = serializers.DateTimeField(required=False)
    created_at_end = serializers.DateTimeField(required=False)
    updated_at_start = serializers.DateTimeField(required=False)
    updated_at_end = serializers.DateTimeField(required=False)
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)


class BillFileUploadSerializer(GenericFileUploadSerilizer):
    id = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9",
        help_text="Id of the bill",
    )
