from apps.users.models import User, UserRole, UserType
from rest_framework import serializers


class FullUserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "client_id", "client_secret")


class UserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "updated_by",
            "password",
            "client_id",
            "client_secret",
            "pending_update_json",
        )


class UserCreationSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3, default="jane")
    last_name = serializers.CharField(min_length=3, default="doe")
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(required=False, default="+254111111111")
    password = serializers.CharField(min_length=10, default="password1234")
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.STAFF)
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
    role = serializers.ChoiceField(required=False, choices=UserRole)
    parent_organization = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)
    updated_by = serializers.CharField(max_length=30)


# For Api Apps
class AppCreationPayloadSerializer(serializers.Serializer):
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(required=False, default="+254111111111")
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


class UserFilterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    user_type = serializers.ChoiceField(required=False, choices=UserType)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    parent_organization = serializers.CharField(required=False)
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
    is_active = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(default="user")
    password = serializers.CharField(default="password")


class AppLoginSerializer(serializers.Serializer):
    username = serializers.CharField(default="app username")
    client_id = serializers.CharField(default="jak2**********cocn")
    client_secret = serializers.CharField(default="MjG**********woHl")
    grant_type = serializers.CharField(default="password")
