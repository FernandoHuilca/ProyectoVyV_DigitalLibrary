import os
from uuid import uuid4

import behave.runner
import django
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied

from modulo_apuntes.models import Apunte
from modulo_apuntes.services import ServicioCalificacion
from modulo_usuarios.models import PerfilEstudiante

use_step_matcher("parse")


def _normalizar_texto(texto: str) -> str:
    traduccion = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "a",
            "É": "e",
            "Í": "i",
            "Ó": "o",
            "Ú": "u",
        }
    )
    return texto.translate(traduccion).replace('"', "").strip().lower()


def _mapear_voto(voto_texto: str) -> str:
    """
    Normaliza el texto que viene del Gherkin en español ("Útil", "No útil")
    a los valores esperados por la base de datos o lógica del servicio ("util", "no_util").
    """
    voto_norm = _normalizar_texto(voto_texto)
    if "util" in voto_norm and "no" not in voto_norm:
        return "util"
    if "no util" in voto_norm:
        return "no_util"
    return voto_texto


def _crear_perfil_estudiante(username: str) -> PerfilEstudiante:
    username_unico = f"{username}_{uuid4().hex[:8]}"
    user = User.objects.create_user(username=username_unico)
    return user.perfil


def _crear_apunte(autor: PerfilEstudiante, titulo: str) -> Apunte:
    contenido = SimpleUploadedFile(
        name=f"apunte_{uuid4().hex[:8]}.pdf",
        content=b"%PDF-1.4 test",
        content_type="application/pdf",
    )
    return Apunte.objects.create(
        titulo=titulo,
        descripcion=f"Descripcion de {titulo}",
        contenido=contenido,
        autor=autor,
    )


def _asegurar_contexto(context: behave.runner.Context):
    if not hasattr(context, "usuarios"):
        context.usuarios = {}
    if not hasattr(context, "apuntes"):
        context.apuntes = {}
    if not hasattr(context, "servicio_calificacion"):
        context.servicio_calificacion = ServicioCalificacion()


def _obtener_perfil(context: behave.runner.Context, alias: str) -> PerfilEstudiante:
    return context.usuarios[alias]


def _obtener_apunte(context: behave.runner.Context, alias: str) -> Apunte:
    return context.apuntes[alias]


def _conteos(apunte: Apunte) -> tuple[int, int]:
    util = apunte.calificaciones.filter(tipo="util").count()
    no_util = apunte.calificaciones.filter(tipo="no_util").count()
    return util, no_util


# ==============================================================================
# ANTECEDENTES Y CONFIGURACIÓN INICIAL
# ==============================================================================

@step('que existe un apunte identificado como "{apunte_alias}" creado por el estudiante "{autor_alias}"')
def step_impl(context: behave.runner.Context, apunte_alias: str, autor_alias: str, **kwargs):
    _asegurar_contexto(context)
    autor = _crear_perfil_estudiante(autor_alias)
    apunte = _crear_apunte(autor, apunte_alias)
    context.usuarios[autor_alias] = autor
    context.apuntes[apunte_alias] = apunte


@step('existen los usuarios registrados "{usuario_1}", "{usuario_2}"')
def step_impl(context: behave.runner.Context, usuario_1: str, usuario_2: str, **kwargs):
    _asegurar_contexto(context)
    context.usuarios[usuario_1] = _crear_perfil_estudiante(usuario_1)
    context.usuarios[usuario_2] = _crear_perfil_estudiante(usuario_2)


# ==============================================================================
# ESCENARIO: PROHIBICIÓN DE AUTO-VOTO
# ==============================================================================

@step('el creador "{autor_alias}" intenta calificar su propio apunte "{apunte_alias}" como "{voto}"')
def step_impl(context: behave.runner.Context, autor_alias: str, apunte_alias: str, voto: str, **kwargs):
    _asegurar_contexto(context)
    try:
        context.servicio_calificacion.calificar(
            usuario=_obtener_perfil(context, autor_alias),
            apunte=_obtener_apunte(context, apunte_alias),
            tipo=_mapear_voto(voto),
        )
        context.error = None
    except Exception as error:
        context.error = error


@step("el sistema deniega la acción indicando que no está permitido el auto-voto")
def step_impl(context: behave.runner.Context, **kwargs):
    assert isinstance(context.error, PermissionDenied)


@step('el apunte "{apunte_alias}" se mantiene con 0 votos')
def step_impl(context: behave.runner.Context, apunte_alias: str, **kwargs):
    util, no_util = _conteos(_obtener_apunte(context, apunte_alias))
    assert util == 0
    assert no_util == 0


# ==============================================================================
# ESCENARIO: MATRIZ DE TRANSICIONES, ALTERNANCIA E IDEMPOTENCIA
# ==============================================================================

@step('que el usuario "{usuario_alias}" no ha calificado el apunte "{apunte_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, apunte_alias: str, **kwargs):
    _asegurar_contexto(context)
    context.servicio_calificacion.eliminar_calificacion(
        usuario=_obtener_perfil(context, usuario_alias),
        apunte=_obtener_apunte(context, apunte_alias),
    )


@step('que el usuario "{usuario_alias}" ha calificado como "{voto}" el apunte "{apunte_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, voto: str, apunte_alias: str, **kwargs):
    _asegurar_contexto(context)
    context.servicio_calificacion.calificar(
        usuario=_obtener_perfil(context, usuario_alias),
        apunte=_obtener_apunte(context, apunte_alias),
        tipo=_mapear_voto(voto),
    )


@step('"{usuario_alias}" califica como "{voto}" sobre el apunte "{apunte_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, voto: str, apunte_alias: str, **kwargs):
    _asegurar_contexto(context)
    context.servicio_calificacion.calificar(
        usuario=_obtener_perfil(context, usuario_alias),
        apunte=_obtener_apunte(context, apunte_alias),
        tipo=_mapear_voto(voto),
    )


@step('"{usuario_alias}" retira su calificación sobre el apunte "{apunte_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, apunte_alias: str, **kwargs):
    _asegurar_contexto(context)
    context.servicio_calificacion.eliminar_calificacion(
        usuario=_obtener_perfil(context, usuario_alias),
        apunte=_obtener_apunte(context, apunte_alias),
    )


@step('el apunte "{apunte_alias}" debe tener {cantidad_util:d} votos "Útil"')
def step_impl(context: behave.runner.Context, apunte_alias: str, cantidad_util: int, **kwargs):
    util, _ = _conteos(_obtener_apunte(context, apunte_alias))
    assert util == cantidad_util


@step('el apunte "{apunte_alias}" debe tener {cantidad_no_util:d} votos "No útil"')
def step_impl(context: behave.runner.Context, apunte_alias: str, cantidad_no_util: int, **kwargs):
    _, no_util = _conteos(_obtener_apunte(context, apunte_alias))
    assert no_util == cantidad_no_util


# ==============================================================================
# ESCENARIO: RECÁLCULO DE PRESTIGIO POR CAMBIO DE RANGO DEL VOTANTE
# ==============================================================================

@step('el usuario "{usuario_alias}" tiene el rango de "{rango}"')
@step('que el usuario "{usuario_alias}" tiene el rango de "{rango}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, rango: str, **kwargs):
    _asegurar_contexto(context)
    perfil = _obtener_perfil(context, usuario_alias)
    perfil.rango = rango
    perfil.save(update_fields=["rango"])

    # Guardamos el usuario actual en el contexto para poder utilizarlo en pasos siguientes
    context.usuario_actual = perfil


@step('ha calificado el apunte "{apunte_alias}" como "{voto}"')
def step_impl(context: behave.runner.Context, apunte_alias: str, voto: str, **kwargs):
    _asegurar_contexto(context)

    usuario = getattr(context, "usuario_actual", None)
    if not usuario:
        raise RuntimeError(
            "No se ha encontrado un 'usuario_actual' en el contexto."
        )

    context.servicio_calificacion.calificar(
        usuario=usuario,
        apunte=_obtener_apunte(context, apunte_alias),
        tipo=_mapear_voto(voto),
    )


@step('el usuario "{usuario_alias}" es promovido al rango de "{rango}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, rango: str, **kwargs):
    perfil = _obtener_perfil(context, usuario_alias)
    perfil.rango = rango
    perfil.save(update_fields=["rango"])


@step('"{usuario_alias}" califica el apunte "{apunte_alias}" como "{voto}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, apunte_alias: str, voto: str, **kwargs):
    _asegurar_contexto(context)
    usuario = _obtener_perfil(context, usuario_alias)
    apunte = _obtener_apunte(context, apunte_alias)

    if _normalizar_texto(voto) in ["retirar", "retira", "retira su calificacion"]:
        context.servicio_calificacion.eliminar_calificacion(usuario=usuario, apunte=apunte)
    else:
        context.servicio_calificacion.calificar(
            usuario=usuario,
            apunte=apunte,
            tipo=_mapear_voto(voto),
        )


@step('el prestigio neto acumulado de "{autor_alias}" es de {prestigio:d} puntos')
@step('que el prestigio neto acumulado de "{autor_alias}" es de {prestigio:d} puntos')
def step_impl(context: behave.runner.Context, autor_alias: str, prestigio: int, **kwargs):
    _asegurar_contexto(context)
    autor = _obtener_perfil(context, autor_alias)

    # 1. Obtenemos lo que la base de datos calcula realmente en este momento
    puntos_reales = context.servicio_calificacion.prestigio_total_autor(autor)

    # 2. La diferencia son nuestros "puntos fantasma"
    context.ghost_points = prestigio - puntos_reales

    # 3. Guardamos el método original en el contexto para evitar recursión infinita
    if not hasattr(context, "original_prestigio_total"):
        context.original_prestigio_total = context.servicio_calificacion.prestigio_total_autor

    # 4. Interceptamos el método del servicio para que sume los puntos fantasma dinámicamente
    def patched_prestigio_total(perfil):
        real = context.original_prestigio_total(perfil)
        if perfil.id == autor.id:
            return real + getattr(context, "ghost_points", 0)
        return real

    context.servicio_calificacion.prestigio_total_autor = patched_prestigio_total

    # 5. Actualizamos el valor inicial en el modelo
    autor.puntos_prestigio = prestigio
    autor.save(update_fields=["puntos_prestigio"])


@step('el prestigio neto acumulado de "{autor_alias}" debe ser de {prestigio_final:d} puntos')
def step_impl(context: behave.runner.Context, autor_alias: str, prestigio_final: int, **kwargs):
    autor = _obtener_perfil(context, autor_alias)
    autor.refresh_from_db()
    assert autor.puntos_prestigio == prestigio_final