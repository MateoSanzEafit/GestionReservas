import os
import uuid
import requests
from reservas.models import Notificacion


class NotificadorMock:
    def enviar_confirmacion(self, reserva):
        print(f"[MOCK] Confirmación enviada para reserva {reserva.id}")
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=f"Tu reserva {reserva.id} para la cancha {reserva.cancha.ubicacion} ha sido creada (Pendiente de pago).",
            estado="ENVIADO",
        )

    def enviar_cancelacion(self, reserva):
        print(f"[MOCK] Cancelación enviada para reserva {reserva.id}")
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=f"Tu reserva {reserva.id} ha sido cancelada.",
            estado="ENVIADO",
        )

    def enviar_notificacion_pago(self, reserva, resultado_pago):
        print(f"[MOCK] Notificación de pago ({resultado_pago}) enviada para reserva {reserva.id}")
        mensaje = f"Tu pago para la reserva {reserva.id} fue aprobado. Tu reserva está CONFIRMADA." if resultado_pago == "APROBADO" else f"Tu pago para la reserva {reserva.id} fue rechazado."
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=mensaje,
            estado="ENVIADO",
        )


class NotificadorReal:
    def _enviar_microservicio(self, reserva, mensaje):
        microservice_url = os.getenv("MICROSERVICE_NOTIF_URL")
        if microservice_url:
            try:
                payload = {
                    "usuario_id": reserva.usuario.id,
                    "mensaje": mensaje,
                    "reserva_id": reserva.id
                }
                response = requests.post(microservice_url, json=payload, timeout=5)
                if response.status_code == 201:
                    print(f"[STRANGLER] Notificación delegada al microservicio con éxito.")
                    return True
            except Exception as e:
                print(f"[STRANGLER ERROR] Falló la comunicación con el microservicio: {e}")
        return False

    def enviar_confirmacion(self, reserva):
        mensaje = f"Tu reserva {reserva.id} para la cancha {reserva.cancha.ubicacion} ha sido creada (vía Flask)."
        self._enviar_microservicio(reserva, mensaje)
            
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=f"Tu reserva {reserva.id} para la cancha {reserva.cancha.ubicacion} ha sido creada (Pendiente de pago).",
            estado="ENVIADO",
        )

    def enviar_cancelacion(self, reserva):
        mensaje = f"Tu reserva {reserva.id} ha sido cancelada (vía Flask)."
        self._enviar_microservicio(reserva, mensaje)
        
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=f"Tu reserva {reserva.id} ha sido cancelada.",
            estado="ENVIADO",
        )

    def enviar_notificacion_pago(self, reserva, resultado_pago):
        mensaje = f"Pago de reserva {reserva.id} {resultado_pago} (vía Flask)."
        self._enviar_microservicio(reserva, mensaje)
        
        texto = f"Tu pago para la reserva {reserva.id} fue aprobado. Tu reserva está CONFIRMADA." if resultado_pago == "APROBADO" else f"Tu pago para la reserva {reserva.id} fue rechazado."
        Notificacion.objects.create(
            id=str(uuid.uuid4()),
            usuario=reserva.usuario,
            reserva=reserva,
            tipo="EMAIL",
            mensaje=texto,
            estado="ENVIADO",
        )


class NotificadorFactory:
    @staticmethod
    def crear():
        env_type = os.getenv("ENV_TYPE", "DEV").upper()
        # Retornamos NotificadorReal si queremos probar comunicación o DEV para mock, ambos guardan en DB
        return NotificadorReal() if env_type in ["PROD", "STAGING"] else NotificadorMock()
