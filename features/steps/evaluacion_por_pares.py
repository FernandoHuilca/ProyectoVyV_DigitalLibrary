import os
from uuid import uuid4

import django
import behave.runner
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client

from modulo_apuntes.models import Apunte, SolicitudRevision

use_step_matcher("parse")

PASSWORD = "bdd-test-password"


def _crear_usuario(nombre_base):
    username = f"{nombre_base}_{uuid4().hex[:8]}"
    return User.objects.create_user(username=username, password=PASSWORD)


def _archivo_pdf_prueba():
    return SimpleUploadedFile(
        "apunte_prueba.pdf",
        b"%PDF-1.4\n%Test PDF\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF",
        content_type="application/pdf",
    )


# ─────────────────────────────────────────────────────────────────────
# Escenario 1: El autor envía un apunte a revisión
# ─────────────────────────────────────────────────────────────────────

@step('que tengo un apunte en estado "Borrador"')
def step_impl(context: behave.runner.Context):
    context.client = Client()
    context.autor_user = _crear_usuario("Autor")
    context.client.login(username=context.autor_user.username, password=PASSWORD)

    context.apunte_prueba = Apunte.objects.create(
        titulo="Apunte de prueba",
        descripcion="Descripción de prueba",
        contenido=_archivo_pdf_prueba(),
        autor=context.autor_user.perfil,
        estado="BORRADOR",
    )


@step("selecciono a un estudiante como revisor y envío el apunte a revisión")
def step_impl(context: behave.runner.Context):
    context.revisor_user = _crear_usuario("Revisor")

    context.response = context.client.post(
        reverse("apuntes:lista_mis_apuntes"),
        data={
            "apunte_id": context.apunte_prueba.pk,
            "titulo": context.apunte_prueba.titulo,
            "descripcion": context.apunte_prueba.descripcion,
            "contenido": _archivo_pdf_prueba(),
            "accion": "enviar_revision",
            "revisor": context.revisor_user.pk,
            "comentario_autor": "Por favor revisa la sección 2",
        },
        follow=True,
    )


@step('el apunte debe cambiar a estado "En revisión"')
def step_impl(context: behave.runner.Context):
    context.apunte_prueba.refresh_from_db()
    form_errors = context.response.context["form"].errors if context.response.context and "form" in context.response.context else None
    assert context.apunte_prueba.estado == "EN_REVISION", (
        f"Se esperaba EN_REVISION, se obtuvo '{context.apunte_prueba.estado}'. "
        f"status={context.response.status_code}, errores de formulario={form_errors}"
    )


@step("debe crearse una solicitud de revisión pendiente para el estudiante seleccionado")
def step_impl(context: behave.runner.Context):
    existe = SolicitudRevision.objects.filter(
        apunte=context.apunte_prueba,
        revisor=context.revisor_user,
        estado="PENDIENTE",
    ).exists()
    assert existe, "No se encontró una SolicitudRevision PENDIENTE para el revisor seleccionado."


# ─────────────────────────────────────────────────────────────────────
# Escenarios 2 y 3: comparten el mismo "Dado" (En revisión enviado por otro)
# ─────────────────────────────────────────────────────────────────────

@step('que tengo un apunte en estado "En revisión" enviado por otro estudiante')
def step_impl(context: behave.runner.Context):
    context.client = Client()
    context.autor_user = _crear_usuario("Autor")

    # "Yo" en este escenario soy el revisor: quien aprueba/rechaza en los pasos siguientes.
    context.revisor_user = _crear_usuario("Revisor")
    context.client.login(username=context.revisor_user.username, password=PASSWORD)

    context.apunte_prueba = Apunte.objects.create(
        titulo="Apunte en revisión",
        descripcion="Descripción de prueba",
        contenido=_archivo_pdf_prueba(),
        autor=context.autor_user.perfil,
        estado="EN_REVISION",
    )
    context.solicitud_actual = SolicitudRevision.objects.create(
        apunte=context.apunte_prueba,
        revisor=context.revisor_user,
        estado="PENDIENTE",
        comentario_autor="Revisa por favor",
    )


@step("apruebo el apunte")
def step_impl(context: behave.runner.Context):
    context.response = context.client.post(
        reverse("apuntes:calificar_revision", args=[context.solicitud_actual.pk]),
        data={"accion": "aprobar", "comentario_revisor": "Muy buen trabajo"},
        follow=True,
    )


@step('el estado del apunte debe cambiar a "Aprobado"')
def step_impl(context: behave.runner.Context):
    context.apunte_prueba.refresh_from_db()
    assert context.apunte_prueba.estado == "APROBADO", (
        f"Se esperaba APROBADO, se obtuvo '{context.apunte_prueba.estado}'. status={context.response.status_code}"
    )


@step("mi perfil debe incrementar en 15 puntos de prestigio")
def step_impl(context: behave.runner.Context):
    context.revisor_user.perfil.refresh_from_db()
    assert context.revisor_user.perfil.puntos_prestigio == 15, (
        f"Se esperaban 15 puntos de prestigio, el perfil del revisor tiene "
        f"{context.revisor_user.perfil.puntos_prestigio}"
    )


@step("rechazo el apunte explicando los cambios necesarios")
def step_impl(context: behave.runner.Context):
    context.response = context.client.post(
        reverse("apuntes:calificar_revision", args=[context.solicitud_actual.pk]),
        data={"accion": "rechazar", "comentario_revisor": "Falta la sección de ejemplos"},
        follow=True,
    )


@step('el estado del apunte debe volver a "Borrador"')
def step_impl(context: behave.runner.Context):
    context.apunte_prueba.refresh_from_db()
    assert context.apunte_prueba.estado == "BORRADOR", (
        f"Se esperaba BORRADOR, se obtuvo '{context.apunte_prueba.estado}'. status={context.response.status_code}"
    )


# ─────────────────────────────────────────────────────────────────────
# Escenario 4: El autor publica el apunte tras ser avalado
# ─────────────────────────────────────────────────────────────────────

@step("que mi apunte ha sido aprobado por un revisor")
def step_impl(context: behave.runner.Context):
    context.client = Client()
    context.autor_user = _crear_usuario("Autor")
    context.client.login(username=context.autor_user.username, password=PASSWORD)

    context.revisor_user = _crear_usuario("Revisor")

    context.apunte_prueba = Apunte.objects.create(
        titulo="Apunte aprobado",
        descripcion="Descripción de prueba",
        contenido=_archivo_pdf_prueba(),
        autor=context.autor_user.perfil,
        estado="APROBADO",
    )
    SolicitudRevision.objects.create(
        apunte=context.apunte_prueba,
        revisor=context.revisor_user,
        estado="APROBADO",
        comentario_autor="Revisa por favor",
        comentario_revisor="Muy buen trabajo",
    )


@step('confirmo la publicación desde mi panel de "Mis apuntes"')
def step_impl(context: behave.runner.Context):
    context.response = context.client.post(
        reverse("apuntes:confirmar_publicacion", args=[context.apunte_prueba.pk]),
        follow=True,
    )


@step('el apunte debe cambiar a estado "Publicado"')
def step_impl(context: behave.runner.Context):
    context.apunte_prueba.refresh_from_db()
    assert context.apunte_prueba.estado == "PUBLICADO", (
        f"Se esperaba PUBLICADO, se obtuvo '{context.apunte_prueba.estado}'. status={context.response.status_code}"
    )