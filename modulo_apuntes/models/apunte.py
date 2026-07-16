from django.db import models

from modulo_usuarios.models import PerfilEstudiante


# Solo las clases que son tablas en la BD es la que hereda de models.Model
class Apunte(models.Model):
    # Campos de texto estándar
    titulo = models.CharField(max_length=200, verbose_name="Título del Apunte")
    descripcion = models.TextField(verbose_name="Descripción o Resumen")

    # El campo para el archivo.
    # 'upload_to' le dice a Django en qué subcarpeta guardar los PDFs cuando se suban
    contenido = models.FileField(upload_to='apuntes/documentos/%Y/%m/', verbose_name="Archivo del Apunte")

    # La relación Uno a Muchos.
    # related_name='apuntes' nos permitirá buscar todos los apuntes de un estudiante usando: estudiante.apuntes.all()
    autor = models.ForeignKey(PerfilEstudiante, on_delete=models.CASCADE, related_name='apuntes')

    # Siempre es buena práctica saber cuándo se creó el registro
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    disponible = models.BooleanField(default=True)
    acceso_restringido = models.BooleanField(default=False)

    # Si luego decides agregar una portada, se vería así:
    portada = models.ImageField(upload_to='apuntes/portadas/%Y/%m/', null=True, blank=True)

    total_descargas = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.titulo} - Subido por {self.autor.usuario.username}"

