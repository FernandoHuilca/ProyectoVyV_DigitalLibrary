from .models.perfil_estudiante import PerfilEstudiante
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import admin

# 1. Creamos un "Inline" de nuestro perfil.
# Esto le dice a Django: "Muestra los campos de este modelo anidados dentro de otro".
class PerfilEstudianteInline(admin.StackedInline):
    model = PerfilEstudiante
    can_delete = False # Evita que borren el perfil sin borrar al usuario
    verbose_name_plural = 'Información del Estudiante'

# 2. Extendemos la clase administradora de Usuarios nativa de Django
class UserAdmin(BaseUserAdmin):
    # Le agregamos nuestro Inline del perfil
    inlines = (PerfilEstudianteInline,)

@admin.register(PerfilEstudiante)
class PerfilEstudianteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'carrera', 'semestre_actual')
    search_fields = ('usuario__username', 'usuario__email', 'carrera')
    list_filter = ('carrera', 'semestre_actual')
    raw_id_fields = ('usuario',)  # Mejor que un dropdown para muchos usuarios
    fields = (
        'usuario',
        'carrera',
        'semestre_actual',
        'foto_perfil',
        'descripcion',
        'bio',
        'temas_interes',
        'ira',
        'email_contacto',
    )

# 3. Des-registramos el modelo de Usuario que viene por defecto
admin.site.unregister(User)

# 4. Lo volvemos a registrar, pero ahora con nuestra clase modificada
admin.site.register(User, UserAdmin)