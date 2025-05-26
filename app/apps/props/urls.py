from django.urls import path
from apps.props import views

urlpatterns = [
    # Health endpoint that is open to everyone
    path("api/health/v1", views.HealthCheker.as_view()),
    path("portal/configs/v1/create", views.CreateConfig.as_view()),
    path("portal/configs/v1/filter", views.FilterConfigs.as_view()),
    path("portal/configs/v1/<str:id>", views.GUDConfig.as_view()),
    path("portal/faqs/v1/create", views.CreateFAQ.as_view()),
    path("portal/faqs/v1/filter", views.FilterFAQs.as_view()),
    path("portal/faqs/v1/<str:id>", views.GUDFAQ.as_view()),
]
