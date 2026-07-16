from django.core.exceptions import PermissionDenied

from modulo_usuarios.models import PerfilEstudiante


class ServicioSuscripciones:
    def suscribir(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante):
        if suscriptor.id == publicador.id:
            raise PermissionDenied("No puedes suscribirte a tu propio perfil.")
        suscriptor.suscripciones.add(publicador)

    def cancelar_suscripcion(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante):
        suscriptor.suscripciones.remove(publicador)

    def esta_suscrito(self, suscriptor: PerfilEstudiante, publicador: PerfilEstudiante) -> bool:
        return suscriptor.suscripciones.filter(pk=publicador.pk).exists()

    def total_suscriptores(self, publicador: PerfilEstudiante) -> int:
        return publicador.suscriptores.count()

