# reservas/views.py
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from datetime import date, time

from .services import ReservaService


def index(request):
    return render(request, "reservas/index.html")


class CrearReservaView(View):
    def post(self, request):
        s = ReservaService()
        r = s.crear_reserva(
            request.POST["usuario_id"],
            request.POST["cancha_id"],
            date.fromisoformat(request.POST["fecha"]),
            time.fromisoformat(request.POST["hora_inicio"]),
            time.fromisoformat(request.POST["hora_fin"]),
        )
        return JsonResponse({"reserva_id": r.id, "estado": r.estado})
