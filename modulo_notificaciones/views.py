from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from modulo_notificaciones.models import Notificacion
from modulo_usuarios.models import PerfilEstudiante
from modulo_usuarios.services.servicio_suscripciones import ServicioSuscripciones


@login_required
def suscribirse(request, perfil_id):
    publicador = get_object_or_404(PerfilEstudiante, pk=perfil_id)
    ServicioSuscripciones().suscribir(request.user.perfil, publicador)
    return redirect(request.META.get("HTTP_REFERER", "publicaciones:lista_apuntes"))


@login_required
def cancelar_suscripcion(request, perfil_id):
    publicador = get_object_or_404(PerfilEstudiante, pk=perfil_id)
    ServicioSuscripciones().cancelar_suscripcion(request.user.perfil, publicador)
    return redirect(request.META.get("HTTP_REFERER", "publicaciones:lista_apuntes"))


@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(receptor=request.user).order_by("-creado_en")
    return render(
        request,
        "notificaciones/lista_notificaciones.html",
        {"notificaciones": notificaciones},
    )


@login_required
def marcar_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk, receptor=request.user)
    notificacion.leido = True
    notificacion.save(update_fields=["leido"])
    return redirect("notificaciones:lista_notificaciones")

