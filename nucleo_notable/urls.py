from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Al dejar el string vacío (''), le decimos a Django:
    # "Cualquier ruta que no sea admin/, delega su resolución a la app"
    path('', include('modulo_publicaciones_apuntes.urls')),
]