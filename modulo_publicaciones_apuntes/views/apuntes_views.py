from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from modulo_publicaciones_apuntes.models import Apunte


# El decorador @login_required es el guardia de seguridad.
# Si alguien sin sesión intenta entrar aquí, lo manda de regreso al /login/
@login_required
def lista_apuntes(request):
    # Consultamos la base de datos.
    # .all() trae todos los registros.
    # .order_by('-fecha_creacion') los ordena del más reciente al más antiguo.
    apuntes_bd = Apunte.objects.all().order_by('-fecha_creacion')

    # Empaquetamos los datos en un diccionario para enviarlos a la plantilla
    contexto = {
        'apuntes': apuntes_bd
    }

    # Le decimos a Django que renderice el archivo HTML pasándole el contexto
    return render(request, 'publicaciones/lista_apuntes.html', contexto)