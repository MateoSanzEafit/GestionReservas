import os
import uuid
import requests
from reservas.models import Notificacion


class NotificadorMock:
    def enviar_confirmacion(self, reserva):
        print(f"[MOCK] Confirmación enviada para reserva {reserva.id}")


class NotificadorReal:
    def enviar_confirmacion(self, reserva):
        # STRANGLER PATTERN: Intentar usar el microservicio si está configurado
        microservice_url = os.getenv("MICROSERVICE_NOTIF_URL")
        
        if microservice_url:
            try:
                payload = {
                    "usuario_id": reserva.usuario.id,
                    "mensaje": f"Tu reserva {reserva.id} fue creada con éxito (vía Flask).",
                    "reserva_id": reserva.id
                }
                response = requests.post(microservice_url, json=payload, timeout=5)
                if response.status_code == 201:
                    print(f"[STRANGLER] Notificación delegada al microservicio con éxito.")
                    return
            except Exception as e:
                print(f"[STRANGLER ERROR] Falló la comunicación con el microservicio: {e}")
                # Fallback al comportamiento del monolito si falla el microservicio (resiliencia)

        # Comportamiento original del monolito: guardamos el historial en la BD
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
        # En el taller, forzamos NotificadorReal si queremos probar el patrón
        return NotificadorReal() if env_type in ["PROD", "STAGING"] else NotificadorMock()
