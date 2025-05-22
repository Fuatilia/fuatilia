from django.urls import path
from apps.users import views

urlpatterns = [
    path("v1/create/user", views.CreateUser().as_view()),
    path("v1/create/app", views.CreateApp().as_view()),
    path("v1/filter", views.FilterUsers().as_view()),
    path("v1/<str:id>", views.GUDUser().as_view()),
    path("v1/login/user", views.UserLogin().as_view()),
    path("v1/login/app", views.AppLogin().as_view()),
    path("v1/update/role", views.UpdateUserRoles().as_view()),
    path("v1/verify/<str:username>/<str:token>", views.VerifyUser().as_view()),
    path(
        "v1/credential/update/<str:username>/<str:token>",
        views.CredentialUpdate().as_view(),
    ),
    path("v1/token/generate", views.GenerateToken().as_view()),
]
