from django.db import models

class Usuario(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Using CharField as per diagram, typically AutoField/UUID
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True) # Added unique constraint for email
    fecha_registro = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='ACTIVO')

    def __str__(self):
        return self.nombre

class Cancha(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    tipo = models.CharField(max_length=50) # e.g., Futbol, Tenis
    ubicacion = models.CharField(max_length=100)
    tarifa_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    estado_disponibilidad = models.CharField(max_length=20, default='DISPONIBLE')

    def __str__(self):
        return f"{self.tipo} - {self.ubicacion}"

class Reserva(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, default='PENDIENTE')
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.usuario} - {self.fecha}"

class Pago(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='PENDIENTE')
    fecha_pago = models.DateTimeField(auto_now_add=True)

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
