from django.contrib import admin
from .models import Usuario, Cancha, Reserva, Pago, Notificacion

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo_electronico', 'estado')
    search_fields = ('nombre', 'correo_electronico')

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'ubicacion', 'tarifa_por_hora', 'estado_disponibilidad')
    list_filter = ('tipo', 'estado_disponibilidad')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'cancha', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__nombre', 'cancha__tipo')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'monto', 'estado', 'fecha_pago')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo', 'fecha_envio', 'estado')
