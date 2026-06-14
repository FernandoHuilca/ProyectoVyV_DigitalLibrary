from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    # Nuestra nueva ruta para ver los apuntes.
    # Usamos la ruta raíz '' para que sea la página principal de la app.
    path('', views.lista_apuntes, name='lista_apuntes'),
]
