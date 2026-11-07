from django.urls import path
from .views import CheckoutView, SaleListView

urlpatterns = [
    path("sales/checkout/", CheckoutView.as_view()),
    path("sales/", SaleListView.as_view()),
]
