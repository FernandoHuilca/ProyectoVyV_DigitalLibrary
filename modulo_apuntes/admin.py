from django.contrib import admin
from .models import Apunte



# Nueva configuración para la tabla Apunte
@admin.register(Apunte)
class ApunteAdmin(admin.ModelAdmin):
    # list_display define qué columnas quieres ver en la tabla resumen del admin
    list_display = ('titulo', 'autor', 'fecha_creacion')

    # Agregamos una barra de búsqueda súper útil
    search_fields = ('titulo', 'descripcion')

    # Y un filtro lateral por fechas
    list_filter = ('fecha_creacion',)