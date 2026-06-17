from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'publicaciones'

urlpatterns = [
    # Nuestra nueva ruta para ver los apuntes.
    # Usamos la ruta raíz '' para que sea la página principal de la app.
    path('', views.lista_apuntes, name='lista_apuntes'),
    path('apunte/<int:pk>/', views.vista_apunte, name='vista_apunte'),
]
