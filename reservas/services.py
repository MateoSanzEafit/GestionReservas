# reservas/services.py
from django.db.models import Q
from .models import Reserva, Cancha, Usuario, Pago
from .domain.reserva_builder import ReservaBuilder
from .infra.notificador_factory import NotificadorFactory
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
        Pago.objects.create(
            id=str(uuid.uuid4()),
            reserva=reserva,
            metodo_pago="EFECTIVO",
            monto=reserva.costo_total,
            estado="PENDIENTE"
        )

        # 2. Notificar creación
        self.notificador.enviar_confirmacion(reserva)
        return reserva

    def cancelar(self, reserva_id):
        try:
            r = Reserva.objects.get(id=reserva_id)
            r.estado = "CANCELADA"
            r.save()
            
            # Cancelar pagos pendientes asociados
            for pago in r.pagos.filter(estado="PENDIENTE"):
                pago.estado = "RECHAZADO"
                pago.save()
                
            self.notificador.enviar_cancelacion(r)
            return True
        except Reserva.DoesNotExist:
            return False

    def confirmar(self, reserva_id):
        try:
            r = Reserva.objects.get(id=reserva_id)
            r.estado = "CONFIRMADA"
            r.save()
            return True
        except Reserva.DoesNotExist:
            return False

    def aprobar_pago(self, pago_id, metodo=None):
        try:
            pago = Pago.objects.get(id=pago_id)
            pago.estado = "PAGADO"
            if metodo:
                pago.metodo_pago = metodo
            pago.save()
            
            reserva = pago.reserva
            reserva.estado = "CONFIRMADA"
            reserva.save()
            
            self.notificador.enviar_notificacion_pago(reserva, "APROBADO")
            return True
        except Pago.DoesNotExist:
            return False

    def rechazar_pago(self, pago_id):
        try:
            pago = Pago.objects.get(id=pago_id)
            pago.estado = "RECHAZADO"
            pago.save()
            
            reserva = pago.reserva
            reserva.estado = "RECHAZADA"
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
        estado__in=["PENDIENTE", "CONFIRMADA"],
    ).filter(
        Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
    )
    return not overlapping.exists()

