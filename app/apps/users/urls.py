from django.urls import path
from apps.users import views

urlpatterns = [
    path("portal/v1/create/user", views.CreateUser().as_view()),
    path("portal/v1/create/app", views.CreateApp().as_view()),
    path("portal/v1/filter", views.FilterUsers().as_view()),
    path("portal/v1/<str:id>", views.GUDUser().as_view()),
    path("portal/v1/login/user", views.UserLogin().as_view()),
    path("portal/v1/update/role", views.UpdateUserRoles().as_view()),
    path("portal/v1/verify/<str:username>/<str:token>", views.VerifyUser().as_view()),
    path(
        "portal/v1/credential/update/<str:username>/<str:token>",
        views.CredentialUpdate().as_view(),
    ),
    path("portal/v1/token/generate", views.GenerateToken().as_view()),
    # API Client endpoints
    path("api/v1/login/app", views.ApiAppLogin().as_view()),
]
