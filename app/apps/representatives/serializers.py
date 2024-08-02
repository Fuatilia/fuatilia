from apps.representatives.models import Representative
from rest_framework import serializers


class FullFetchRepresenatativeSerializer(serializers):
    class Meta:
        model = Representative
        fields = "__all__"


class UserFetchRepresenatativeSerializer(serializers):
    class Meta:
        model = Representative
        exclude = ("created_at", "updated_at", "updated_by", "pending_update_json")


class RepresentativeCreationSerializer(serializers):
    full_name = serializers.CharField()
    position = serializers.CharField()
    position_type = serializers.CharField()
    house = serializers.CharField()
    area_represented = serializers.CharField()
    image_url = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    representation_summary = serializers.JSONField(required=False)

    def create(self, validated_data):
        representative = Representative.objects.create(**validated_data)
        return representative


class RepresentativeUpdateSerializer(serializers):
    full_name = serializers.CharField(required=False)
    position = serializers.CharField(required=False)
    position_type = serializers.CharField(required=False)
    house = serializers.CharField(required=False)
    image_url = serializers.CharField(required=False)
    area_represented = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    updated_by = serializers.CharField(max_length=30)
    representation_summary = serializers.JSONField(required=False)
