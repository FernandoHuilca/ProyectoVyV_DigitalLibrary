from django.urls import path
from django.contrib.auth.views import LoginView
from .views import apuntes_views

app_name = 'publicaciones'

urlpatterns = [
    # Usamos apuntes_views para mapear cada una de las rutas
    path('', apuntes_views.lista_apuntes, name='lista_apuntes'),
    path('apunte/<int:pk>/', apuntes_views.vista_apunte, name='vista_apunte'),
    path('apunte/<int:pk>/guardar/', apuntes_views.guardar_apunte, name='guardar_apunte'),
    path('mi-biblioteca/', apuntes_views.mi_biblioteca, name='mi_biblioteca'),
]
