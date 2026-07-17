from django.db import models
from django.contrib.auth.models import User
from .apunte import Apunte  # Asegúrate de que la ruta sea la correcta en tu proyecto


class SolicitudRevision(models.Model):
    ESTADOS_REVISION = [
        ('PENDIENTE', 'Pendiente de revisión'),
        ('APROBADO', 'Avalado'),
        ('RECHAZADO', 'Requiere Cambios'),
    ]

    # Relación con el apunte y el usuario que va a revisar
    apunte = models.ForeignKey(Apunte, on_delete=models.CASCADE, related_name='revisiones')
    revisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revisiones_asignadas')

    # Estado individual de ESTA solicitud
    estado = models.CharField(max_length=20, choices=ESTADOS_REVISION, default='PENDIENTE')

    # Comentario que deja el publicador al enviar la solicitud
    comentario_autor = models.TextField(blank=True, null=True, help_text="¿Qué quieres que revise específicamente?")

    # Comentario que deja el revisor al aprobar o rechazar
    comentario_revisor = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Revisión de {self.apunte.titulo} por {self.revisor.username}"