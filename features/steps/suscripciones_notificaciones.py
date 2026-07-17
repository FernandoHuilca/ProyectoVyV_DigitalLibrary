import os
from uuid import uuid4

import behave.runner
import django
from behave import step

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from modulo_apuntes.models import Apunte, ApunteGuardado
from modulo_notificaciones.models import Notificacion
from modulo_notificaciones.signals import apunte_calificado_signal
from modulo_usuarios.services.servicio_suscripciones import ServicioSuscripciones

def _crear_usuario_con_perfil(nombre: str):
    username_unico = f"{nombre}_{uuid4().hex[:8]}"
    usuario = User.objects.create_user(username=username_unico, first_name=nombre)
    return usuario, usuario.perfil


def _crear_apunte(autor_perfil, titulo: str, estado: str = "BORRADOR"):
    contenido = SimpleUploadedFile(
        name=f"apunte_{uuid4().hex[:8]}.pdf",
        content=b"%PDF-1.4 test",
        content_type="application/pdf",
    )
    return Apunte.objects.create(
        titulo=titulo,
        descripcion=f"Apunte de {titulo}",
        contenido=contenido,
        autor=autor_perfil,
        estado=estado,
    )


@step('que existe un estudiante consumidor autenticado "{nombre}"')
def step_impl(context: behave.runner.Context, nombre: str):
    usuario, perfil = _crear_usuario_con_perfil(nombre)
    context.usuarios = {nombre: usuario}
    context.perfiles = {nombre: perfil}
    context.servicio_suscripciones = ServicioSuscripciones()


@step('existe el perfil público de la publicadora "{nombre}"')
def step_impl(context: behave.runner.Context, nombre: str):
    usuario, perfil = _crear_usuario_con_perfil(nombre)
    context.usuarios[nombre] = usuario
    context.perfiles[nombre] = perfil


@step('"{consumidor}" no está suscrito a "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    assert not context.servicio_suscripciones.esta_suscrito(
        context.perfiles[consumidor],
        context.perfiles[publicador],
    )


@step('"{consumidor}" se suscribe al perfil de "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    context.suscriptores_antes = context.servicio_suscripciones.total_suscriptores(
        context.perfiles[publicador]
    )
    context.servicio_suscripciones.suscribir(
        context.perfiles[consumidor],
        context.perfiles[publicador],
    )


@step('"{consumidor}" debe figurar en la lista de suscriptores de "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    assert context.perfiles[publicador].suscriptores.filter(
        pk=context.perfiles[consumidor].pk
    ).exists()


@step('el contador de suscriptores de "{publicador}" debe incrementarse en {valor:d}')
def step_impl(context: behave.runner.Context, publicador: str, valor: int):
    total_actual = context.servicio_suscripciones.total_suscriptores(context.perfiles[publicador])
    assert total_actual == context.suscriptores_antes + valor


@step('"{consumidor}" está suscrito a la publicadora "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    if consumidor not in context.perfiles:
        usuario, perfil = _crear_usuario_con_perfil(consumidor)
        context.usuarios[consumidor] = usuario
        context.perfiles[consumidor] = perfil
    if publicador not in context.perfiles:
        usuario, perfil = _crear_usuario_con_perfil(publicador)
        context.usuarios[publicador] = usuario
        context.perfiles[publicador] = perfil

    context.servicio_suscripciones.suscribir(
        context.perfiles[consumidor],
        context.perfiles[publicador],
    )
    assert context.servicio_suscripciones.esta_suscrito(
        context.perfiles[consumidor],
        context.perfiles[publicador],
    )


@step('"{consumidor}" cancela su suscripción al perfil de "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    context.suscriptores_antes = context.servicio_suscripciones.total_suscriptores(
        context.perfiles[publicador]
    )
    context.servicio_suscripciones.cancelar_suscripcion(
        context.perfiles[consumidor],
        context.perfiles[publicador],
    )


@step('"{consumidor}" ya no debe figurar en la lista de suscriptores de "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    assert not context.perfiles[publicador].suscriptores.filter(
        pk=context.perfiles[consumidor].pk
    ).exists()


@step('el contador de suscriptores de "{publicador}" debe disminuir en {valor:d}')
def step_impl(context: behave.runner.Context, publicador: str, valor: int):
    total_actual = context.servicio_suscripciones.total_suscriptores(context.perfiles[publicador])
    assert total_actual == context.suscriptores_antes - valor


@step('que el consumidor "{consumidor}" está suscrito a la publicadora "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    usuario_consumidor, perfil_consumidor = _crear_usuario_con_perfil(consumidor)
    usuario_publicador, perfil_publicador = _crear_usuario_con_perfil(publicador)

    context.usuarios = {consumidor: usuario_consumidor, publicador: usuario_publicador}
    context.perfiles = {consumidor: perfil_consumidor, publicador: perfil_publicador}
    context.servicio_suscripciones = ServicioSuscripciones()
    context.servicio_suscripciones.suscribir(perfil_consumidor, perfil_publicador)


@step('"{publicador}" publica un nuevo apunte titulado "{titulo}"')
def step_impl(context: behave.runner.Context, publicador: str, titulo: str):
    context.apunte_publicado = _crear_apunte(
        context.perfiles[publicador],
        titulo,
        estado="PUBLICADO",
    )


@step('"{consumidor}" debe recibir una notificación en la plataforma')
def step_impl(context: behave.runner.Context, consumidor: str):
    context.notificaciones_destino = Notificacion.objects.filter(
        receptor=context.usuarios[consumidor]
    ).order_by("-creado_en")
    assert context.notificaciones_destino.exists()


@step('la notificación debe contener el texto "{texto}"')
def step_impl(context: behave.runner.Context, texto: str):
    assert context.notificaciones_destino.filter(mensaje=texto).exists()


@step("la notificación debe incluir el enlace directo al apunte")
def step_impl(context: behave.runner.Context):
    assert context.notificaciones_destino.filter(
        enlace=f"/apunte/{context.apunte_publicado.pk}/"
    ).exists()


@step('que la publicadora "{publicador}" tiene publicado un apunte de "{titulo}"')
def step_impl(context: behave.runner.Context, publicador: str, titulo: str):
    usuario_publicador, perfil_publicador = _crear_usuario_con_perfil(publicador)
    context.usuarios = {publicador: usuario_publicador}
    context.perfiles = {publicador: perfil_publicador}
    context.apunte_publicado = _crear_apunte(perfil_publicador, titulo)


@step('el estudiante "{nombre}" no es el autor del apunte')
def step_impl(context: behave.runner.Context, nombre: str):
    usuario_estudiante, perfil_estudiante = _crear_usuario_con_perfil(nombre)
    context.usuarios[nombre] = usuario_estudiante
    context.perfiles[nombre] = perfil_estudiante
    assert context.apunte_publicado.autor_id != perfil_estudiante.id


@step('"{nombre}" califica el apunte "{titulo}" como "útil"')
def step_impl(context: behave.runner.Context, nombre: str, titulo: str):
    assert context.apunte_publicado.titulo == titulo
    apunte_calificado_signal.send(
        sender=Apunte,
        apunte=context.apunte_publicado,
        calificador=context.perfiles[nombre],
        tipo_calificacion="util",
    )


@step('la notificación debe indicar que su apunte "{titulo}" recibió una nueva calificación')
def step_impl(context: behave.runner.Context, titulo: str):
    assert context.notificaciones_destino.filter(
        mensaje=f'Tu apunte "{titulo}" recibio una nueva calificacion util.'
    ).exists()


@step('el estudiante "{nombre}" descarga el apunte "{titulo}"')
def step_impl(context: behave.runner.Context, nombre: str, titulo: str):
    if nombre not in context.perfiles:
        usuario_estudiante, perfil_estudiante = _crear_usuario_con_perfil(nombre)
        context.usuarios[nombre] = usuario_estudiante
        context.perfiles[nombre] = perfil_estudiante

    assert context.apunte_publicado.titulo == titulo
    ApunteGuardado.objects.create(
        usuario=context.perfiles[nombre],
        apunte=context.apunte_publicado,
    )


@step('la notificación debe indicar que su apunte "{titulo}" fue descargado')
def step_impl(context: behave.runner.Context, titulo: str):
    assert context.notificaciones_destino.filter(
        mensaje=f'Tu apunte "{titulo}" fue descargado.'
    ).exists()


@step('que el consumidor "{consumidor}" no está suscrito al publicador "{publicador}"')
def step_impl(context: behave.runner.Context, consumidor: str, publicador: str):
    usuario_consumidor, perfil_consumidor = _crear_usuario_con_perfil(consumidor)
    usuario_publicador, perfil_publicador = _crear_usuario_con_perfil(publicador)

    context.usuarios = {consumidor: usuario_consumidor, publicador: usuario_publicador}
    context.perfiles = {consumidor: perfil_consumidor, publicador: perfil_publicador}
    context.servicio_suscripciones = ServicioSuscripciones()

    assert not context.servicio_suscripciones.esta_suscrito(
        perfil_consumidor,
        perfil_publicador,
    )


@step('"{consumidor}" no debe recibir ninguna notificación de la plataforma')
def step_impl(context: behave.runner.Context, consumidor: str):
    assert not Notificacion.objects.filter(receptor=context.usuarios[consumidor]).exists()




