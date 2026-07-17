from django.urls import path

from modulo_notificaciones import views

app_name = "notificaciones"

urlpatterns = [
    path("", views.lista_notificaciones, name="lista_notificaciones"),
    path("suscribir/<int:perfil_id>/", views.suscribirse, name="suscribirse"),
    path("cancelar/<int:perfil_id>/", views.cancelar_suscripcion, name="cancelar_suscripcion"),
    path("marcar-todas-leidas/", views.marcar_todas_leidas, name="marcar_todas_leidas"),
    path("<int:pk>/leida/", views.marcar_leida, name="marcar_leida"),
]

