from django.urls import path
from apps.users import views

urlpatterns = [
    path("create/user", views.CreateUser().as_view()),
    path("create/app", views.CreateApp().as_view()),
    path("filter", views.ListUsers().as_view()),
    path("<str:id>", views.GetOrDeleteUser().as_view()),
    # path('/login', ),
]
