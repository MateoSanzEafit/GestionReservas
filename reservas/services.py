# reservas/services.py
import os
from django.db import transaction
from django.db.models import Q
from .models import Reserva, Cancha, Usuario, Pago
from .domain.reserva_builder import ReservaBuilder
from .infra.notificador_factory import NotificadorFactory
from .tasks import enviar_confirmacion_reserva_async
import uuid


class ReservaService:
    def __init__(self, notificador=None):
        self.notificador = notificador or NotificadorFactory.crear()

    def crear_reserva(self, usuario_id, cancha_id, fecha, hora_inicio, hora_fin):
        usuario = Usuario.objects.get(id=usuario_id)
        cancha = Cancha.objects.get(id=cancha_id)

        reserva = (
            ReservaBuilder()
            .para_usuario(usuario)
            .para_cancha(cancha)
            .en_fecha(fecha)
            .desde(hora_inicio)
            .hasta(hora_fin)
            .build()
        )

        reserva.save()
        
        # 1. Crear automáticamente el objeto Pago asociado
        Pago.objects.get_or_create(
            reserva=reserva,
            defaults={
                'id': str(uuid.uuid4()),
                'metodo_pago': Pago.MetodoPago.EFECTIVO,
                'monto': reserva.costo_total,
                'estado': Pago.EstadoPago.PENDIENTE,
            }
        )

        # 2. Notificar creación sin bloquear la respuesta principal.
        transaction.on_commit(lambda: enviar_confirmacion_reserva_async.delay(reserva.id))
        return reserva

    def cancelar(self, reserva_id):
        try:
            r = Reserva.objects.get(id=reserva_id)
            r.estado = Reserva.Estado.CANCELADA
            r.save()
            
            # Cancelar pagos pendientes asociados
            for pago in r.pagos.filter(estado=Pago.EstadoPago.PENDIENTE):
                pago.estado = Pago.EstadoPago.RECHAZADO
                pago.save()
                
            self.notificador.enviar_cancelacion(r)
            return True
        except Reserva.DoesNotExist:
            return False

    def confirmar(self, reserva_id):
        try:
            r = Reserva.objects.get(id=reserva_id)
            r.estado = Reserva.Estado.CONFIRMADA
            r.save()
            return True
        except Reserva.DoesNotExist:
            return False

    def aprobar_pago(self, pago_id, metodo=None):
        try:
            pago = Pago.objects.get(id=pago_id)
            pago.estado = Pago.EstadoPago.PAGADO
            if metodo:
                pago.metodo_pago = metodo
            pago.save()
            
            reserva = pago.reserva
            reserva.estado = Reserva.Estado.CONFIRMADA
            reserva.save()
            
            self.notificador.enviar_notificacion_pago(reserva, "APROBADO")
            return True
        except Pago.DoesNotExist:
            return False

    def rechazar_pago(self, pago_id):
        try:
            pago = Pago.objects.get(id=pago_id)
            pago.estado = Pago.EstadoPago.RECHAZADO
            pago.save()
            
            reserva = pago.reserva
            reserva.estado = Reserva.Estado.RECHAZADA
            reserva.save()
            
            self.notificador.enviar_notificacion_pago(reserva, "RECHAZADO")
            return True
        except Pago.DoesNotExist:
            return False


# ✅ Wrappers para NO romper tus tests actuales
def create_reservation(usuario_id, cancha_id, fecha, hora_inicio, hora_fin):
    return ReservaService().crear_reserva(usuario_id, cancha_id, fecha, hora_inicio, hora_fin)

def cancel_reservation(reserva_id):
    return ReservaService().cancelar(reserva_id)

def confirm_reservation(reserva_id):
    return ReservaService().confirmar(reserva_id)

def check_availability(cancha, fecha, hora_inicio, hora_fin):
    overlapping = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA],
    ).filter(
        Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
    )
    return not overlapping.exists()

