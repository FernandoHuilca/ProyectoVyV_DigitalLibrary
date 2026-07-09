from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilEstudiante(models.Model):
    # La relación estricta: un Perfil por cada Usuario de Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')

    # Atributos específicos para la plataforma de apuntes
    carrera = models.CharField(max_length=100, verbose_name="Carrera Universitaria")
    semestre_actual = models.IntegerField(default=1)
    foto_perfil = models.ImageField(upload_to='perfiles/avatares/', default='perfiles/default.png')

    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Corta")
    bio = models.TextField(blank=True, null=True, verbose_name="Biografía o Información")
    temas_interes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Temas de Interés")
    ira = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="IRA")
    email_contacto = models.EmailField(blank=True, null=True, verbose_name="Email de Contacto")
    puntos_prestigio = models.IntegerField(default=0, verbose_name="Puntos de Prestigio")
    rango = models.CharField(max_length=50, default="MAESTRO", verbose_name="Rango")

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    @property
    def total_apuntes(self):
        """
        Cuenta el total de apuntes publicados por este estudiante
        El modelo debe tener autor = FK(PerfilEstudiante)
        """
        return self.apuntes.count()
# SIGNAL: Crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta automáticamente después de guardar un User.
    Si el usuario es NUEVO (created=True), crea su perfil.
    """
    if created:
        PerfilEstudiante.objects.create(
            usuario=instance,
            carrera="No especificada",  # Valor por defecto
            semestre_actual=1,
        )

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Esta función asegura que el perfil se guarde cuando el usuario se guarda.
    """
    # Solo ejecutar si el usuario tiene perfil (evita errores)
    if hasattr(instance, 'perfil'):
        instance.perfil.save()