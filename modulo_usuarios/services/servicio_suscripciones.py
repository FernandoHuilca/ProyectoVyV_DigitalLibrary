from django.db import transaction
from django.core.exceptions import PermissionDenied

from modulo_prestigio.models import HitoSuscripcionOtorgado
from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_usuarios.constants import PRESTIGIO_HITOS_SUSCRIPTORES
from modulo_usuarios.models import PerfilEstudiante


class ServicioSuscripciones:
    @transaction.atomic
    def suscribir(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante):
        if suscriptor.id == publicador.id:
            raise PermissionDenied("No puedes suscribirte a tu propio perfil.")

        if suscriptor.suscripciones.filter(pk=publicador.pk).exists():
            return

        suscriptor.suscripciones.add(publicador)

        total_suscriptores = publicador.suscriptores.count()
        puntos_hito = PRESTIGIO_HITOS_SUSCRIPTORES.get(total_suscriptores)
        if not puntos_hito:
            return

        hito_otorgado, creado = HitoSuscripcionOtorgado.objects.get_or_create(
            publicador=publicador,
            hito=total_suscriptores,
            defaults={"puntos_otorgados": int(puntos_hito)},
        )
        if not creado:
            return

        ServicioNivelesPrestigio().incrementar_prestigio(publicador, int(puntos_hito))

    def cancelar_suscripcion(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante):
        suscriptor.suscripciones.remove(publicador)

    def esta_suscrito(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante) -> bool:
        return suscriptor.suscripciones.filter(pk=publicador.pk).exists()

    def total_suscriptores(self, publicador: PerfilEstudiante) -> int:
        return publicador.suscriptores.count()

