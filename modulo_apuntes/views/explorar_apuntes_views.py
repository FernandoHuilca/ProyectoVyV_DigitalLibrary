from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Prefetch, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from modulo_apuntes.models import Apunte, ApunteGuardado, Calificacion, Comentario  # Importamos ApunteGuardado
from modulo_apuntes.services import ServicioGuardadoApuntes, ServicioCalificacion, ServicioComentario
from modulo_usuarios.models import PerfilEstudiante


# ── FUNCIÓN AUXILIAR DE NEGOCIO ──────────────────────────────────────
def _procesar_toggle_guardado(request, apunte):
    servicio_guardados = ServicioGuardadoApuntes()
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
    servicio_calificacion = ServicioCalificacion()
    apuntes_bd = list(
        Apunte.objects.filter(disponible=True)
        .select_related("autor__usuario")
        .annotate(
            total_utiles=Count("calificaciones", filter=Q(calificaciones__tipo=Calificacion.TIPO_UTIL)),
            total_no_utiles=Count("calificaciones", filter=Q(calificaciones__tipo=Calificacion.TIPO_NO_UTIL)),
        )
        .order_by('-fecha_creacion')
    )

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

    votos_usuario = dict(
        Calificacion.objects.filter(usuario=perfil_usuario)
        .values_list("apunte_id", "tipo")
    )

    for apunte in apuntes_bd:
        apunte.prestigio_utilidad = servicio_calificacion.prestigio_de_apunte(apunte)
        apunte.mi_voto = votos_usuario.get(apunte.id)

    # Empaquetamos los datos en el contexto para la plantilla
    contexto = {
        'apuntes': apuntes_bd,
        'top_publicadores': top_publicadores,
        'guardados': guardados_ids  # Esto habilita el: {% if apunte.id in guardados %}
    }

    return render(request, 'lista_apuntes.html', contexto)


@login_required
def vista_apunte(request, pk):
    servicio_calificacion = ServicioCalificacion()
    comentarios_con_respuestas = Comentario.objects.select_related(
        "autor__usuario",
        "parent__autor__usuario",
    ).order_by("creado_en")
    apunte = get_object_or_404(
        Apunte.objects.select_related("autor__usuario").annotate(
            total_utiles=Count("calificaciones", filter=Q(calificaciones__tipo=Calificacion.TIPO_UTIL)),
            total_no_utiles=Count("calificaciones", filter=Q(calificaciones__tipo=Calificacion.TIPO_NO_UTIL)),
        ).prefetch_related(
            Prefetch(
                "comentarios",
                queryset=Comentario.objects.filter(parent__isnull=True)
                .select_related("autor__usuario")
                .prefetch_related(
                    Prefetch("respuestas", queryset=comentarios_con_respuestas, to_attr="respuestas_cargadas")
                )
                .order_by("creado_en"),
            )
        ),
        pk=pk,
    )
    if not apunte.disponible or apunte.acceso_restringido:
        raise Http404("El apunte no está disponible.")

    servicio_guardados = ServicioGuardadoApuntes()
    perfil_usuario = request.user.perfil
    apunte.prestigio_utilidad = servicio_calificacion.prestigio_de_apunte(apunte)
    apunte.mi_voto = servicio_calificacion.tipo_usuario_en_apunte(perfil_usuario, apunte)
    apunte.comentarios_principales = list(apunte.comentarios.all())

    if request.method == "POST":
        # Reutilizamos la función auxiliar común
        _procesar_toggle_guardado(request, apunte)
        return redirect("apuntes:vista_apunte", pk=apunte.pk)

    contexto = {
        'apunte': apunte,
        'esta_guardado': servicio_guardados.esta_guardado(perfil_usuario, apunte),
        'comentarios_principales': apunte.comentarios_principales,
    }

    return render(request, 'vista_apunte.html', contexto)


@login_required
@require_POST
def gestionar_comentario_apunte(request, pk):
    apunte = get_object_or_404(Apunte.objects.select_related("autor__usuario"), pk=pk)
    servicio_comentario = ServicioComentario()
    accion = request.POST.get("accion", "")
    contenido = (request.POST.get("contenido", "") or "").strip()

    try:
        if accion == "crear_comentario":
            if not contenido:
                messages.error(request, "El comentario no puede estar vacío.")
                return redirect("apuntes:vista_apunte", pk=apunte.pk)
            parent_id = request.POST.get("parent_id") or None
            parent = None
            if parent_id:
                parent = get_object_or_404(Comentario.objects.select_related("autor", "apunte"), pk=parent_id, apunte=apunte)
            servicio_comentario.crear_comentario(
                autor=request.user.perfil,
                apunte=apunte,
                contenido=contenido,
                parent=parent,
            )
            messages.success(request, "Comentario publicado correctamente.")
        elif accion == "editar_comentario":
            if not contenido:
                messages.error(request, "El comentario no puede estar vacío.")
                return redirect("apuntes:vista_apunte", pk=apunte.pk)
            comentario = get_object_or_404(Comentario.objects.select_related("autor", "apunte"), pk=request.POST.get("comentario_id"), apunte=apunte)
            servicio_comentario.editar_comentario(
                usuario_solicitante=request.user.perfil,
                comentario=comentario,
                nuevo_contenido=contenido,
            )
            messages.success(request, "Comentario actualizado correctamente.")
        elif accion == "toggle_corazon":
            comentario = get_object_or_404(Comentario.objects.select_related("autor", "apunte"), pk=request.POST.get("comentario_id"), apunte=apunte)
            servicio_comentario.dar_corazon(
                usuario_solicitante=request.user.perfil,
                comentario=comentario,
            )
            messages.success(request, "Corazón actualizado correctamente.")
        else:
            messages.error(request, "Acción de comentario no soportada.")
    except (PermissionDenied, ValidationError) as error:
        messages.error(request, str(error))

    return redirect("apuntes:vista_apunte", pk=apunte.pk)


@login_required
@require_POST
def calificar_apunte(request, pk):
    apunte = get_object_or_404(Apunte.objects.select_related("autor__usuario"), pk=pk)
    if not apunte.disponible or apunte.acceso_restringido:
        raise Http404("El apunte no está disponible.")

    servicio_calificacion = ServicioCalificacion()
    tipo = request.POST.get("tipo", "")

    try:
        servicio_calificacion.calificar(request.user.perfil, apunte, tipo)
    except PermissionDenied as error:
        return JsonResponse({"error": str(error)}, status=403)
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)

    apunte.refresh_from_db()
    apunte.autor.refresh_from_db()

    conteos = servicio_calificacion.conteo_apunte(apunte)
    voto_usuario = servicio_calificacion.tipo_usuario_en_apunte(request.user.perfil, apunte)

    return JsonResponse(
        {
            "apunte_id": apunte.pk,
            "total_utiles": conteos[Calificacion.TIPO_UTIL],
            "total_no_utiles": conteos[Calificacion.TIPO_NO_UTIL],
            "prestigio_apunte": servicio_calificacion.prestigio_de_apunte(apunte),
            "prestigio_autor": apunte.autor.puntos_prestigio,
            "rango_autor": apunte.autor.rango,
            "voto_usuario": voto_usuario or "",
        }
    )


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
    return redirect(request.META.get("HTTP_REFERER", "apuntes:lista_apuntes"))


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

    return render(request, 'mi_biblioteca.html', contexto)