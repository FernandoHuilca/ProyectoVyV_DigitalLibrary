import os

import django
import behave.runner
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from uuid import uuid4

from modulo_publicaciones_apuntes.models import Apunte

use_step_matcher("parse")


@step("que existe un publicador autenticado")
def step_impl(context: behave.runner.Context):
    username = f"Fernando_{uuid4().hex[:8]}"
    user = User.objects.create_user(
        username=username,
        password="bdd-test-password",
    )

    context.publicador_actual = user.perfil
    context.publicaciones_iniciales = Apunte.objects.filter(autor=context.publicador_actual).count()

    login_exitoso = context.test.client.login(
        username=username,
        password="bdd-test-password",
    )

    assert login_exitoso is True, "El inicio de sesión falló en el test"


@step("sube un apunte en formato PDF")
def step_impl(context: behave.runner.Context):
    archivo_pdf = SimpleUploadedFile(
        "apunte_prueba.pdf",
        b"%PDF-1.4\n%Test PDF\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF",
        content_type="application/pdf",
    )

    context.apunte_subido = Apunte.objects.create(
        titulo="Apunte de prueba",
        descripcion="Documento de prueba para escenario BDD",
        contenido=archivo_pdf,
        autor=context.publicador_actual,
    )


@step("el número de sus publicaciones aumenta en 1")
def step_impl(context: behave.runner.Context):
    publicaciones_finales = Apunte.objects.filter(autor=context.publicador_actual).count()
    assert publicaciones_finales == context.publicaciones_iniciales + 1
