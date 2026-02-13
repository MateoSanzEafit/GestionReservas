from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reservas/crear/", views.CrearReservaView.as_view(), name="crear_reserva"),
]
