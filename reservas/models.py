from django.core.validators import MinValueValidator
from django.db import models

class Usuario(models.Model):
    class Rol(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        ADMIN = 'ADMIN', 'Administrador'

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'

    id = models.CharField(max_length=50, primary_key=True)  # Using CharField as per diagram, typically AutoField/UUID
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True) # Added unique constraint for email
    fecha_registro = models.DateField(auto_now_add=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.NORMAL)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre

class Cancha(models.Model):
    class EstadoDisponibilidad(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OCUPADA = 'OCUPADA', 'Ocupada'
        MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'

    id = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=100, default='Cancha Deportiva')
    tipo = models.CharField(max_length=50) # e.g., Futbol, Tenis
    ubicacion = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True, default='')
    imagen = models.CharField(max_length=200, default='reservas/images/sport_football_card.png')
    tarifa_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    estado_disponibilidad = models.CharField(
        max_length=20,
        choices=EstadoDisponibilidad.choices,
        default=EstadoDisponibilidad.DISPONIBLE,
    )

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    id = models.CharField(max_length=50, primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.usuario} - {self.fecha}"

class Pago(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA = 'TARJETA', 'Tarjeta'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'

    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADO = 'PAGADO', 'Pagado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    id = models.CharField(max_length=50, primary_key=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.CharField(max_length=50, choices=MetodoPago.choices, default=MetodoPago.EFECTIVO)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reserva'], name='unique_pago_por_reserva'),
        ]

    @property
    def valor(self):
        return self.monto

    @property
    def fecha(self):
        return self.fecha_pago

    @property
    def metodo(self):
        return self.metodo_pago

    def __str__(self):
        return f"Pago {self.id} - {self.monto}"

class Notificacion(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    tipo = models.CharField(max_length=50) # Email, SMS, etc.
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='ENVIADO')

    def __str__(self):
        return f"Notificacion {self.id} - {self.usuario}"
