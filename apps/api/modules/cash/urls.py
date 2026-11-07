from django.urls import path
from .views import MovementView, ShiftCloseView, ShiftView

urlpatterns = [
    path("cash/shifts/", ShiftView.as_view()),
    path("cash/shifts/<uuid:shift_id>/close/", ShiftCloseView.as_view()),
    path("cash/movements/", MovementView.as_view()),
]
