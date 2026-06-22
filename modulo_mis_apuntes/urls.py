from django.urls import path
from .views.mis_apuntes_view import mis_apuntes, eliminar_apunte

app_name = 'modulo_mis_apuntes'
urlpatterns = [
    path('', mis_apuntes, name='lista_mis_apuntes'),
path('eliminar/<int:pk>/', eliminar_apunte, name='eliminar_apunte'),
]