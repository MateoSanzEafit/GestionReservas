from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("reservar/<str:deporte>/", views.ReservaDeporteView.as_view(), name="reservar_deporte"),
    path("reservas/crear/", views.CrearReservaView.as_view(), name="crear_reserva"),
]
