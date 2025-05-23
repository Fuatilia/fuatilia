import logging
from rest_framework import serializers

from apps.helpers.general import GenericFilterSerializer
from apps.representatives.models import Representative
from utils.enum_utils import HouseChoices
from apps.bills.models import Bill, BillStatus
from utils.file_utils.models import GenericFileUploadSerilizer

logger = logging.getLogger("app_logger")


class FullFetchBillSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"


class UserFetchBillSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        exclude = ("file_url", "topics_in_the_bill")


class BillCreationSerializer(serializers.Serializer):
    title = serializers.CharField(default="Finance Bill 2024")
    status = serializers.ChoiceField(choices=BillStatus, default=BillStatus.IN_PROGRESS)
    sponsored_by = serializers.CharField(
        required=True,
        help_text="Id of the representative that brought the damn bill before the house",
    )  # rep name/ID
    supported_by = serializers.CharField(
        required=False,
        help_text="Id of the representative that brought the damn bill before the house",
    )
    house = serializers.ChoiceField(
        choices=HouseChoices.choices, default=HouseChoices.NATIONAL
    )
    bill_no = serializers.CharField(
        required=True
    )  # e.g "10 of 2024", Tracks bills in the year
    gazette_no = serializers.CharField(required=True)
    date_introduced = serializers.DateField(format="DD-MM-YYYY")
    summary = serializers.CharField(required=False)
    summary_created_by = serializers.CharField(
        required=False,
        help_text='Id of user that created the summary ideally of "Expert" role',
    )  # Id of portal user)
    # Summary upvotes will be done after bill creation

    final_date_voted = serializers.CharField(
        required=False,
        help_text="Third reading date",
    )
    topics_in_the_bill = serializers.CharField(
        required=False, help_text="E.g agriculture, local seeds, radioactive waste"
    )
    metadata = serializers.DictField(required=False)

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

        # You can have the same bill in seperate houses but not in the same
        #  Not using unique together for better response output
        bill = Bill.objects.filter(
            title=data.get("title"), house=data.get("house")
        ).first()
        if bill:
            raise serializers.ValidationError(
                f'Duplicate bill  < {data.get("title")} > for {data.get("house")} house'
            )

        return data


class BillFilterSerializer(GenericFilterSerializer):
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


class BillFileUploadSerializer(GenericFileUploadSerilizer):
    id = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9",
        help_text="Id of the bill",
    )


class BillUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(default="Finance Bill 2024", required=False)
    status = serializers.ChoiceField(
        choices=BillStatus, default=BillStatus.IN_PROGRESS, required=False
    )
    sponsored_by = serializers.CharField(
        required=False,
        help_text="Id of the representative that brought the damn bill before the house",
    )  # rep name/ID
    supported_by = serializers.CharField(
        required=False,
        help_text="Id of the representative that brought the damn bill before the house",
    )
    house = serializers.ChoiceField(
        choices=HouseChoices.choices, default=HouseChoices.NATIONAL, required=False
    )
    bill_no = serializers.CharField(
        required=False
    )  # e.g "10 of 2024", Tracks bills in the year
    gazette_no = serializers.CharField(required=False)
    date_introduced = serializers.DateField(format="DD-MM-YYYY", required=False)
    summary = serializers.CharField(required=False)
    summary_created_by = serializers.CharField(
        required=False,
        help_text='Id of user that created the summary ideally of "Expert" role',
    )  # Id of portal user)
    # Summary upvotes will be done after bill creation

    final_date_voted = serializers.CharField(
        required=False,
        help_text="Third reading date",
    )
    topics_in_the_bill = serializers.CharField(
        required=False, help_text="E.g agriculture, local seeds, radioactive waste"
    )
    metadata = serializers.DictField(required=False)
