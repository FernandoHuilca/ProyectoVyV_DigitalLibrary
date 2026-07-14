import os

import django
import behave.runner
from behave import step, use_step_matcher
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")
django.setup()

from django.contrib.auth.models import User
from uuid import uuid4

from modulo_usuarios.models import PerfilEstudiante
from modulo_prestigio.services import ServicioNivelesPrestigio

use_step_matcher("parse")


def _normalizar_rango(texto: str) -> str:
    traduccion = str.maketrans({
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u",
    })
    return texto.translate(traduccion).replace('"', "").strip().lower()


def _crear_perfil_estudiante(username: str) -> PerfilEstudiante:
    username_unico = f"{username}_{uuid4().hex[:8]}"
    user = User.objects.create_user(
        username=username_unico,
        password="bdd-test-password",
    )
    return user.perfil


# ------------------------
# Scenario 1
# ------------------------

@step("que un estudiante se registra por primera vez")
def step_student_registers(context: behave.runner.Context):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_registro")


@step("se cree la cuenta")
def step_create_account(context: behave.runner.Context):
    context.perfil_estudiante = context.servicio_niveles.registrar_nuevo_estudiante(
        context.perfil_estudiante
    )


@step("su puntaje de prestigio es {prestige:d}")
def step_student_prestige(context: behave.runner.Context, prestige: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestige


@step('el sistema registra en la cuenta el rango de "{rank}"')
def step_initial_rank(context: behave.runner.Context, rank: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rank)

# ------------------------
# Scenario 2
# ------------------------

@step("un estudiante de rango “{rank}” y que cuenta con prestigio de {prestige:d} puntos")
def step_impl(context: behave.runner.Context, rank: str, prestige: int):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_ascenso")
    context.perfil_estudiante.rango = rank
    context.perfil_estudiante.puntos_prestigio = prestige
    context.perfil_estudiante.save(update_fields=["rango", "puntos_prestigio"])


@step('el umbral establecido para el siguiente rango de "{next_rank}" es de {threshold:d} puntos')
def step_rank_threshold(context: behave.runner.Context, next_rank: str, threshold: int):
    context.threshold_esperado = threshold
    context.siguiente_rango_esperado = next_rank
    rango_calculado = context.servicio_niveles.rango_para_prestigio(threshold)
    assert _normalizar_rango(rango_calculado) == _normalizar_rango(next_rank)


@step("el sistema procese un incremento de {points:d} puntos de prestigio")
def step_add_prestige(context: behave.runner.Context, points: int):
    context.perfil_estudiante = context.servicio_niveles.incrementar_prestigio(
        context.perfil_estudiante, points
    )


@step("el sistema actualiza el puntaje acumulado a {prestige:d} puntos de prestigio")
def step_updated_prestige(context: behave.runner.Context, prestige: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestige


@step('el rango se actualiza automáticamente a "{rank}".')
def step_impl(context: behave.runner.Context, rank: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rank)


# ------------------------
# Scenario 3
# ------------------------

@step('que un estudiante posee el rango "{rank}" con un puntaje exacto de {prestige:d} puntos')
def step_student_with_rank(context: behave.runner.Context, rank: str, prestige: int):
    context.servicio_niveles = ServicioNivelesPrestigio()
    context.perfil_estudiante = _crear_perfil_estudiante("estudiante_descenso")
    context.perfil_estudiante.rango = rank
    context.perfil_estudiante.puntos_prestigio = prestige
    context.perfil_estudiante.save(update_fields=["rango", "puntos_prestigio"])


@step("el sistema registra la eliminación de un apunte con {points:d} puntos de prestigio")
def step_remove_prestige(context: behave.runner.Context, points: int):
    context.perfil_estudiante = context.servicio_niveles.disminuir_prestigio(
        context.perfil_estudiante, points
    )


@step("el sistema disminuye el puntaje total del perfil a {prestige:d} puntos de prestigio")
def step_decreased_prestige(context: behave.runner.Context, prestige: int):
    context.perfil_estudiante.refresh_from_db()
    assert context.perfil_estudiante.puntos_prestigio == prestige


@step('el sistema degrada automáticamente el rango del estudiante a "{rank}".')
def step_impl(context: behave.runner.Context, rank: str):
    context.perfil_estudiante.refresh_from_db()
    assert _normalizar_rango(context.perfil_estudiante.rango) == _normalizar_rango(rank)
