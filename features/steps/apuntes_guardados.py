import os
from uuid import uuid4

import behave.runner
import django
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from modulo_apuntes.models import Apunte
from modulo_apuntes.services import servicio_guardado_apuntes
from modulo_usuarios.models import PerfilEstudiante

use_step_matcher("parse")


def _normalizar(texto: str) -> str:
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


@step('que el usuario no tiene el apunte "{note}" en su lista de guardados')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados = servicio_guardado_apuntes()
    context.autor_apunte = _crear_perfil_estudiante("autor_guardado")
    context.usuario_actual = _crear_perfil_estudiante("usuario_guardado")
    context.apunte = _crear_apunte(context.autor_apunte, note)
    context.prestigio_autor_inicial = context.autor_apunte.puntos_prestigio
    assert not context.servicio_guardados.esta_guardado(context.usuario_actual, context.apunte)


@step('el apunte "{note}" se encuentra disponible y es accesible para el usuario')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados.asegurar_apunte_disponible(context.apunte)
    estado = context.servicio_guardados.estado_de(context.apunte)
    assert estado.disponible
    assert not estado.acceso_restringido


@step('el usuario guarda el apunte "{note}"')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados.guardar(context.usuario_actual, context.apunte)


@step('el sistema registra el apunte "{note}" en la lista de guardados del usuario')
def step_impl(context: behave.runner.Context, note: str):
    assert context.servicio_guardados.esta_guardado(context.usuario_actual, context.apunte)


@step('el prestigio del autor del apunte "{note}" se incrementa en "{points:d}" puntos')
def step_impl(context: behave.runner.Context, note: str, points: int):
    context.autor_apunte.refresh_from_db()
    assert context.autor_apunte.puntos_prestigio == context.prestigio_autor_inicial + points


@step('que el usuario tiene guardado el apunte "{note}"')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados = servicio_guardado_apuntes()
    context.autor_apunte = _crear_perfil_estudiante("autor_quitar")
    context.usuario_actual = _crear_perfil_estudiante("usuario_quitar")
    context.apunte = _crear_apunte(context.autor_apunte, note)
    context.servicio_guardados.guardar(context.usuario_actual, context.apunte)
    context.autor_apunte.refresh_from_db()
    context.prestigio_antes_de_quitar = context.autor_apunte.puntos_prestigio
    assert context.servicio_guardados.esta_guardado(context.usuario_actual, context.apunte)


@step('el usuario quita el apunte "{note}" de sus guardados')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados.quitar(context.usuario_actual, context.apunte)


@step("el sistema elimina el registro de guardado asociado al usuario")
def step_impl(context: behave.runner.Context):
    assert not context.servicio_guardados.esta_guardado(context.usuario_actual, context.apunte)


@step('el prestigio del autor del apunte "{note}" disminuye en "{points:d}" puntos')
def step_impl(context: behave.runner.Context, note: str, points: int):
    context.autor_apunte.refresh_from_db()
    assert context.autor_apunte.puntos_prestigio == context.prestigio_antes_de_quitar - points


@step('que el apunte "{note}" tiene {users:d} usuarios que lo guardaron')
def step_impl(context: behave.runner.Context, note: str, users: int):
    context.servicio_guardados = servicio_guardado_apuntes()
    context.autor_apunte = _crear_perfil_estudiante("autor_eliminacion")
    context.apunte = _crear_apunte(context.autor_apunte, note)
    context.usuarios_guardadores = []
    for index in range(users):
        usuario = _crear_perfil_estudiante(f"guardador_{index}")
        context.usuarios_guardadores.append(usuario)
        context.servicio_guardados.guardar(usuario, context.apunte)
    assert context.servicio_guardados.total_guardados(context.apunte) == users


@step('el autor elimina el apunte "{note}" de la plataforma')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados.eliminar_apunte(context.apunte, autor=context.autor_apunte)


@step(
    "el sistema conserva el registro de guardado en la lista de cada uno de los {users:d} usuarios"
)
def step_impl(context: behave.runner.Context, users: int):
    assert context.servicio_guardados.total_guardados(context.apunte) == users


@step('el estado del apunte "{note}" cambia a "{status}"')
def step_impl(context: behave.runner.Context, note: str, status: str):
    estado = context.servicio_guardados.estado_de(context.apunte)
    estado_actual = "no disponible" if not estado.disponible else "disponible"
    assert _normalizar(estado_actual) == _normalizar(status)


@step('el acceso al contenido del apunte "{note}" queda restringido')
def step_impl(context: behave.runner.Context, note: str):
    estado = context.servicio_guardados.estado_de(context.apunte)
    assert estado.acceso_restringido


# -----------------------------------------------------------------------------
# Pasos nuevos: el autor no puede guardar su propio apunte
# -----------------------------------------------------------------------------

@step('que el autor tiene el apunte "{note}"')
def step_impl(context: behave.runner.Context, note: str):
    context.servicio_guardados = servicio_guardado_apuntes()
    # Crear un autor y usarlo también como usuario actual
    context.autor_apunte = _crear_perfil_estudiante("autor_propio")
    context.usuario_actual = context.autor_apunte
    context.apunte = _crear_apunte(context.autor_apunte, note)


@step('el autor intenta guardar el apunte "{note}"')
def step_impl(context: behave.runner.Context, note: str):
    # Intentar guardar y capturar la excepción
    try:
        context.servicio_guardados.guardar(context.usuario_actual, context.apunte)
        context.exception = None
    except Exception as e:
        context.exception = e


@step('el sistema impide la acción')
def step_impl(context: behave.runner.Context):
    from django.core.exceptions import PermissionDenied

    assert hasattr(context, 'exception') and isinstance(context.exception, PermissionDenied)

