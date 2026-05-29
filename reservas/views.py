# reservas/views.py
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from datetime import date, time
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from .models import Cancha, Usuario, Reserva, Pago
from .services import ReservaService, check_availability


def index(request):
    return render(request, "reservas/index.html")


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # Sincronización de respaldo (las señales también actúan automáticamente)
        username = form.cleaned_data.get('username')
        Usuario.objects.get_or_create(
            id=username,
            defaults={
                'nombre': username,
                'correo_electronico': f"{username}@example.com",
                'rol': Usuario.Rol.NORMAL,
            }
        )
        return response


class ReservaDeporteView(View):
    def get(self, request, deporte):
        # Filtramos canchas disponibles por deporte
        canchas = Cancha.objects.filter(tipo__iexact=deporte, estado_disponibilidad='DISPONIBLE')
        today_str = date.today().isoformat()
        return render(request, "reservas/reservar_deporte.html", {
            "deporte": deporte,
            "canchas": canchas,
            "today": today_str
        })


class CrearReservaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            s = ReservaService()
            # SEGURIDAD: Evitar IDOR y spoofing de usuario usando el autenticado de la sesión
            usuario_id = request.user.username
            
            # Asegurar que el Usuario del dominio exista
            Usuario.objects.get_or_create(
                id=usuario_id,
                defaults={
                    'nombre': usuario_id,
                    'correo_electronico': request.user.email or f"{usuario_id}@example.com",
                    'rol': Usuario.Rol.ADMIN if request.user.is_staff else Usuario.Rol.NORMAL,
                }
            )

            r = s.crear_reserva(
                usuario_id,
                request.POST["cancha_id"],
                date.fromisoformat(request.POST["fecha"]),
                time.fromisoformat(request.POST["hora_inicio"]),
                time.fromisoformat(request.POST["hora_fin"]),
            )
            return JsonResponse({"reserva_id": r.id, "estado": r.estado})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class DisponibilidadAPIView(View):
    def get(self, request):
        cancha_id = request.GET.get("cancha_id")
        fecha_str = request.GET.get("fecha")
        if not cancha_id or not fecha_str:
            return JsonResponse({"error": "Faltan parámetros cancha_id y fecha."}, status=400)
        try:
            fecha = date.fromisoformat(fecha_str)
            reservas = Reserva.objects.filter(
                cancha_id=cancha_id,
                fecha=fecha,
                estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA]
            ).order_by("hora_inicio")
            
            ocupados = []
            for r in reservas:
                ocupados.append({
                    "inicio": r.hora_inicio.strftime("%H:%M"),
                    "fin": r.hora_fin.strftime("%H:%M")
                })
            return JsonResponse({"ocupados": ocupados})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UserDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        usuario_id = request.user.username
        usuario, _ = Usuario.objects.get_or_create(
            id=usuario_id,
            defaults={
                'nombre': usuario_id,
                'correo_electronico': request.user.email or f"{usuario_id}@example.com",
                'rol': Usuario.Rol.ADMIN if request.user.is_staff else Usuario.Rol.NORMAL,
            }
        )
        
        today = date.today()
        
        # Reservas activas (futuras o de hoy no canceladas/rechazadas)
        reservas_activas = Reserva.objects.filter(
            usuario=usuario,
            fecha__gte=today,
            estado__in=["PENDIENTE", "CONFIRMADA"]
        ).order_by("fecha", "hora_inicio")
        
        # Historial de reservas (pasadas, o rechazadas/canceladas)
        historial_reservas = Reserva.objects.filter(
            usuario=usuario
        ).exclude(
            id__in=[r.id for r in reservas_activas]
        ).order_by("-fecha", "-hora_inicio")
        
        # Pagos del usuario
        pagos = Pago.objects.filter(reserva__usuario=usuario).order_by("-fecha_pago")
        
        # Notificaciones
        notificaciones = usuario.notificaciones.all().order_by("-fecha_envio")
        
        return render(request, "reservas/dashboard_usuario.html", {
            "reservas_activas": reservas_activas,
            "historial_reservas": historial_reservas,
            "pagos": pagos,
            "notificaciones": notificaciones,
            "usuario": usuario
        })


class CancelarReservaView(LoginRequiredMixin, View):
    def post(self, request, reserva_id):
        try:
            s = ReservaService()
            reserva = Reserva.objects.get(id=reserva_id)
            # Validar pertenencia o rol de admin
            if reserva.usuario.id != request.user.username and not request.user.is_staff:
                return JsonResponse({"error": "No tienes permiso para cancelar esta reserva."}, status=403)
                
            exito = s.cancelar(reserva_id)
            if exito:
                return JsonResponse({"success": "Reserva cancelada correctamente."})
            else:
                return JsonResponse({"error": "No se pudo cancelar la reserva."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class AdminDashboardView(LoginRequiredMixin, View):
    @method_decorator(user_passes_test(lambda u: u.is_staff, login_url="/accounts/login/"))
    def get(self, request):
        from django.db.models import Sum
        
        # KPIs
        total_usuarios = Usuario.objects.count()
        total_canchas = Cancha.objects.count()
        total_reservas = Reserva.objects.count()
        total_pagado = Pago.objects.filter(estado=Pago.EstadoPago.PAGADO).aggregate(total=Sum("monto"))["total"] or 0
        
        # Listados
        usuarios = Usuario.objects.all()
        canchas = Cancha.objects.all()
        reservas = Reserva.objects.all().order_by("-fecha", "-hora_inicio")
        pagos = Pago.objects.all().order_by("-fecha_pago")
        
        return render(request, "reservas/dashboard_admin.html", {
            "total_usuarios": total_usuarios,
            "total_canchas": total_canchas,
            "total_reservas": total_reservas,
            "total_pagado": total_pagado,
            "usuarios": usuarios,
            "canchas": canchas,
            "reservas": reservas,
            "pagos": pagos
        })


class ProcesarPagoView(LoginRequiredMixin, View):
    @method_decorator(user_passes_test(lambda u: u.is_staff, login_url="/accounts/login/"))
    def post(self, request, pago_id, accion):
        try:
            s = ReservaService()
            if accion == "aprobar":
                metodo = request.POST.get("metodo_pago", "TARJETA")
                exito = s.aprobar_pago(pago_id, metodo=metodo)
            elif accion == "rechazar":
                exito = s.rechazar_pago(pago_id)
            else:
                exito = False
                
            if exito:
                return JsonResponse({"success": f"Pago {accion}do correctamente."})
            else:
                return JsonResponse({"error": "No se pudo procesar el pago."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class CanchaCreateView(LoginRequiredMixin, View):
    @method_decorator(user_passes_test(lambda u: u.is_staff, login_url="/accounts/login/"))
    def post(self, request):
        try:
            cancha_id = request.POST["id"]
            nombre = request.POST["nombre"]
            tipo = request.POST["tipo"]
            ubicacion = request.POST["ubicacion"]
            tarifa = request.POST["tarifa_por_hora"]
            descripcion = request.POST.get("descripcion", "")
            imagen_url = request.POST.get("imagen", "")
            
            cancha = Cancha.objects.create(
                id=cancha_id,
                nombre=nombre,
                tipo=tipo,
                ubicacion=ubicacion,
                tarifa_por_hora=tarifa,
                descripcion=descripcion,
                estado_disponibilidad="DISPONIBLE"
            )
            if imagen_url:
                cancha.imagen = imagen_url
                cancha.save()
                
            return redirect("admin_dashboard")
        except Exception as e:
            # En caso de error, podríamos renderizar con un mensaje flash, pero para simplificar AJAX/Post:
            return JsonResponse({"error": str(e)}, status=400)


class CanchaDeleteView(LoginRequiredMixin, View):
    @method_decorator(user_passes_test(lambda u: u.is_staff, login_url="/accounts/login/"))
    def post(self, request, cancha_id):
        try:
            cancha = Cancha.objects.get(id=cancha_id)
            cancha.delete()
            return JsonResponse({"success": "Cancha eliminada con éxito."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
