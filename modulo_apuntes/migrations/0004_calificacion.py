# Generated manually for utilidad/no utilidad votes.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("modulo_apuntes", "0003_apunte_total_descargas"),
    ]

    operations = [
        migrations.CreateModel(
            name="Calificacion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tipo", models.CharField(choices=[("util", "Útil"), ("no_util", "No útil")], max_length=10)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                (
                    "apunte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calificaciones",
                        to="modulo_apuntes.apunte",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calificaciones_emitidas",
                        to="modulo_usuarios.perfilestudiante",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("usuario", "apunte"),
                        name="unique_calificacion_por_usuario_apunte",
                    )
                ],
            },
        ),
    ]
