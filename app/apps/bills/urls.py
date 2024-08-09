from django.urls import path
from apps.bills import views

urlpatterns = [
    path("create", views.CreateBill().as_view()),
    path("filter", views.FilterBills().as_view()),
    path("<str:id>", views.GetOrDeleteBill().as_view()),
    path("upload/file", views.AddBillFile().as_view()),
]
