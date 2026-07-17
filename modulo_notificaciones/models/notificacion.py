from django.contrib.auth.models import User
from django.db import models


class Notificacion(models.Model):
    receptor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    remitente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notificaciones_enviadas",
    )
    mensaje = models.CharField(max_length=255)
    enlace = models.CharField(max_length=500, blank=True)
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Para {self.receptor.username}: {self.mensaje}"

