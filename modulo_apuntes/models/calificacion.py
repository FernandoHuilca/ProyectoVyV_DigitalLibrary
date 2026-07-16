from django.db import models

from modulo_apuntes.models.apunte import Apunte
from modulo_usuarios.models import PerfilEstudiante


class Calificacion(models.Model):
    TIPO_UTIL = "util"
    TIPO_NO_UTIL = "no_util"

    TIPOS = (
        (TIPO_UTIL, "Útil"),
        (TIPO_NO_UTIL, "No útil"),
    )

    usuario = models.ForeignKey(
        PerfilEstudiante,
        on_delete=models.CASCADE,
        related_name="calificaciones_emitidas",
    )
    apunte = models.ForeignKey(
        Apunte,
        on_delete=models.CASCADE,
        related_name="calificaciones",
    )
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "apunte"],
                name="unique_calificacion_por_usuario_apunte",
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.usuario.usuario.username} sobre {self.apunte.titulo}"
