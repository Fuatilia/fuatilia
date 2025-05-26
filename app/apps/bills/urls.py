from django.urls import path
from apps.bills import views

urlpatterns = [
    path("portal/v1/create", views.CreateBill().as_view()),
    path("portal/v1/filter", views.FilterBills().as_view()),
    path("portal/v1/<str:id>", views.GUDBill().as_view()),
    path("portal/v1/upload/file", views.AddBillFile().as_view()),
    path("portal/v1/<str:id>/file", views.GetBillFile().as_view()),
    # For API clients
    path("api/v1/filter", views.ApiFilterBills().as_view()),
    path("api/v1/<str:id>/file", views.ApiGetBillFile().as_view()),
]
