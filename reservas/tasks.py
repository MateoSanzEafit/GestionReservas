from celery import shared_task

from .infra.notificador_factory import NotificadorFactory
from .models import Reserva


@shared_task(name='reservas.enviar_confirmacion_reserva_async')
def enviar_confirmacion_reserva_async(reserva_id):
    reserva = Reserva.objects.select_related('usuario', 'cancha').get(id=reserva_id)
    NotificadorFactory.crear().enviar_confirmacion(reserva)
    return {'reserva_id': reserva.id, 'status': 'notificacion_programada'}