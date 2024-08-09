import logging
from rest_framework import serializers

from apps.representatives.models import Representative
from utils.enum_utils import HouseChoices
from apps.bills.models import Bill, BillStatus
from utils.file_utils.models import GenericFileUploadSerilizer

logger = logging.getLogger("app_logger")


class FullFetchBillSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"


class BillCreationSerializer(serializers.Serializer):
    title = serializers.CharField(default="Finance Bill 2024")
    status = serializers.ChoiceField(choices=BillStatus, default=BillStatus.IN_PROGRESS)
    sponsored_by = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9",
        help_text="The person that brough the damn bill before the house",
    )  # rep name/ID
    supported_by = serializers.CharField(default="6134fc82-0faa-4bed-b7a2-edbcf541a3c1")
    house = serializers.ChoiceField(
        choices=HouseChoices.choices, default=HouseChoices.NATIONAL
    )
    summary = serializers.CharField(required=False)
    summary_created_by = serializers.CharField(
        required=False,
        help_text='Id of user that created the summary ideally of "Expert" role',
    )  # Id of portal user)
    summary_upvoted_by = serializers.CharField(
        required=False,
        help_text='Comma seperated string of users that upvoted "Experts" ideally ',
    )
    summary_downvoted_by = serializers.CharField(required=False)
    final_date_voted = serializers.CharField(
        required=False,
        help_text="The final day the bill was either voted for ascent by president or otherwise",
    )
    topics_in_the_bill = serializers.CharField(
        required=True, help_text="E.g agriculture, local seeds, radioactive waste"
    )
    file_url = serializers.CharField(required=False)

    def create(self, validated_data):
        bill = Bill.objects.create(**validated_data)
        return bill

    def validate(self, data):
        try:
            Representative.objects.get(id=data.get("sponsored_by"))
        except Exception:
            raise serializers.ValidationError(
                f'Could not find representative with ID {data.get("sponsored_by")}'
            )

        if data.get("supported_by"):
            if data.get("supported_by") == data.get("sponsored_by"):
                raise serializers.ValidationError(
                    "Sponsoring representative and supporting representative cannot be the same"
                )

            try:
                Representative.objects.get(id=data.get("supported_by"))
            except Exception:
                raise serializers.ValidationError(
                    f'Could not find representative with ID {data.get("supported_by")}'
                )

        return data


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
    created_at_start = serializers.DateTimeField(
        required=False, help_text="Start of date range filter for creation date"
    )
    created_at_end = serializers.DateTimeField(
        required=False, help_text="End of date range filter for creation date"
    )
    updated_at_start = serializers.DateTimeField(
        required=False, help_text="End of date range filter for update date"
    )
    updated_at_end = serializers.DateTimeField(
        required=False, help_text="End of date range filter for update date"
    )
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)


class BillFileUploadSerializer(GenericFileUploadSerilizer):
    id = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9",
        help_text="Id of the bill",
    )
