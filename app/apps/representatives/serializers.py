import logging
from apps.helpers.general import GenericFilterSerializer
from utils.file_utils.models import GenericFileUploadSerilizer
from apps.representatives.models import (
    PositionChoices,
    PositionClassChoices,
    Representative,
)
from rest_framework import serializers


logger = logging.getLogger("app_logger")


class FullFetchRepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Representative
        exclude = ("image_url",)


class UserFetchRepresentativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Representative
        exclude = (
            "last_updated_by",
            "pending_update_json",
            "image_url",
        )


class RepresentativeCreationSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    position = serializers.ChoiceField(choices=PositionChoices)
    position_class = serializers.ChoiceField(choices=PositionClassChoices)
    house = serializers.CharField()
    area_represented = serializers.CharField()
    image_url = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    current_parliamentary_roles = serializers.CharField(required=False)
    representation_summary = serializers.DictField(required=False)

    def create(self, validated_data):
        representative = Representative.objects.create(**validated_data)
        return representative


class RepresentativeUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    position = serializers.CharField(required=False)
    position_class = serializers.CharField(required=False)
    house = serializers.CharField(required=False)
    image_url = serializers.CharField(required=False)
    area_represented = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    current_parliamentary_roles = serializers.CharField(required=False)
    representation_summary = serializers.DictField(required=False)
    version = serializers.IntegerField()

    def update(self, representative_id, validated_data):
        version = validated_data.get("version") or validated_data[
            "pending_update_json"
        ].get("version")
        version_exists = Representative.objects.filter(id=representative_id).first()
        if version_exists.version >= version:
            raise Exception(
                f"Version {version} passed on update is invalid or not up to date"
            )

        updated = Representative.objects.update(id=representative_id, **validated_data)

        logger.info(
            f"Update response  -- {updated} --- representative {representative_id} now has  :: {updated}"
        )
        return Representative.objects.get(id=representative_id)


class RepresentativeFilterSerilizer(GenericFilterSerializer):
    full_name = serializers.CharField(required=False)
    position = serializers.CharField(required=False)
    position_class = serializers.CharField(required=False)
    house = serializers.CharField(required=False)
    area_represented = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    last_updated_by = serializers.CharField(required=False)
    current_parliamentary_roles = serializers.CharField(required=False)
    # representation_summary = serializers.CharField(required=False)


class RepresentativeFileUploadSerializer(GenericFileUploadSerilizer):
    id = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9",
        help_text="Id of the representative",
    )
