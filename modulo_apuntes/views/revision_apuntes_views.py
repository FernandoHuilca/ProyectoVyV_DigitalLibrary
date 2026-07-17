from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modulo_apuntes.models.solicitud_revision import SolicitudRevision
from modulo_prestigio.services import ServicioNivelesPrestigio # Importa el servicio

@login_required
def panel_revisiones(request):
    """
    Muestra al usuario los apuntes que otros le han enviado para revisar.
    """
    # 1. Filtramos las solicitudes que están esperando la acción de este usuario
    solicitudes_pendientes = SolicitudRevision.objects.filter(
        revisor=request.user,
        estado='PENDIENTE'
    ).order_by('-fecha_creacion')

    # 2. Filtramos el historial (las que ya aprobó o rechazó)
    solicitudes_historial = SolicitudRevision.objects.filter(
        revisor=request.user
    ).exclude(estado='PENDIENTE').order_by('-fecha_revision')

    context = {
        'pendientes': solicitudes_pendientes,
        'historial': solicitudes_historial,
    }

    return render(request, 'mis_revisiones.html', context)


@login_required
def calificar_revision(request, revision_id):
    solicitud = get_object_or_404(SolicitudRevision, pk=revision_id, revisor=request.user)
    apunte = solicitud.apunte
    # Instanciamos el servicio de prestigio
    servicio_prestigio = ServicioNivelesPrestigio()

    if request.method == 'POST':
        accion = request.POST.get('accion')
        comentario = request.POST.get('comentario_revisor', '')

        solicitud.comentario_revisor = comentario

        if accion == 'aprobar':
            solicitud.estado = 'APROBADO'
            apunte.estado = 'APROBADO'

            # ── OTORGAMIENTO DE PUNTOS POR APROBAR ──
            # Obtenemos el perfil del revisor (el usuario actual) y sumamos 15 puntos
            perfil_revisor = request.user.perfil
            servicio_prestigio.incrementar_prestigio(perfil_revisor, 15)

        elif accion == 'rechazar':
            solicitud.estado = 'RECHAZADO'
            apunte.estado = 'BORRADOR'


        solicitud.save()
        apunte.save()

        messages.success(request, f'Tu revisión para "{apunte.titulo}" fue enviada. ¡Has ganado 15 puntos de prestigio!')
        return redirect('publicaciones:mis_revisiones')

    context = {
        'solicitud': solicitud,
        'apunte': apunte,
    }
    return render(request, 'calificar_apunte.html', context)