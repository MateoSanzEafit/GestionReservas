# reservas/infra/notificador_factory.py
import os
import uuid
from reservas.models import Notificacion


class NotificadorMock:
    def enviar_confirmacion(self, reserva):
        print(f"[MOCK] Confirmación enviada para reserva {reserva.id}")


class NotificadorReal:
    def enviar_confirmacion(self, reserva):
        # Simulación "real": guardamos el historial en la BD
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=f"Tu reserva {reserva.id} fue creada con éxito.",
            estado="ENVIADO",
        )


class NotificadorFactory:
    @staticmethod
    def crear():
        env_type = os.getenv("ENV_TYPE", "DEV").upper()
        return NotificadorReal() if env_type == "PROD" else NotificadorMock()
