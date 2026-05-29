from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("reservar/<str:deporte>/", views.ReservaDeporteView.as_view(), name="reservar_deporte"),
    path("reservas/crear/", views.CrearReservaView.as_view(), name="crear_reserva"),
    
    # Dashboards
    path("dashboard/", views.UserDashboardView.as_view(), name="dashboard"),
    path("dashboard/cancelar/<str:reserva_id>/", views.CancelarReservaView.as_view(), name="cancelar_reserva"),
    path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    
    # Admin Operations
    path("admin-dashboard/pagos/procesar/<str:pago_id>/<str:accion>/", views.ProcesarPagoView.as_view(), name="procesar_pago"),
    path("admin-dashboard/canchas/crear/", views.CanchaCreateView.as_view(), name="crear_cancha"),
    path("admin-dashboard/canchas/eliminar/<str:cancha_id>/", views.CanchaDeleteView.as_view(), name="eliminar_cancha"),
    
    # API JSON
    path("api/disponibilidad/", views.DisponibilidadAPIView.as_view(), name="api_disponibilidad"),
]
