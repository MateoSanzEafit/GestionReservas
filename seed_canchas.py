import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_canchas.settings')
django.setup()

from reservas.models import Cancha

def seed():
    canchas_data = [
        {'id': 'fut1', 'tipo': 'Fútbol', 'ubicacion': 'Cancha Sintética 1', 'tarifa_por_hora': 120.00},
        {'id': 'fut2', 'tipo': 'Fútbol', 'ubicacion': 'Cancha Sintética 2', 'tarifa_por_hora': 120.00},
        {'id': 'ten1', 'tipo': 'Tenis', 'ubicacion': 'Cancha Polvo de Ladrillo 1', 'tarifa_por_hora': 60.00},
        {'id': 'ten2', 'tipo': 'Tenis', 'ubicacion': 'Cancha Superficie Dura 1', 'tarifa_por_hora': 70.00},
        {'id': 'pad1', 'tipo': 'Pádel', 'ubicacion': 'Cancha Cristal 1', 'tarifa_por_hora': 90.00},
    ]

    for data in canchas_data:
        Cancha.objects.get_or_create(id=data['id'], defaults=data)
    
    print("Canchas creadas con éxito.")

if __name__ == '__main__':
    seed()
