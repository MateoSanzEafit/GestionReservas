from .models import Reserva, Cancha, Usuario
from django.db.models import Q
from datetime import datetime
import uuid

def check_availability(cancha, fecha, hora_inicio, hora_fin):
    """
    Check if a court is available for a given date and time range.
    Returns True if available, False otherwise.
    """
    overlapping_reservations = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA'] # Don't count cancelled reservations
    ).filter(
        Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
    )
    
    return not overlapping_reservations.exists()

def create_reservation(usuario_id, cancha_id, fecha, hora_inicio, hora_fin):
    """
    Creates a reservation if the court is available.
    Raises ValueError if inputs are invalid or court is not available.
    """
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        cancha = Cancha.objects.get(id=cancha_id)
    except (Usuario.DoesNotExist, Cancha.DoesNotExist):
        raise ValueError("Usuario o Cancha no encontrados.")

    if not check_availability(cancha, fecha, hora_inicio, hora_fin):
        raise ValueError("La cancha no está disponible en el horario seleccionado.")

    # Calculate cost (simple implementation)
    # Assuming duration is in hours, can be fractional
    # Convert time objects to datetime for subtraction
    dummy_date = datetime.today().date()
    start_dt = datetime.combine(dummy_date, hora_inicio)
    end_dt = datetime.combine(dummy_date, hora_fin)
    duration_hours = (end_dt - start_dt).total_seconds() / 3600
    
    if duration_hours <= 0:
         raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

    costo_total = float(cancha.tarifa_por_hora) * duration_hours

    reserva = Reserva.objects.create(
        id=str(uuid.uuid4()), # Generate a UUID for the ID since it is a CharField
        usuario=usuario,
        cancha=cancha,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        costo_total=costo_total,
        estado='PENDIENTE'
    )
    return reserva

def cancel_reservation(reserva_id):
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.estado = 'CANCELADA'
        reserva.save()
        return True
    except Reserva.DoesNotExist:
        return False

def confirm_reservation(reserva_id):
    try:
        reserva = Reserva.objects.get(id=reserva_id)
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        return True
    except Reserva.DoesNotExist:
        return False
