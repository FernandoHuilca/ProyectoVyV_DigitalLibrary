from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from modulo_apuntes.services import ServicioDescargas


from modulo_apuntes.models import Apunte
from modulo_apuntes.forms.ApunteCreacionForm import ApunteForm

@login_required
def mis_apuntes(request):
    """
    Vista única para listar, crear, actualizar y eliminar apuntes propios.

    """
    perfil = request.user.perfil
    apuntes = Apunte.objects.filter(autor=perfil).order_by('-fecha_creacion')

    # Determinar modo: CREATE o UPDATE
    apunte_editando = None
    pk_editar = request.GET.get('editar')

    if pk_editar:
        # Seguridad: solo el dueño puede cargar su apunte en el formulario
        apunte_editando = get_object_or_404(Apunte, pk=pk_editar, autor=perfil)

    # Manejar POST (guardar)
    if request.method == 'POST':
        pk_post = request.POST.get('apunte_id')
        instancia = None

        if pk_post:
            # UPDATE: verificar que el apunte pertenece al usuario
            instancia = get_object_or_404(Apunte, pk=pk_post, autor=perfil)

        form = ApunteForm(request.POST, request.FILES, instance=instancia)

        if form.is_valid():
            apunte = form.save(commit=False)
            apunte.autor = perfil
            apunte.save()

            if instancia:
                messages.success(request, f'"{apunte.titulo}" actualizado correctamente.')
            else:
                messages.success(request, f'"{apunte.titulo}" publicado correctamente.')

            return redirect('apuntes:lista_mis_apuntes')

        # Si el form no es válido, volvemos a mostrar la página
        # con los errores Y el apunte que se estaba editando (si aplica)
        if pk_post:
            apunte_editando = get_object_or_404(Apunte, pk=pk_post, autor=perfil)

    else:
        # GET: inicializar formulario vacío o con instancia
        form = ApunteForm(instance=apunte_editando)

    context = {
        'apuntes': apuntes,
        'form': form,
        'apunte_editando': apunte_editando,
        'total_apuntes': apuntes.count(),
        # TODO: descomentar cuando se implementen las estadísticas
        # 'total_vistas': ...,
        # 'total_me_gustas': ...,
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
