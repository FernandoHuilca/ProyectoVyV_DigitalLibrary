import behave.runner
from behave import *
from django.contrib.auth.models import User

from modulo_publicaciones_apuntes.models import PerfilEstudiante

use_step_matcher("parse")


@step("que existe un publicador autenticado")
def step_impl(context):
    # 1. Crear el usuario nativo de Django usando su método seguro
    user = User.objects.create_user(
        username="Fernando",
        password="testpassword123"
    )

    # 2. Crear el perfil asociado a ese usuario usando los nombres de los atributos
    perfil = PerfilEstudiante.objects.create(
        usuario=user,
        carrera="Software",
        semestre_actual=5
    )

    # 3. Guardar el perfil en el contexto de behave para usarlo en steps posteriores
    context.publicador_actual = perfil

    # 4. Simular la autenticación real usando el cliente de pruebas web
    # context.test.client es el navegador simulado que proporciona django-behave
    login_exitoso = context.test.client.login(
        username="Fernando",
        password="testpassword123"
    )

    # 5. La aserción valida que el framework de Django aceptó las credenciales
    assert login_exitoso is True, "El inicio de sesión falló en el test"


@step("sube un apunte en formato PDF")
def step_impl(context: behave.runner.Context):
    pass


@step("el número de sus publicaciones aumenta en 1")
def step_impl(context: behave.runner.Context):
    pass