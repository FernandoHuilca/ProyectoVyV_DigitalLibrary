from django.urls import path
from django.contrib.auth.views import LoginView
from .views import PerfilDetailView, PerfilUpdateView

app_name = 'modulo_usuarios'

urlpatterns = [
    # Usamos la vista nativa LoginView y le indicamos la NUEVA ruta de tu plantilla
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('perfil_usuario/', PerfilDetailView.as_view(template_name='usuarios/perfil_usuario.html'), name='perfil_usuario'),
    path('perfil_usuario/<int:pk>/', PerfilDetailView.as_view(template_name='usuarios/perfil_usuario_edicion.html'),
         name='perfil_usuario_edicion'),
    path('perfil_usuario/<int:pk>/editar/', PerfilUpdateView.as_view(template_name='usuarios/perfil_usuario_edicion.html'),
         name='editar_perfil'),
]