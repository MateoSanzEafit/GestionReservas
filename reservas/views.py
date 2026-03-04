# reservas/views.py
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from datetime import date, time
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from .models import Cancha, Usuario
from .services import ReservaService


def index(request):
    return render(request, "reservas/index.html")


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # Sincronizar con el modelo Usuario del dominio
        username = form.cleaned_data.get('username')
        Usuario.objects.get_or_create(
            id=username,
            defaults={
                'nombre': username,
                'correo_electronico': f"{username}@example.com"
            }
        )
        return response


class ReservaDeporteView(View):
    def get(self, request, deporte):
        canchas = Cancha.objects.filter(tipo__iexact=deporte, estado_disponibilidad='DISPONIBLE')
        return render(request, "reservas/reservar_deporte.html", {
            "deporte": deporte,
            "canchas": canchas
        })


class CrearReservaView(View):
    def post(self, request):
        try:
            s = ReservaService()
            usuario_id = request.POST["usuario_id"]
            
            # Asegurar que el Usuario del dominio exista (para usuarios previos como admin)
            Usuario.objects.get_or_create(
                id=usuario_id,
                defaults={
                    'nombre': usuario_id,
                    'correo_electronico': f"{usuario_id}@example.com"
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
