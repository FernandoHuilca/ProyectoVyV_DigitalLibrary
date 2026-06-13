import behave.runner
from behave import *

use_step_matcher("parse")


@step("que existe un publicador autenticado")
def step_impl(context: behave.runner.Context):
    context.publicador_actual = Publicador("Fernando")
    context.publicador_actual.estado_logueado(True)
    assert context.publicador_actual.logueado()


@step("sube un apunte en formato PDF")
def step_impl(context: behave.runner.Context):
    context.cant_publicaciones = context.publicador_actual.get_numero_publicaciones()
    context.apunte = Apunte_PDF()
    context.apunte.agregar_contenido("apunte.txt")
    context.servicio_publicacion.publicar(
        context.publicador_actual,
        context.apunte
    )



@step("el número de sus publicaciones aumenta en 1")
def step_impl(context: behave.runner.Context):
    context.cant_publicaciones_aumentadas = context.publicador_actual.get_numero_publicaciones()
    assert context.cant_publicaciones_aumentadas == context.cant_publicaciones + 1