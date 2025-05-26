from django.urls import path
from apps.roles.custom_permissions_views import (
    CreateCustomPermission,
    FilterPermissions,
    GUDPermissions,
)
from apps.roles.custom_roles_views import (
    CreateCustomRole,
    FilterRoles,
    GUDRole,
)

urlpatterns = [
    path("portal/v1/create", CreateCustomRole().as_view()),
    path("portal/v1/filter", FilterRoles().as_view()),
    path("portal/v1/<str:id>", GUDRole().as_view()),
    path("portal/v1/permission/create", CreateCustomPermission().as_view()),
    path("portal/v1/permission/filter", FilterPermissions().as_view()),
    path("portal/v1/permission/<str:id>", GUDPermissions().as_view()),
]
