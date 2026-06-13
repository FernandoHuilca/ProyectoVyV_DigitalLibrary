from django.urls import path
from django.contrib.auth.views import LoginView

urlpatterns = [
    # Usamos la vista nativa LoginView y le indicamos la ruta de nuestra futura plantilla
    path('login/', LoginView.as_view(template_name='publicaciones/login.html'), name='login'),
]