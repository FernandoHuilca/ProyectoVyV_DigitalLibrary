from django.db import models

from modulo_apuntes.models.apunte import Apunte
from modulo_usuarios.models import PerfilEstudiante


class ApunteGuardado(models.Model):
    usuario = models.ForeignKey(
        PerfilEstudiante,
        on_delete=models.CASCADE,
        related_name="guardados",
    )
    apunte = models.ForeignKey(
        Apunte,
        on_delete=models.CASCADE,
        related_name="guardados",
    )
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "apunte"],
                name="unique_guardado_por_usuario_apunte",
            )
        ]

