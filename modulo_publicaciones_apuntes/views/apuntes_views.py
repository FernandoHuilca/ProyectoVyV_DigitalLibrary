from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from modulo_publicaciones_apuntes.models import Apunte
from modulo_usuarios.models import PerfilEstudiante


# El decorador @login_required es el guardia de seguridad.
# Si alguien sin sesión intenta entrar aquí, lo manda de regreso al /login/
@login_required
def lista_apuntes(request):
    # Consultamos la base de datos.
    # .all() trae todos los registros.
    # .order_by('-fecha_creacion') los ordena del más reciente al más antiguo.
    apuntes_bd = Apunte.objects.all().order_by('-fecha_creacion')


    # Añadimos los publicadores destacados del ranking

    top_publicadores = (
        PerfilEstudiante.objects
        .select_related("usuario")
        .order_by("-puntos_prestigio") [:10]
    )
    # Empaquetamos los datos en un diccionario para enviarlos a la plantilla
    contexto = {
        'apuntes': apuntes_bd,
        'top_publicadores': top_publicadores
    }

    # Le decimos a Django que renderice el archivo HTML pasándole el contexto
    return render(request, 'publicaciones/lista_apuntes.html', contexto)


@login_required
def vista_apunte(request, pk):
    apunte = get_object_or_404(Apunte, pk=pk)

    contexto = {
        'apunte': apunte,
    }

    return render(request, 'publicaciones/vista_apunte.html', contexto)