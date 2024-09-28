from rest_framework import serializers

from apps.generics.general import GenericFilterSerilizer
from apps.users.models import User
from apps.props.models import FAQ, Config


class ConfigCreationSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()
    created_by = serializers.CharField()

    # def validate(self, data):
    #     if User.objects.get(id=data["created_by"]):
    #         return data

    def create(self, validated_data) -> Config:
        return Config.objects.create(**validated_data)


class ConfigUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    last_updated_by = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9"
    )

    def validate(self, data):
        if User.objects.get(id=data["last_updated_by"]):
            return data

    def update(self, config: Config, validated_data) -> None:
        Config.objects.filter(pk=config.id).update(**validated_data)
        config.refresh_from_db()


class ConfigFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = "__all__"


class FilterConfigsBody(GenericFilterSerilizer):
    name = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)


# =============== FAQS ====================


class FAQUpdateSerializer(serializers.Serializer):
    faq = serializers.CharField(required=False)
    answer = serializers.CharField(required=False)
    last_updated_by = serializers.CharField(
        default="6134fc82-0faa-4bed-b7a2-edbcf541a3c9"
    )

    def validate(self, data):
        if User.objects.get(id=data["last_updated_by"]):
            return data

    def update(self, faq: FAQ, validated_data) -> None:
        FAQ.objects.filter(pk=faq.id).update(**validated_data)
        faq.refresh_from_db()


class FAQCreationSerializer(serializers.Serializer):
    faq = serializers.CharField()
    answer = serializers.CharField()
    created_by = serializers.CharField()

    def validate(self, data):
        if User.objects.get(id=data["created_by"]):
            return data

    def create(self, validated_data) -> FAQ:
        return FAQ.objects.create(**validated_data)


class FAQFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class FilterFAQsBody(GenericFilterSerilizer):
    faq = serializers.CharField(required=False)
    answer = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
