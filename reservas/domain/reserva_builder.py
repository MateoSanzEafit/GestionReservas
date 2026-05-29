# reservas/domain/reserva_builder.py
from dataclasses import dataclass
from datetime import datetime
import uuid

from django.db.models import Q
from reservas.models import Reserva, Cancha, Usuario


@dataclass(frozen=True)
class ReservaData:
    usuario: Usuario
    cancha: Cancha
    fecha: object
    hora_inicio: object
    hora_fin: object


class ReservaBuilder:
    def __init__(self):
        self._usuario = None
        self._cancha = None
        self._fecha = None
        self._hora_inicio = None
        self._hora_fin = None

    # Fluent Interface
    def para_usuario(self, usuario: Usuario):
        self._usuario = usuario
        return self

    def para_cancha(self, cancha: Cancha):
        self._cancha = cancha
        return self

    def en_fecha(self, fecha):
        self._fecha = fecha
        return self

    def desde(self, hora_inicio):
        self._hora_inicio = hora_inicio
        return self

    def hasta(self, hora_fin):
        self._hora_fin = hora_fin
        return self

    def _validar_completo(self):
        if not all([self._usuario, self._cancha, self._fecha, self._hora_inicio, self._hora_fin]):
            raise ValueError("Datos incompletos para crear la reserva.")

    def _validar_horario(self):
        from datetime import time, datetime, date
        from django.utils import timezone

        # 1. Validar hora de inicio posterior a fin
        dummy_date = date.today()
        start_dt = datetime.combine(dummy_date, self._hora_inicio)
        end_dt = datetime.combine(dummy_date, self._hora_fin)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60

        if duration_minutes <= 0:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")

        # 2. Validar horario de operación (7:00 AM a 11:00 PM) y minutos 00 o 30
        op_start = time(7, 0)
        op_end = time(23, 0)

        if not (self._hora_inicio >= op_start and self._hora_fin <= op_end):
            raise ValueError("La reserva debe realizarse dentro del horario de atención (7:00 AM - 11:00 PM) y en intervalos de 30 minutos.")

        if self._hora_inicio.minute not in [0, 30] or self._hora_fin.minute not in [0, 30]:
            raise ValueError("La reserva debe realizarse dentro del horario de atención (7:00 AM - 11:00 PM) y en intervalos de 30 minutos.")

        # 3. Validar duración (mínimo 30 minutos, máximo 3 horas)
        if duration_minutes < 30:
            raise ValueError("La duración mínima de una reserva es de 30 minutos.")
        if duration_minutes > 180:
            raise ValueError("La duración máxima de una reserva es de 3 horas.")

        # 4. Reservas en fechas pasadas y tiempo transcurrido hoy
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()
        current_time = now_local.time()

        if self._fecha < today:
            raise ValueError("No se permiten reservas en fechas pasadas.")
        elif self._fecha == today and self._hora_inicio < current_time:
            raise ValueError("No se permiten reservas en horarios pasados del día de hoy.")

        return duration_minutes / 60.0

    def _validar_disponibilidad(self):
        overlapping = Reserva.objects.filter(
            cancha=self._cancha,
            fecha=self._fecha,
            estado__in=["PENDIENTE", "CONFIRMADA"],
        ).filter(
            Q(hora_inicio__lt=self._hora_fin) & Q(hora_fin__gt=self._hora_inicio)
        )
        if overlapping.exists():
            raise ValueError("La cancha no está disponible en el horario seleccionado.")

    def build(self) -> Reserva:
        self._validar_completo()
        duration_hours = self._validar_horario()
        self._validar_disponibilidad()

        costo_total = float(self._cancha.tarifa_por_hora) * duration_hours

        return Reserva(
            id=str(uuid.uuid4()),
            usuario=self._usuario,
            cancha=self._cancha,
            fecha=self._fecha,
            hora_inicio=self._hora_inicio,
            hora_fin=self._hora_fin,
            costo_total=costo_total,
            estado="PENDIENTE",
        )
