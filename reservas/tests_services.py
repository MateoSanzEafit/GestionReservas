from django.test import TestCase
from .models import Usuario, Cancha, Reserva
from .services import create_reservation, check_availability, cancel_reservation
from datetime import date, time
import uuid

class ReservationServiceTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            id='user1',
            nombre='Juan Perez',
            correo_electronico='juan@example.com'
        )
        self.cancha = Cancha.objects.create(
            id='cancha1',
            tipo='Futbol',
            ubicacion='Norte',
            tarifa_por_hora=100.00
        )

    def test_availability_check(self):
        # Create a reservation
        Reserva.objects.create(
            id=str(uuid.uuid4()),
            usuario=self.usuario,
            cancha=self.cancha,
            fecha=date(2023, 10, 27),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            estado='CONFIRMADA'
        )

        # Check overlap
        is_available = check_availability(
            self.cancha,
            date(2023, 10, 27),
            time(10, 30),
            time(11, 30)
        )
        self.assertFalse(is_available)

        # Check no overlap
        is_available = check_availability(
            self.cancha,
            date(2023, 10, 27),
            time(11, 0),
            time(12, 0)
        )
        self.assertTrue(is_available)

    def test_create_reservation_success(self):
        reserva = create_reservation(
            'user1',
            'cancha1',
            date(2023, 10, 28),
            time(10, 0),
            time(12, 0)
        )
        self.assertEqual(reserva.estado, 'PENDIENTE')
        self.assertEqual(reserva.costo_total, 200.00)

    def test_create_reservation_overlap_fail(self):
        create_reservation(
            'user1',
            'cancha1',
            date(2023, 10, 28),
            time(10, 0),
            time(12, 0)
        )
        
        with self.assertRaises(ValueError):
            create_reservation(
            'user1',
            'cancha1',
            date(2023, 10, 28),
            time(11, 0),
            time(13, 0)
        )
