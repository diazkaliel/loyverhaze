from django.urls import path
from .views import MovementListCreateView, StockView

urlpatterns = [
    path("inventory/stock/", StockView.as_view()),
    path("inventory/movements/", MovementListCreateView.as_view()),
]
