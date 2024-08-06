from django.urls import path
from apps.representatives import views

urlpatterns = [
    path("create", views.CreateRepresentative().as_view()),
    path("filter", views.ListRepresentatives().as_view()),
    path("<str:id>", views.GetOrDeleteRepresentative().as_view()),
    path("upload/file", views.AddRepresentativeFile().as_view()),
]
