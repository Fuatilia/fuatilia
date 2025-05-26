from django.urls import path
from apps.votes import views

urlpatterns = [
    path("portal/v1/create", views.CreateVote().as_view()),
    path("portal/v1/filter", views.FilterVotes().as_view()),
    path("portal/v1/<str:id>", views.GUDVote().as_view()),
    path("portal/v1/<str:bill_id>/file", views.UploadVoteFile().as_view()),
    path(
        "portal/v1/<str:bill_id>/file/data/<str:file_name>",
        views.GetVoteFileData().as_view(),
    ),
    path(
        "portal/v1/<str:bill_id>/file/download/<str:file_name>",
        views.DownloadVoteFile().as_view(),
    ),
    path(
        "portal/v1/<str:bill_id>/file/stream/<str:file_name>",
        views.StreamVoteFile().as_view(),
    ),
    path("portal/v1/summary/aggregate", views.VoteSummaries().as_view()),
    # API Clients
    path("api/v1/filter", views.ApiFilterVotes().as_view()),
    path(
        "api/v1/<str:bill_id>/file/data/<str:file_name>",
        views.ApiGetVoteFileData().as_view(),
    ),
    path(
        "api/v1/<str:bill_id>/file/download/<str:file_name>",
        views.ApiDownloadVoteFile().as_view(),
    ),
    path(
        "api/v1/<str:bill_id>/file/stream/<str:file_name>",
        views.ApiStreamVoteFile().as_view(),
    ),
]
