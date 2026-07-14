from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class NivelPrestigio:
    nombre: str
    minimo: int


class ServicioNivelesPrestigio:
    """
    Encapsula las reglas de negocio para asignar y actualizar el rango
    de un estudiante según su puntaje de prestigio.
    """

    NIVELES: ClassVar[tuple[NivelPrestigio, ...]] = (
        NivelPrestigio(nombre="Prepo", minimo=0),
        NivelPrestigio(nombre="Tecnólogo", minimo=300),
        NivelPrestigio(nombre="Ingeniero", minimo=700),
        NivelPrestigio(nombre="PHD", minimo=3000),
    )

    def rango_para_prestigio(self, puntos_prestigio: int) -> str:
        if puntos_prestigio < 0:
            return self.NIVELES[0].nombre

        rango_actual = self.NIVELES[0].nombre
        for nivel in self.NIVELES:
            if puntos_prestigio >= nivel.minimo:
                rango_actual = nivel.nombre
            else:
                break
        return rango_actual

    def aplicar_estado(self, perfil, puntos_prestigio: int):
        perfil.puntos_prestigio = puntos_prestigio
        perfil.rango = self.rango_para_prestigio(puntos_prestigio)
        perfil.save(update_fields=["puntos_prestigio", "rango"])
        return perfil

    def registrar_nuevo_estudiante(self, perfil):
        return self.aplicar_estado(perfil, 0)

    def incrementar_prestigio(self, perfil, puntos: int):
        return self.aplicar_estado(perfil, perfil.puntos_prestigio + puntos)

    def disminuir_prestigio(self, perfil, puntos: int):
        return self.aplicar_estado(perfil, perfil.puntos_prestigio - puntos)

