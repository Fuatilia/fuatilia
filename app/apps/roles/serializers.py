from rest_framework import serializers
from apps.users.models import User
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType


class FetchPermissionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("pk", "codename", "name")


class FetchRolesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class PermissionCreationSerializer(serializers.Serializer):
    permission_name = serializers.CharField(min_length=3)
    definition = serializers.CharField(max_length=100)

    def create(self, validated_data):
        # Avoided creating a proxy model, didn't see the need
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename=validated_data["permission_name"],
            name=validated_data["definition"],
            content_type=content_type,
        )
        return permission


class RoleCreationSerializer(serializers.Serializer):
    role_name = serializers.CharField(min_length=3)
    action = serializers.CharField(
        default="add", help_text="Option are <add> or <remove>"
    )
    permissions = serializers.ListField()

    def create(self, validated_data):
        permissions = Permission.objects.filter(
            codename__in=validated_data["permissions"]
        )
        if len(permissions) < 1:
            raise serializers.ValidationError("Specified permission(s) not found")

        group = Group.objects.create(
            name=validated_data["role_name"],
        )
        for permission in permissions:
            group.permissions.add(permission)

        return group


class FilterSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)


class PermissionFilterSerializer(FilterSerializer):
    permission_name = serializers.CharField(required=False)
    definition = serializers.CharField(required=False)


class RoleFilterSerializer(FilterSerializer):
    role_name = serializers.CharField(required=False)
