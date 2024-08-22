from django.urls import path
from apps.bills import views

urlpatterns = [
    path("v1/create", views.CreateBill().as_view()),
    path("v1/filter", views.FilterBills().as_view()),
    path("v1/<str:id>", views.GetOrDeleteBill().as_view()),
    path("v1/upload/file", views.AddBillFile().as_view()),
    path("v1/<str:id>/file", views.GetBillFile().as_view()),
]
