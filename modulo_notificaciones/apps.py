from django.apps import AppConfig


class ModuloNotificacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modulo_notificaciones"

    def ready(self):
        import modulo_notificaciones.signals  # noqa: F401

