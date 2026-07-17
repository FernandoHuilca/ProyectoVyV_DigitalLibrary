import os
from uuid import uuid4

import behave.runner
import django
from behave import step

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from modulo_apuntes.models import Apunte, ApunteGuardado, Calificacion
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


@step('"{nombre}" da like útil al apunte "{titulo}"')
def step_impl(context: behave.runner.Context, nombre: str, titulo: str):
    assert context.apunte_publicado.titulo == titulo
    if nombre not in context.perfiles:
        usuario_estudiante, perfil_estudiante = _crear_usuario_con_perfil(nombre)
        context.usuarios[nombre] = usuario_estudiante
        context.perfiles[nombre] = perfil_estudiante

    Calificacion.objects.update_or_create(
        usuario=context.perfiles[nombre],
        apunte=context.apunte_publicado,
        defaults={"tipo": Calificacion.TIPO_UTIL},
    )
    apunte_calificado_signal.send(
        sender=Apunte,
        apunte=context.apunte_publicado,
        calificador=context.perfiles[nombre],
        tipo_calificacion="util",
    )


@step('el apunte de "{titulo}" tiene {total:d} likes útiles')
def step_impl(context: behave.runner.Context, titulo: str, total: int):
    assert context.apunte_publicado.titulo == titulo

    for indice in range(total):
        usuario_like, perfil_like = _crear_usuario_con_perfil(f"Likeador{indice}")
        context.usuarios[f"Likeador{indice}"] = usuario_like
        context.perfiles[f"Likeador{indice}"] = perfil_like
        Calificacion.objects.update_or_create(
            usuario=perfil_like,
            apunte=context.apunte_publicado,
            defaults={"tipo": Calificacion.TIPO_UTIL},
        )


@step('la notificación debe indicar que su apunte "{titulo}" alcanzó los {total:d} likes')
def step_impl(context: behave.runner.Context, titulo: str, total: int):
    assert context.notificaciones_destino.filter(
        mensaje=f'Tu apunte "{titulo}" ha alcanzado los {total} likes.'
    ).exists()


@step('el estudiante "{nombre}" guarda el apunte "{titulo}" en su biblioteca')
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


@step('la notificación debe indicar que su apunte "{titulo}" fue guardado en biblioteca')
def step_impl(context: behave.runner.Context, titulo: str):
    assert context.notificaciones_destino.filter(
        mensaje=f'Tu apunte "{titulo}" fue guardado en la biblioteca de un estudiante.'
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


@step('que la publicadora "{publicador}" tiene {suscriptores_previos:d} suscriptores y "{puntos_iniciales}" puntos de prestigio')
def step_impl(context: behave.runner.Context, publicador: str, suscriptores_previos: int, puntos_iniciales: str):
    usuario_publicador, perfil_publicador = _crear_usuario_con_perfil(publicador)
    context.usuarios = {publicador: usuario_publicador}
    context.perfiles = {publicador: perfil_publicador}
    context.servicio_suscripciones = ServicioSuscripciones()

    for indice in range(suscriptores_previos):
        usuario_suscriptor, perfil_suscriptor = _crear_usuario_con_perfil(f"SuscriptorPrevio{indice}")
        context.usuarios[f"SuscriptorPrevio{indice}"] = usuario_suscriptor
        context.perfiles[f"SuscriptorPrevio{indice}"] = perfil_suscriptor
        context.servicio_suscripciones.suscribir(perfil_suscriptor, perfil_publicador)

    puntos_base = int(puntos_iniciales)
    perfil_publicador.puntos_prestigio = puntos_base
    perfil_publicador.save(update_fields=["puntos_prestigio"])
    context.puntos_antes_hito = puntos_base


@step('un nuevo estudiante se suscribe al perfil de "{publicador}"')
def step_impl(context: behave.runner.Context, publicador: str):
    usuario_nuevo, perfil_nuevo = _crear_usuario_con_perfil("NuevoSuscriptor")
    context.usuarios["NuevoSuscriptor"] = usuario_nuevo
    context.perfiles["NuevoSuscriptor"] = perfil_nuevo

    context.servicio_suscripciones.suscribir(
        perfil_nuevo,
        context.perfiles[publicador],
    )


@step('"{publicador}" debe tener "{suscriptores_finales}" suscriptores')
def step_impl(context: behave.runner.Context, publicador: str, suscriptores_finales: str):
    total_actual = context.perfiles[publicador].suscriptores.count()
    assert total_actual == int(suscriptores_finales)


@step('sus puntos de prestigio deben incrementarse en {puntos:d} puntos')
def step_impl(context: behave.runner.Context, puntos: int):
    perfil_publicador = context.perfiles["Ana"]
    perfil_publicador.refresh_from_db(fields=["puntos_prestigio"])
    context.puntos_despues_hito = perfil_publicador.puntos_prestigio
    assert context.puntos_despues_hito - context.puntos_antes_hito == puntos


@step('su total de puntos de prestigio debe ser "{puntos_totales}"')
def step_impl(context: behave.runner.Context, puntos_totales: str):
    assert context.puntos_despues_hito == int(puntos_totales)




