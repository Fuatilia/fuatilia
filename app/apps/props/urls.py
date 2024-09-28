from django.urls import path
from apps.props import views

urlpatterns = [
    path("configs/v1/create", views.CreateOrUpdateConfig.as_view()),
    path("configs/v1/filter", views.FilterConfigs.as_view()),
    path("configs/v1/<str:id>", views.GUDConfig.as_view()),
    path("faqs/v1/create", views.CreateFAQ.as_view()),
    path("faqs/v1/filter", views.FilterFAQs.as_view()),
    path("faqs/v1/<str:id>", views.GUDFAQ.as_view()),
]
