from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F

from modulo_apuntes.models import Apunte
from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_usuarios.models import PerfilEstudiante


class ServicioDescargas:

    def __init__(self, puntos_por_descarga: int = 2):
        self.puntos_por_descarga = puntos_por_descarga
        self.servicio_prestigio = ServicioNivelesPrestigio()

    @transaction.atomic
    def descargar(self, usuario: PerfilEstudiante, apunte: Apunte):
        # Validar que el apunte pueda descargarse
        if not apunte.disponible or apunte.acceso_restringido:
            raise PermissionDenied("El apunte no está disponible para descarga.")

        if apunte.autor_id != usuario.id:
            self.agregar_nueva_descarga(apunte)
            self.servicio_prestigio.incrementar_prestigio(
                apunte.autor,
                self.puntos_por_descarga
            )

    def agregar_nueva_descarga(self, apunte: Apunte):
        Apunte.objects.filter(pk=apunte.pk).update(
            total_descargas=F("total_descargas") + 1
        )