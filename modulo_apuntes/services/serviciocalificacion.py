from django.core.exceptions import PermissionDenied
from django.db import transaction

from modulo_apuntes.models import Apunte, Calificacion
from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_usuarios.models import PerfilEstudiante


class ServicioCalificacion:
    PUNTAJE_BASE_VOTO_UTIL = 2
    PUNTAJE_PENALIZACION_VOTO_NO_UTIL = 1
    PESOS_POR_RANGO = {
        "prepo": 1,
        "tecnologo": 2,
        "ingeniero": 3,
        "phd": 4,
    }

    def __init__(self):
        self.servicio_niveles = ServicioNivelesPrestigio()

    def _normalizar_rango(self, rango: str) -> str:
        return (
            rango.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("Á", "a")
            .replace("É", "e")
            .replace("Í", "i")
            .replace("Ó", "o")
            .replace("Ú", "u")
            .strip()
            .lower()
        )

    def _normalizar_tipo(self, tipo: str) -> str:
        tipo_normalizado = (
            tipo.replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("Á", "a")
            .replace("É", "e")
            .replace("Í", "i")
            .replace("Ó", "o")
            .replace("Ú", "u")
            .strip()
            .lower()
        )
        if tipo_normalizado == "util":
            return Calificacion.TIPO_UTIL
        if tipo_normalizado in ("no util", "no_util"):
            return Calificacion.TIPO_NO_UTIL
        raise ValueError(f"Tipo de calificación no soportado: {tipo}")

    def _validar_auto_voto(self, usuario: PerfilEstudiante, apunte: Apunte):
        if apunte.autor_id == usuario.id:
            raise PermissionDenied("No se permite el auto-voto.")

    def peso_para(self, usuario: PerfilEstudiante) -> int:
        rango = self._normalizar_rango(usuario.rango)
        return self.PESOS_POR_RANGO[rango]

    def _valor_calificacion(self, calificacion: Calificacion) -> int:
        peso = self.peso_para(calificacion.usuario)
        if calificacion.tipo == Calificacion.TIPO_UTIL:
            return self.PUNTAJE_BASE_VOTO_UTIL * peso
        return -self.PUNTAJE_PENALIZACION_VOTO_NO_UTIL * peso

    def prestigio_de_apunte(self, apunte: Apunte) -> int:
        total = 0
        for calificacion in Calificacion.objects.filter(apunte=apunte).select_related("usuario"):
            total += self._valor_calificacion(calificacion)
        return total

    def conteo_apunte(self, apunte: Apunte) -> dict[str, int]:
        return {
            Calificacion.TIPO_UTIL: Calificacion.objects.filter(apunte=apunte, tipo=Calificacion.TIPO_UTIL).count(),
            Calificacion.TIPO_NO_UTIL: Calificacion.objects.filter(apunte=apunte, tipo=Calificacion.TIPO_NO_UTIL).count(),
        }

    def tipo_usuario_en_apunte(self, usuario: PerfilEstudiante, apunte: Apunte):
        return (
            Calificacion.objects.filter(usuario=usuario, apunte=apunte)
            .values_list("tipo", flat=True)
            .first()
        )

    def prestigio_total_autor(self, autor: PerfilEstudiante) -> int:
        total = 0
        for apunte in autor.apuntes.all():
            total += self.prestigio_de_apunte(apunte)
        return total

    def recalcular_prestigio_autor(self, autor: PerfilEstudiante):
        total = self.prestigio_total_autor(autor)
        autor.puntos_prestigio = total
        autor.rango = self.servicio_niveles.rango_para_prestigio(total)
        autor.save(update_fields=["puntos_prestigio", "rango"])
        return autor

    @transaction.atomic
    def calificar(self, usuario: PerfilEstudiante, apunte: Apunte, tipo: str):
        self._validar_auto_voto(usuario, apunte)
        tipo_normalizado = self._normalizar_tipo(tipo)
        calificacion_aplicada_util = False

        Apunte.objects.select_for_update().get(pk=apunte.pk)
        autor = PerfilEstudiante.objects.select_for_update().get(pk=apunte.autor_id)

        calificacion = (
            Calificacion.objects.select_for_update()
            .filter(usuario=usuario, apunte=apunte)
            .first()
        )

        if calificacion and calificacion.tipo == tipo_normalizado:
            calificacion.delete()
        elif calificacion:
            calificacion.tipo = tipo_normalizado
            calificacion.save(update_fields=["tipo"])
            calificacion_aplicada_util = tipo_normalizado == Calificacion.TIPO_UTIL
        else:
            Calificacion.objects.create(
                usuario=usuario,
                apunte=apunte,
                tipo=tipo_normalizado,
            )
            calificacion_aplicada_util = tipo_normalizado == Calificacion.TIPO_UTIL

        self.recalcular_prestigio_autor(autor)

        if calificacion_aplicada_util:
            from modulo_notificaciones.signals import apunte_calificado_signal

            apunte_calificado_signal.send(
                sender=Apunte,
                apunte=apunte,
                calificador=usuario,
                tipo_calificacion=Calificacion.TIPO_UTIL,
            )

        return self.prestigio_de_apunte(apunte)

    @transaction.atomic
    def eliminar_calificacion(self, usuario: PerfilEstudiante, apunte: Apunte):
        Calificacion.objects.filter(usuario=usuario, apunte=apunte).delete()
        self.recalcular_prestigio_autor(apunte.autor)
