from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db import transaction

from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_apuntes.models import Apunte, ApunteGuardado
from modulo_usuarios.models import PerfilEstudiante


@dataclass(frozen=True)
class EstadoApunte:
    disponible: bool
    acceso_restringido: bool


class ServicioGuardadoApuntes:
    def __init__(self, puntos_por_guardado: int = 5):
        self.puntos_por_guardado = puntos_por_guardado
        self.servicio_prestigio = ServicioNivelesPrestigio()

    def estado_de(self, apunte: Apunte) -> EstadoApunte:
        return EstadoApunte(
            disponible=apunte.disponible,
            acceso_restringido=apunte.acceso_restringido,
        )

    def asegurar_apunte_disponible(self, apunte: Apunte):
        estado = self.estado_de(apunte)
        if not estado.disponible or estado.acceso_restringido:
            raise ValueError("El apunte no está disponible para ser guardado.")

    def esta_guardado(self, usuario: PerfilEstudiante, apunte: Apunte) -> bool:
        return ApunteGuardado.objects.filter(usuario=usuario, apunte=apunte).exists()

    @transaction.atomic
    def guardar(self, usuario: PerfilEstudiante, apunte: Apunte):
        # Un usuario no puede guardar (marcar) su propio apunte
        if apunte.autor_id == usuario.id:
            raise PermissionDenied("No se puede guardar el propio apunte.")
        self.asegurar_apunte_disponible(apunte)
        guardado, creado = ApunteGuardado.objects.get_or_create(
            usuario=usuario,
            apunte=apunte,
        )
        if creado:
            self.servicio_prestigio.incrementar_prestigio(apunte.autor, self.puntos_por_guardado)
        return guardado

    @transaction.atomic
    def quitar(self, usuario: PerfilEstudiante, apunte: Apunte):
        eliminados, _ = ApunteGuardado.objects.filter(usuario=usuario, apunte=apunte).delete()
        if eliminados:
            self.servicio_prestigio.disminuir_prestigio(apunte.autor, self.puntos_por_guardado)

    def total_guardados(self, apunte: Apunte) -> int:
        return ApunteGuardado.objects.filter(apunte=apunte).count()
