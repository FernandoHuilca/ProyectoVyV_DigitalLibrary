from django.urls import path
from django.contrib.auth.views import LoginView
from .views import explorar_apuntes_views, gestion_apuntes_views

app_name = 'apuntes'

urlpatterns = [
    # Usamos apuntes_views para mapear cada una de las rutas
    path('', explorar_apuntes_views.lista_apuntes, name='lista_apuntes'),
    path('apunte/<int:pk>/', explorar_apuntes_views.vista_apunte, name='vista_apunte'),
    path('apunte/<int:pk>/calificar/', explorar_apuntes_views.calificar_apunte, name='calificar_apunte'),
    path('apunte/<int:pk>/guardar/', explorar_apuntes_views.guardar_apunte, name='guardar_apunte'),
    path('mi-biblioteca/', explorar_apuntes_views.mi_biblioteca, name='mi_biblioteca'),

    path('mis-apuntes/', gestion_apuntes_views.mis_apuntes, name='lista_mis_apuntes'),
    path('mis-apuntes/eliminar/<int:pk>/', gestion_apuntes_views.eliminar_apunte, name='eliminar_apunte'),
    path("apuntes/<int:pk>/descargar/", gestion_apuntes_views.descargar_apunte,name="descargar_apunte",)
]
