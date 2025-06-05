from django.urls import path
from apps.representatives import views

urlpatterns = [
    path("portal/v1/create", views.CreateRepresentative().as_view()),
    path("portal/v1/filter", views.FilterRepresentatives.as_view()),
    path("portal/v1/<str:id>", views.GUDRepresentative().as_view()),
    path("portal/v1/approve/<str:id>", views.ApproveRepresentative().as_view()),
    path("portal/v1/upload/file", views.AddRepresentativeFile().as_view()),
    path(
        "portal/v1/<str:id>/file/<str:file_type>",
        views.GetRepresentativeFilesList().as_view(),
    ),
    path(
        "portal/v1/file/<str:id>/<str:file_type>/<str:file_name>",
        views.GetRepresentativeFile().as_view(),
    ),
    path(
        "portal/v1/display-image/<str:id>",
        views.GetRepresentativeDisplayImage().as_view(),
    ),
    # For Api Clients
    path("api/v1/filter", views.ApiFilterRepresentatives().as_view()),
    path(
        "api/v1/<str:id>/file/<str:file_type>",
        views.ApiGetRepresentativeFilesList().as_view(),
    ),
    path(
        "api/v1/file/<str:id>/<str:file_type>/<str:file_name>",
        views.ApiGetRepresentativeFile().as_view(),
    ),
]
