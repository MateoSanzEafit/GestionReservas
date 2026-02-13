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
        dummy_date = datetime.today().date()
        start_dt = datetime.combine(dummy_date, self._hora_inicio)
        end_dt = datetime.combine(dummy_date, self._hora_fin)
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        if duration_hours <= 0:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")
        return duration_hours

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
