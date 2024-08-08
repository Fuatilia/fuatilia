from apps.users.models import User, UserRole, UserType
from rest_framework import serializers


class AdminUserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "client_secret")


class UserFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "client_secret", "pending_update_json", "role")


class UserCreationSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=3, default="jane")
    last_name = serializers.CharField(min_length=3, default="doe")
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(required=False, default="+254111111111")
    password = serializers.CharField(min_length=10, default="password1234")
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.STAFF)
    parent_organization = serializers.CharField(required=False, default="fuatilia")


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
class AppCreationSerializer(serializers.Serializer):
    email = serializers.CharField(min_length=3, default="janedoe@fuatilia.com")
    username = serializers.CharField(min_length=3, default="janedoe")
    phone_number = serializers.CharField(required=False, default="+254111111111")
    parent_organization = serializers.CharField(required=False, default="fuatilia")


class UserFilterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    user_type = serializers.ChoiceField(required=False, choices=UserType)
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    parent_organization = serializers.CharField(required=False)
    created_at_start = serializers.CharField(required=False)
    created_at_end = serializers.CharField(required=False)
    updated_at_start = serializers.CharField(required=False)
    updated_at_end = serializers.CharField(required=False)
    is_active = serializers.CharField(required=False)
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)
