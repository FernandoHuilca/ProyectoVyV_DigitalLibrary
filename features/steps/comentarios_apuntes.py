import os
import time
from uuid import uuid4

import behave.runner
import django
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from modulo_apuntes.models import Apunte, Comentario
from modulo_apuntes.services import ServicioComentario
from modulo_usuarios.models import PerfilEstudiante

use_step_matcher("parse")


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
    if not hasattr(context, "comentarios"):
        context.comentarios = {}
    if not hasattr(context, "servicio_comentario"):
        context.servicio_comentario = ServicioComentario()


def _obtener_perfil(context: behave.runner.Context, alias: str) -> PerfilEstudiante:
    if alias not in context.usuarios:
        context.usuarios[alias] = _crear_perfil_estudiante(alias)
    return context.usuarios[alias]


def _obtener_apunte(context: behave.runner.Context, alias: str) -> Apunte:
    if alias not in context.apuntes:
        # Si no existe, lo crea asignándole un autor ficticio por defecto
        autor_ficticio = _obtener_perfil(context, f"autor_de_{alias}")
        context.apuntes[alias] = _crear_apunte(autor_ficticio, alias)
    return context.apuntes[alias]


# ==============================================================================
# ANTECEDENTES Y CONFIGURACIÓN DE CONTEXTO
# ==============================================================================

@step('que "{usuario_alias}" tiene un comentario principal en un apunte')
def step_impl(context: behave.runner.Context, usuario_alias: str, **kwargs):
    _asegurar_contexto(context)
    autor_comentario = _obtener_perfil(context, usuario_alias)
    apunte = _obtener_apunte(context, "Apunte de Prueba")

    comentario = context.servicio_comentario.crear_comentario(
        autor=autor_comentario,
        apunte=apunte,
        contenido="Este es el comentario principal de prueba"
    )
    context.comentarios[usuario_alias] = comentario


@step('"{usuario_alias}" escribió una respuesta al comentario de "{parent_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, parent_alias: str, **kwargs):
    _asegurar_contexto(context)
    autor_respuesta = _obtener_perfil(context, usuario_alias)
    comentario_padre = context.comentarios[parent_alias]

    comentario_respuesta = context.servicio_comentario.crear_comentario(
        autor=autor_respuesta,
        apunte=comentario_padre.apunte,
        contenido="Esta es una respuesta intermedia",
        parent=comentario_padre
    )
    context.comentarios[usuario_alias] = comentario_respuesta


@step('que "{autor_alias}" tiene un apunte "{apunte_titulo}"')
def step_impl(context: behave.runner.Context, autor_alias: str, apunte_titulo: str, **kwargs):
    _asegurar_contexto(context)
    autor = _obtener_perfil(context, autor_alias)
    apunte = _crear_apunte(autor, apunte_titulo)
    context.apuntes[apunte_titulo] = apunte


@step('"{usuario_alias}" tiene inicialmente {puntos:d} puntos de prestigio')
@step('que "{usuario_alias}" tiene inicialmente {puntos:d} puntos de prestigio')
def step_impl(context: behave.runner.Context, usuario_alias: str, puntos: int, **kwargs):
    _asegurar_contexto(context)
    usuario = _obtener_perfil(context, usuario_alias)
    usuario.puntos_prestigio = puntos
    usuario.save(update_fields=["puntos_prestigio"])


@step('que "{usuario_alias}" tiene un comentario en el apunte de "{autor_alias}"')
@step('que "{usuario_alias}" tiene un comentario principal en el apunte de "{autor_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, autor_alias: str, **kwargs):
    _asegurar_contexto(context)
    autor_apunte = _obtener_perfil(context, autor_alias)
    apunte = _crear_apunte(autor_apunte, f"Apunte de {autor_alias}")
    context.apuntes[apunte.titulo] = apunte

    usuario_comenta = _obtener_perfil(context, usuario_alias)
    comentario = context.servicio_comentario.crear_comentario(
        autor=usuario_comenta,
        apunte=apunte,
        contenido="Comentario para recibir reaccion o respuesta"
    )
    context.comentarios[usuario_alias] = comentario


@step('que "{usuario_alias}" tiene un comentario publicado con el texto "{texto_inicial}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, texto_inicial: str, **kwargs):
    _asegurar_contexto(context)
    usuario = _obtener_perfil(context, usuario_alias)
    apunte = _obtener_apunte(context, "Apunte de Edicion")

    comentario = context.servicio_comentario.crear_comentario(
        autor=usuario,
        apunte=apunte,
        contenido=texto_inicial
    )
    context.comentarios[usuario_alias] = comentario


@step('el comentario no registra ninguna marca de edición')
def step_impl(context: behave.runner.Context, **kwargs):
    # En la base de datos de pruebas se asienta la fecha de creacion y modificacion exactamente igual
    comentario = list(context.comentarios.values())[-1]
    assert comentario.creado_en == comentario.editado_en


@step('"{autor_alias}" (autor del apunte) tiene inicialmente {puntos:d} puntos de prestigio')
def step_impl(context: behave.runner.Context, autor_alias: str, puntos: int, **kwargs):
    _asegurar_contexto(context)
    autor_apunte = _obtener_perfil(context, autor_alias)
    autor_apunte.puntos_prestigio = puntos
    autor_apunte.save(update_fields=["puntos_prestigio"])


# ==============================================================================
# ACCIONES (CUANDO / WHEN)
# ==============================================================================

@step('"{usuario_alias}" responde a la respuesta de "{target_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, target_alias: str, **kwargs):
    autor = _obtener_perfil(context, usuario_alias)
    comentario_al_que_responde = context.comentarios[target_alias]

    nueva_respuesta = context.servicio_comentario.crear_comentario(
        autor=autor,
        apunte=comentario_al_que_responde.apunte,
        contenido=f"Respuesta de {usuario_alias} a {target_alias}",
        parent=comentario_al_que_responde
    )
    context.comentarios[usuario_alias] = nueva_respuesta


@step('el usuario "{usuario_alias}" escribe un comentario principal en "{apunte_titulo}"')
@step('"{usuario_alias}" escribe un comentario principal en su propio apunte "{apunte_titulo}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, apunte_titulo: str, **kwargs):
    autor_comentario = _obtener_perfil(context, usuario_alias)
    apunte = context.apuntes[apunte_titulo]

    comentario = context.servicio_comentario.crear_comentario(
        autor=autor_comentario,
        apunte=apunte,
        contenido="Este es un nuevo comentario principal de prueba"
    )
    context.comentarios[usuario_alias] = comentario


@step('el usuario "{usuario_alias}" responde al comentario de "{parent_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, parent_alias: str, **kwargs):
    autor_respuesta = _obtener_perfil(context, usuario_alias)
    comentario_padre = context.comentarios[parent_alias]

    comentario_respuesta = context.servicio_comentario.crear_comentario(
        autor=autor_respuesta,
        apunte=comentario_padre.apunte,
        contenido=f"Respuesta de {usuario_alias}",
        parent=comentario_padre
    )
    context.comentarios[usuario_alias] = comentario_respuesta


@step('"{autor_alias}" reacciona con un corazón al comentario de "{usuario_alias}"')
def step_impl(context: behave.runner.Context, autor_alias: str, usuario_alias: str, **kwargs):
    creador = _obtener_perfil(context, autor_alias)
    comentario = context.comentarios[usuario_alias]
    context.servicio_comentario.dar_corazon(usuario_solicitante=creador, comentario=comentario)


@step('"{autor_alias}" escribe una respuesta al comentario de "{usuario_alias}"')
def step_impl(context: behave.runner.Context, autor_alias: str, usuario_alias: str, **kwargs):
    autor = _obtener_perfil(context, autor_alias)
    comentario_padre = context.comentarios[usuario_alias]

    comentario_respuesta = context.servicio_comentario.crear_comentario(
        autor=autor,
        apunte=comentario_padre.apunte,
        contenido="Respuesta del mismísimo creador",
        parent=comentario_padre
    )
    context.comentarios[autor_alias] = comentario_respuesta


@step('"{usuario_alias}" edita el texto de su comentario a "{nuevo_texto}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, nuevo_texto: str, **kwargs):
    usuario = _obtener_perfil(context, usuario_alias)
    comentario = context.comentarios[usuario_alias]

    # Agregamos una pausa milimétrica imperceptible para asegurar que la marca
    # temporal del sistema de archivos o base de datos cambie entre creación y edición.
    time.sleep(0.01)

    context.servicio_comment_editado = context.servicio_comentario.editar_comentario(
        usuario_solicitante=usuario,
        comentario=comentario,
        nuevo_contenido=nuevo_texto
    )


# ==============================================================================
# VERIFICACIONES (ENTONCES / THEN)
# ==============================================================================

@step('la respuesta de "{usuario_alias}" se registra bajo el comentario principal de "{parent_alias}"')
def step_impl(context: behave.runner.Context, usuario_alias: str, parent_alias: str, **kwargs):
    respuesta_d = context.comentarios[usuario_alias]
    comentario_principal = context.comentarios[parent_alias]

    assert respuesta_d.parent == comentario_principal
    assert respuesta_d.parent.parent is None  # Aseguramos que el padre sea estrictamente nivel 1


@step('el prestigio de "{usuario_alias}" debe ser de {puntos_final:d} puntos')
@step('el prestigio de "{usuario_alias}" debe mantenerse en {puntos_final:d} puntos')
@step('el prestigio de "{usuario_alias}" debe incrementarse a {puntos_final:d} puntos')
def step_impl(context: behave.runner.Context, usuario_alias: str, puntos_final: int, **kwargs):
    usuario = _obtener_perfil(context, usuario_alias)
    usuario.refresh_from_db()
    assert usuario.puntos_prestigio == puntos_final


@step('el comentario debe actualizar su texto en la base de datos')
def step_impl(context: behave.runner.Context, **kwargs):
    comentario = list(context.comentarios.values())[-1]
    comentario.refresh_from_db()
    assert comentario.contenido == context.servicio_comment_editado.contenido


@step('el comentario debe quedar marcado como editado')
def step_impl(context: behave.runner.Context, **kwargs):
    comentario = list(context.comentarios.values())[-1]
    comentario.refresh_from_db()

    # Si el tiempo de edición es mayor al de creación, está correctamente editado
    assert comentario.editado_en > comentario.creado_en