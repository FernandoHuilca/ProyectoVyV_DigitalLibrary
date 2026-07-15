from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from modulo_publicaciones_apuntes.models import Apunte, ApunteGuardado  # Importamos ApunteGuardado
from modulo_publicaciones_apuntes.services import servicio_guardado_apuntes
from modulo_usuarios.models import PerfilEstudiante


# ── FUNCIÓN AUXILIAR DE NEGOCIO ──────────────────────────────────────
def _procesar_toggle_guardado(request, apunte):
    servicio_guardados = servicio_guardado_apuntes()
    perfil_usuario = request.user.perfil

    ya_guardado = servicio_guardados.esta_guardado(perfil_usuario, apunte)
    try:
        if ya_guardado:
            servicio_guardados.quitar(perfil_usuario, apunte)
            messages.success(request, "Apunte quitado de guardados.")
        else:
            servicio_guardados.guardar(perfil_usuario, apunte)
            messages.success(request, "Apunte guardado correctamente.")
    except (PermissionDenied, ValueError) as error:
        messages.error(request, str(error))


# ── VISTAS ───────────────────────────────────────────────────────────

@login_required
def lista_apuntes(request):
    # Consultamos la base de datos de apuntes disponibles.
    apuntes_bd = Apunte.objects.filter(disponible=True).order_by('-fecha_creacion')

    # Añadimos los publicadores destacados del ranking
    top_publicadores = (
        PerfilEstudiante.objects
        .select_related("usuario")
        .order_by("-puntos_prestigio")[:10]
    )

    perfil_usuario = request.user.perfil

    # Usamos el ORM de Django para traer eficientemente solo los IDs de los apuntes
    # que este usuario en particular ya tiene guardados.
    guardados_ids = set(
        ApunteGuardado.objects.filter(usuario=perfil_usuario)
        .values_list('apunte_id', flat=True)
    )

    # Empaquetamos los datos en el contexto para la plantilla
    contexto = {
        'apuntes': apuntes_bd,
        'top_publicadores': top_publicadores,
        'guardados': guardados_ids  # Esto habilita el: {% if apunte.id in guardados %}
    }

    return render(request, 'publicaciones/lista_apuntes.html', contexto)


@login_required
def vista_apunte(request, pk):
    apunte = get_object_or_404(Apunte, pk=pk)
    if not apunte.disponible or apunte.acceso_restringido:
        raise Http404("El apunte no está disponible.")

    servicio_guardados = servicio_guardado_apuntes()
    perfil_usuario = request.user.perfil

    if request.method == "POST":
        # Reutilizamos la función auxiliar común
        _procesar_toggle_guardado(request, apunte)
        return redirect("publicaciones:vista_apunte", pk=apunte.pk)

    contexto = {
        'apunte': apunte,
        'esta_guardado': servicio_guardados.esta_guardado(perfil_usuario, apunte),
    }

    return render(request, 'publicaciones/vista_apunte.html', contexto)


@login_required
def guardar_apunte(request, pk):
    """
    Nueva vista que procesa la acción de guardar desde el listado general
    y redirige al usuario al mismo punto donde hizo clic.
    """
    apunte = get_object_or_404(Apunte, pk=pk)

    if request.method == "POST":
        _procesar_toggle_guardado(request, apunte)

    # Vuelve a la página origen (el listado) usando HTTP_REFERER.
    return redirect(request.META.get("HTTP_REFERER", "publicaciones:lista_apuntes"))


@login_required
def mi_biblioteca(request):
    perfil_usuario = request.user.perfil

    # 1. Filtramos los registros guardados por este usuario.
    # Usamos select_related para traer los apuntes en una sola consulta SQL optimizada.
    guardados_relacion = (
        ApunteGuardado.objects
        .filter(usuario=perfil_usuario)
        .select_related('apunte')
    )

    # 2. Extraemos los apuntes asociados que se encuentren disponibles (activos)
    apuntes_guardados = [
        reg.apunte for reg in guardados_relacion
        if reg.apunte.disponible and not reg.apunte.acceso_restringido
    ]

    # 3. Guardamos los IDs en un set para pintar los iconos de guardado de forma instantánea
    guardados_ids = {apunte.id for apunte in apuntes_guardados}

    # 4. Traemos los publicadores destacados (el ranking que usa tu barra lateral)
    top_publicadores = (
        PerfilEstudiante.objects
        .select_related("usuario")
        .order_by("-puntos_prestigio")[:10]
    )

    contexto = {
        'apuntes': apuntes_guardados,
        'guardados': guardados_ids,
        'top_publicadores': top_publicadores
    }

    return render(request, 'publicaciones/mi_biblioteca.html', contexto)