from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Usuario

@receiver(post_save, sender=User)
def sync_usuario_with_user(sender, instance, created, **kwargs):
    Usuario.objects.update_or_create(
        id=instance.username,
        defaults={
            'nombre': f"{instance.first_name} {instance.last_name}".strip() or instance.username,
            'correo_electronico': instance.email or f"{instance.username}@example.com",
            'rol': Usuario.Rol.ADMIN if instance.is_staff else Usuario.Rol.NORMAL,
            'estado': 'ACTIVO' if instance.is_active else 'INACTIVO'
        }
    )
