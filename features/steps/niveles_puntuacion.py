import os
from uuid import uuid4

import behave.runner
import django
from behave import step, use_step_matcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_usuarios.models import PerfilEstudiante

use_step_matcher("parse")


def _normalizar_rango(texto: str) -> str:
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


@step("que un estudiante se registra por primera vez")
def step_impl(context: behave.runner.Context):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_registro")


@step("se cree la cuenta")
def step_impl(context: behave.runner.Context):
    context.perfil_estudiante = context.servicio_niveles.registrar_nuevo_estudiante(
        context.perfil_estudiante
    )


@step("su puntaje de prestigio es {prestige:d}")
def step_impl(context: behave.runner.Context, prestige: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestige


@step('el sistema registra en la cuenta el rango de "{rank}"')
def step_impl(context: behave.runner.Context, rank: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rank)


@step('un estudiante de rango "{rango_inicial}" y que cuenta con prestigio de {prestigio_inicial:d} puntos')
def step_impl(context: behave.runner.Context, rango_inicial: str, prestigio_inicial: int):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_ascenso")
    context.perfil_estudiante.rango = rango_inicial
    context.perfil_estudiante.puntos_prestigio = prestigio_inicial
    context.perfil_estudiante.save(update_fields=["rango", "puntos_prestigio"])


@step('el siguiente rango "{rango_final}" requiere un mínimo de {umbral:d} puntos')
def step_impl(context: behave.runner.Context, rango_final: str, umbral: int):
    context.threshold_esperado = umbral
    context.siguiente_rango_esperado = rango_final
    rango_calculado = context.servicio_niveles.rango_para_prestigio(umbral)
    assert _normalizar_rango(rango_calculado) == _normalizar_rango(rango_final)


@step("el sistema procesa un incremento de {incremento:d} puntos de prestigio")
def step_impl(context: behave.runner.Context, incremento: int):
    context.perfil_estudiante = context.servicio_niveles.incrementar_prestigio(
        context.perfil_estudiante, incremento
    )


@step("el sistema actualiza el puntaje acumulado a {prestige:d} puntos de prestigio")
def step_impl(context: behave.runner.Context, prestige: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestige


@step('el rango del estudiante se actualiza automáticamente a "{rango_final}"')
def step_impl(context: behave.runner.Context, rango_final: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rango_final)

@step('un estudiante con el rango "{rango_inicial}" y un prestigio de {prestigio_inicial:d} puntos')
def step_impl(context: behave.runner.Context, rango_inicial: str, prestigio_inicial: int):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_descenso")
    context.perfil_estudiante.rango = rango_inicial
    context.perfil_estudiante.puntos_prestigio = prestigio_inicial
    context.perfil_estudiante.save(update_fields=["rango", "puntos_prestigio"])


@step("el sistema registra una pérdida de {perdida:d} puntos de prestigio")
def step_impl(context: behave.runner.Context, perdida: int):
    context.perfil_estudiante = context.servicio_niveles.disminuir_prestigio(
        context.perfil_estudiante, perdida
    )


@step("el prestigio acumulado del estudiante es de {prestigio_final:d} puntos")
def step_impl(context: behave.runner.Context, prestigio_final: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestigio_final


@step('el sistema degrada automáticamente el rango del estudiante a "{rank}".')
def step_impl(context: behave.runner.Context, rank: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rank)


