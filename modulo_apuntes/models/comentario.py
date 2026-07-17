from django.core.exceptions import ValidationError
from django.db import models

from modulo_apuntes.models.apunte import Apunte
from modulo_usuarios.models import PerfilEstudiante


class Comentario(models.Model):
    autor = models.ForeignKey(
        PerfilEstudiante,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    apunte = models.ForeignKey(
        Apunte,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="respuestas",
    )
    contenido = models.TextField(max_length=500, blank=True)
    tiene_corazon = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    editado_en = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        contenido_limpio = (self.contenido or "").strip()
        if not contenido_limpio:
            raise ValidationError({"contenido": "El comentario no puede estar vacío."})
        if len(contenido_limpio) > 500:
            raise ValidationError({"contenido": "El comentario no puede superar 500 caracteres."})
        if self.parent and self.parent.apunte_id != self.apunte_id:
            raise ValidationError({"parent": "El comentario padre debe pertenecer al mismo apunte."})
        if self.parent and self.parent.parent_id is not None:
            raise ValidationError({"parent": "Un comentario solo puede responder a un comentario principal."})

    def save(self, *args, **kwargs):
        self.contenido = (self.contenido or "").strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comentario de {self.autor.usuario.username} sobre {self.apunte.titulo}"
