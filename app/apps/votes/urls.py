from django.urls import path
from apps.votes import views

urlpatterns = [
    path("create", views.CreateVote().as_view()),
    path("filter", views.FilterVotes().as_view()),
    path("<str:id>", views.GetOrDeleteVote().as_view()),
]
