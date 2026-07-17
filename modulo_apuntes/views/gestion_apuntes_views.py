from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from modulo_apuntes.services import ServicioDescargas

from modulo_apuntes.models.solicitud_revision import SolicitudRevision
from modulo_apuntes.models import Apunte
from modulo_apuntes.forms.ApunteCreacionForm import ApunteForm


@login_required
def mis_apuntes(request):
    """
    Vista única para listar, crear, actualizar y eliminar apuntes propios.
    """
    perfil = request.user.perfil
    apuntes = Apunte.objects.filter(autor=perfil).order_by('-fecha_creacion')

    apunte_editando = None
    pk_editar = request.GET.get('editar')

    if pk_editar:
        apunte_editando = get_object_or_404(Apunte, pk=pk_editar, autor=perfil)

    if request.method == 'POST':
        pk_post = request.POST.get('apunte_id')
        instancia = None

        if pk_post:
            instancia = get_object_or_404(Apunte, pk=pk_post, autor=perfil)

        # NUEVO: Pasamos user=request.user al formulario para filtrar la lista de revisores
        form = ApunteForm(request.POST, request.FILES, instance=instancia, user=request.user)

        if form.is_valid():
            apunte = form.save(commit=False)
            apunte.autor = perfil

            # NUEVO: Capturamos qué botón presionó el usuario y los datos extra
            accion = request.POST.get('accion')
            revisor = form.cleaned_data.get('revisor')
            comentario_autor = form.cleaned_data.get('comentario_autor')

            if accion == 'enviar_revision':
                if not revisor:
                    # Si intenta enviar a revisión pero no seleccionó a nadie
                    form.add_error('revisor', 'Debes seleccionar un estudiante para revisar tu apunte.')
                else:
                    apunte.estado = 'EN_REVISION'
                    apunte.save()

                    # Creamos la solicitud de revisión en la base de datos
                    SolicitudRevision.objects.create(
                        apunte=apunte,
                        revisor=revisor,
                        estado='PENDIENTE',
                        comentario_autor=comentario_autor
                    )
                    messages.success(request, f'"{apunte.titulo}" enviado a revisión correctamente.')
                    return redirect('apuntes:lista_mis_apuntes')

            elif accion == 'publicar':
                apunte.estado = 'PUBLICADO'
                apunte.save()
                messages.success(request, f'"{apunte.titulo}" publicado en la plataforma.')
                return redirect('apuntes:lista_mis_apuntes')

            elif accion == 'guardar_cambios':
                # Si solo está editando un apunte existente sin cambiar su estado
                apunte.save()
                messages.success(request, f'"{apunte.titulo}" actualizado correctamente.')
                return redirect('apuntes:lista_mis_apuntes')

            # Fallback por si no coincide ninguna acción
            if not form.errors:
                apunte.save()
                return redirect('apuntes:lista_mis_apuntes')

        if pk_post:
            apunte_editando = get_object_or_404(Apunte, pk=pk_post, autor=perfil)

    else:
        # GET: inicializar formulario vacío o con instancia
        # NUEVO: Pasamos user=request.user
        form = ApunteForm(instance=apunte_editando, user=request.user)

    context = {
        'apuntes': apuntes,
        'form': form,
        'apunte_editando': apunte_editando,
        'total_apuntes': apuntes.count(),
    }
    return render(request, 'lista_mis_apuntes.html', context)


@login_required
def eliminar_apunte(request, pk):
    """
    Elimina un apunte del usuario autenticado.
    Solo el dueño del apunte puede eliminarlo.
    """
    # Obtener el apunte o error 404
    # Seguridad: solo permite eliminar si el autor es el usuario actual
    apunte = get_object_or_404(Apunte, pk=pk, autor=request.user.perfil)

    # Guardar el título para el mensaje de confirmación
    titulo = apunte.titulo

    # 1. Eliminar referencias (guardados de otros usuarios)
    # Esto es automático con on_delete=CASCADE, pero puedes ser explícito:
    # apunte.guardados.all().delete()  # ← Opcional, Django ya lo hace

    # 2. Eliminar archivos físicos (si quieres liberar espacio)
    if apunte.contenido:
        apunte.contenido.delete(save=False)
    if apunte.portada:
        apunte.portada.delete(save=False)

    # 3. Eliminar el apunte (y automáticamente los guardados por CASCADE)
    apunte.delete()

    # Mensaje de éxito
    messages.success(request, f'"{titulo}" eliminado correctamente.')

    # Redirigir a la lista de mis apuntes
    return HttpResponseRedirect(reverse('apuntes:lista_mis_apuntes'))


@login_required
def descargar_apunte(request, pk):
    servicio_descargas = ServicioDescargas()

    apunte = get_object_or_404(Apunte, pk=pk)

    # Valida el estado del apunte, registra la descarga
    # e incrementa el prestigio del autor (según la lógica del servicio)
    servicio_descargas.descargar(
        request.user.perfil,
        apunte
    )

    return FileResponse(
        apunte.contenido.open("rb"),
        as_attachment=True,
        filename=apunte.contenido.name.split("/")[-1],
    )


@login_required
def publicar_apunte_aprobado(request, pk):
    """
    Vista exclusiva para que el autor confirme la publicación de un apunte
    que ya fue aprobado por un revisor.
    """
    if request.method == 'POST':
        # Buscamos el apunte asegurándonos de que le pertenezca al usuario (PerfilEstudiante)
        apunte = get_object_or_404(Apunte, pk=pk, autor=request.user.perfil)

        # Validamos que realmente tenga el estado correcto antes de publicarlo
        if apunte.estado == 'APROBADO':
            apunte.estado = 'PUBLICADO'
            # Aprovechamos para marcarlo como disponible en la base de datos general
            apunte.disponible = True
            apunte.save()
            messages.success(request, f'¡Excelente! "{apunte.titulo}" ya es público en la plataforma.')

    # Redirigimos siempre a la lista de apuntes propios
    return redirect('publicaciones:lista_mis_apuntes')