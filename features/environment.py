# features/environment.py
import os
import django
from django.test.runner import DiscoverRunner

# 1. Configurar el entorno de Django antes de cualquier acción
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleo_notable.settings")

def before_all(context):
    django.setup()
    # Inicializa el ejecutor de pruebas de Django
    context.test_runner = DiscoverRunner(interactive=False)
    # Crea una base de datos de pruebas temporal (usualmente en memoria o db_test.sqlite3)
    context.test_db_config = context.test_runner.setup_databases()

def after_all(context):
    # Destruye la base de datos de pruebas temporal al finalizar
    context.test_runner.teardown_databases(context.test_db_config)