from django.urls import path
from django.contrib.auth.views import LoginView

urlpatterns = [
    # Usamos la vista nativa LoginView y le indicamos la NUEVA ruta de tu plantilla
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
]