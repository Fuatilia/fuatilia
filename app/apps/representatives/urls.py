from django.urls import path
from apps.representatives import views

urlpatterns = [
    path("v1/create", views.CreateRepresentative().as_view()),
    path("v1/filter", views.FilterRepresentatives().as_view()),
    path("v1/<str:id>", views.GetOrDeleteRepresentative().as_view()),
    path("v1/upload/file", views.AddRepresentativeFile().as_view()),
    path("v1/<str:id>/<str:file_type>", views.GetRepresentativeFilesList().as_view()),
    path(
        "v1/file/<str:id>/<str:file_type>/<str:file_name>",
        views.GetRepresentativeFile().as_view(),
    ),
]
