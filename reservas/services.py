# reservas/services.py
from .models import Reserva, Cancha, Usuario
from .domain.reserva_builder import ReservaBuilder
from .infra.notificador_factory import NotificadorFactory


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
        self.notificador.enviar_confirmacion(reserva)
        return reserva

    def cancelar(self, reserva_id):
        try:
            r = Reserva.objects.get(id=reserva_id)
            r.estado = "CANCELADA"
            r.save()
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


# ✅ Wrappers para NO romper tus tests actuales
def create_reservation(usuario_id, cancha_id, fecha, hora_inicio, hora_fin):
    return ReservaService().crear_reserva(usuario_id, cancha_id, fecha, hora_inicio, hora_fin)

def cancel_reservation(reserva_id):
    return ReservaService().cancelar(reserva_id)

def confirm_reservation(reserva_id):
    return ReservaService().confirmar(reserva_id)
