from django.urls import path
from apps.roles.custom_permissions_views import (
    CreateCustomPermission,
    FilterPermissions,
    GetOrDeletePermissions,
)
from apps.roles.custom_roles_views import (
    CreateCustomRole,
    FilterRoles,
    GetOrDeleteRole,
    UpdateRolePermissions,
)

urlpatterns = [
    path("v1/create", CreateCustomRole().as_view()),
    path("v1/update-permissions", UpdateRolePermissions().as_view()),
    path("v1/filter", FilterRoles().as_view()),
    path("v1/<str:id>", GetOrDeleteRole().as_view()),
    path("v1/permission/create", CreateCustomPermission().as_view()),
    path("v1/permission/filter", FilterPermissions().as_view()),
    path("v1/permission/<str:id>", GetOrDeletePermissions().as_view()),
]
