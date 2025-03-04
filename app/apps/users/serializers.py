import datetime
from apps.helpers.general import GenericFilterSerializer
from apps.users.models import User, UserType
from rest_framework import serializers


class FullUserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "client_id", "client_secret")


class UserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "last_updated_by",
            "password",
            "client_id",
            "client_secret",
            "pending_update_json",
            "groups",
            "user_permissions",
        )


class UserCreationSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3, default="jane")
    last_name = serializers.CharField(min_length=3, default="doe")
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(required=False, default="254111111111")
    password = serializers.CharField(min_length=10, default="password1234")
    role = serializers.CharField(required=False, default="client_api")
    parent_organization = serializers.CharField(
        required=False,
        default="fuatilia",
        help_text="Organization the user belongs to e.g Kengen,LSK",
    )

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


# Serializer for update payload
class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3, required=False)
    last_name = serializers.CharField(min_length=3, required=False)
    email = serializers.CharField(min_length=3, required=False)
    username = serializers.CharField(min_length=3, required=False)
    phone_number = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    parent_organization = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)
    last_updated_by = serializers.CharField(max_length=30, required=True)

    def update(self, user: User, validated_data) -> None:
        User.objects.filter(pk=user.id).update(
            **{**validated_data, "updated_at": datetime.datetime.now()}
        )
        user.refresh_from_db()


# For Api Apps
class AppCreationPayloadSerializer(serializers.Serializer):
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(default="254111111111")
    parent_organization = serializers.CharField(required=False, default="fuatilia")
    user_type = serializers.CharField(default="APP")


class AppCreationSerializer(serializers.Serializer):
    email = serializers.CharField(min_length=3)
    username = serializers.CharField(min_length=3)
    phone_number = serializers.CharField()
    parent_organization = serializers.CharField()
    user_type = serializers.CharField()
    client_id = serializers.CharField(min_length=20)
    client_secret = serializers.CharField()

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class UserFilterSerializer(GenericFilterSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    user_type = serializers.ChoiceField(required=False, choices=UserType)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    parent_organization = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class AppLoginSerializer(serializers.Serializer):
    username = serializers.CharField(default="app username")
    client_id = serializers.CharField(default="jak2**********cocn")
    client_secret = serializers.CharField(default="MjG**********woHl")
    grant_type = serializers.CharField(default="client_credentials")


class UserRoleUpdateSerializer(serializers.Serializer):
    user_id = serializers.CharField(default="user")
    role_name = serializers.CharField(default="dev")
