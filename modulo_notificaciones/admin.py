from django.contrib import admin

from modulo_notificaciones.models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "receptor", "remitente", "leido", "creado_en")
    list_filter = ("leido", "creado_en")
    search_fields = ("receptor__username", "remitente__username", "mensaje")

