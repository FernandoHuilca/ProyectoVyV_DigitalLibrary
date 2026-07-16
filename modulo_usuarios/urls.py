from django.urls import path
from django.contrib.auth.views import LoginView
from .views import PerfilDetailView, PerfilUpdateView, RegisterView

app_name = 'modulo_usuarios'

urlpatterns = [
    # Usamos la vista nativa LoginView y le indicamos la NUEVA ruta de tu plantilla
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('perfil_usuario/', PerfilDetailView.as_view(template_name='usuarios/perfil_usuario.html'), name='mi_perfil'),
    path('perfil_usuario/<int:pk>/', PerfilDetailView.as_view(template_name='usuarios/perfil_usuario.html'), name='perfil_usuario'),
    path('registro/', RegisterView.as_view(template_name='usuarios/registro.html'), name='registro'),
    path('perfil_usuario/', PerfilDetailView.as_view(template_name='usuarios/perfil_usuario.html'), name='perfil_usuario'),
    path('perfil_usuario/<int:pk>/editar/', PerfilUpdateView.as_view(template_name='usuarios/perfil_usuario_edicion.html'),
         name='editar_perfil'),
]