from django.db import migrations


def recompute_rango(apps, schema_editor):
    Perfil = apps.get_model('modulo_usuarios', 'PerfilEstudiante')
    # Importar el servicio de niveles; si falla, no interrumpir la migración
    try:
        from modulo_usuarios.services.niveles_prestigio import ServicioNivelesPrestigio
    except Exception:
        ServicioNivelesPrestigio = None

    servicio = ServicioNivelesPrestigio() if ServicioNivelesPrestigio else None

    # Actualizar cada perfil: calcular rango según puntos_prestigio
    for perfil in Perfil.objects.all():
        puntos = perfil.puntos_prestigio or 0
        nuevo_rango = servicio.rango_para_prestigio(puntos) if servicio else perfil.rango
        if perfil.rango != nuevo_rango:
            perfil.rango = nuevo_rango
            perfil.save(update_fields=["rango"])


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_usuarios', '0003_perfilestudiante_puntos_prestigio_and_more'),
    ]

    operations = [
        migrations.RunPython(recompute_rango, migrations.RunPython.noop),
    ]
