from rest_framework import serializers
from apps.votes.models import Vote, VoteTypeChoices
from utils.enum_utils import HouseChoices


class FullFetchVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"


class VoteCreationSerializer(serializers.Serializer):
    bill_id = serializers.CharField(default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9")
    representative_id = serializers.CharField(
        required=False, default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9"
    )
    vote_type = serializers.ChoiceField(
        choices=VoteTypeChoices.choices, default=VoteTypeChoices.INDIVIDUAL
    )
    vote_summary = serializers.JSONField(
        required=False,
        help_text="Only for use in the event of consensus(AYE/NO) type votes\n"
        + 'example :--> {"YES": 100, "NO": 20, "ABSENT": 30}',
    )
    house = serializers.ChoiceField(
        choices=HouseChoices.choices, default=HouseChoices.NATIONAL
    )
    vote = serializers.CharField(required=False)

    def create(self, validated_data):
        representative = Vote.objects.create(**validated_data)
        return representative

    def validate(self, data):
        if data.get("vote_type") == VoteTypeChoices.INDIVIDUAL:
            if data.get("vote_summary"):
                raise serializers.ValidationError(
                    f"Summary not compatible for  vote_type {VoteTypeChoices.INDIVIDUAL}"
                )
            if not data.get("representative_id"):
                raise serializers.ValidationError(
                    f"vote_type {VoteTypeChoices.INDIVIDUAL} requires expected string value at representative_id. Current value {data.get('representative_id')}"
                )
            if not data.get("vote"):
                raise serializers.ValidationError(
                    "<vote> is required for vote type INDIVIDUAL"
                )
        else:
            if not data.get("vote_summary"):
                raise serializers.ValidationError(
                    f"Expected value at vote_summary found {data.get('vote_summary')}"
                )

        return data


class VoteUpdateSerializer(serializers.Serializer):
    bill_id = serializers.CharField(default="NATIONAL")
    representative_id = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9"
    )
    vote_type = serializers.ChoiceField(
        required=False,
        choices=VoteTypeChoices.choices,
        default=VoteTypeChoices.INDIVIDUAL,
    )
    vote_summary = serializers.JSONField(
        required=False,
        help_text="Only for use in the event of consensus(AYE/NO) type votes",
    )
    house = serializers.CharField(required=False, default="NATIONAL")
    vote = serializers.CharField(required=False, default="YES")


class VotesFilterSerializer(serializers.Serializer):
    bill_id = serializers.CharField(required=False)
    representative_id = serializers.CharField(required=False)
    vote_type = serializers.ChoiceField(required=False, choices=VoteTypeChoices.choices)
    house = serializers.ChoiceField(required=False, choices=HouseChoices.choices)
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
