from django.db import models
from django.contrib.auth.models import User


class PerfilEstudiante(models.Model):
    # La relación estricta: un Perfil por cada Usuario de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')

    # Atributos específicos para la plataforma de apuntes
    carrera = models.CharField(max_length=100, verbose_name="Carrera Universitaria")
    semestre_actual = models.IntegerField(default=1)
    # puntos_reputacion = models.IntegerField(default=0, help_text="Puntos por subir apuntes de calidad")

    def __str__(self):
        return f"Perfil de {self.usuario.username}"