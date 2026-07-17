from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from modulo_apuntes.models import Apunte, Comentario
from modulo_prestigio.services import ServicioNivelesPrestigio
from modulo_usuarios.models import PerfilEstudiante


class ServicioComentario:
    PUNTOS_COMENTARIO_PRINCIPAL = 2
    PUNTOS_RESPUESTA = 1
    PUNTOS_CORAZON = 5

    def __init__(self):
        self.servicio_prestigio = ServicioNivelesPrestigio()

    def _resolver_parent(self, parent: Comentario | None) -> Comentario | None:
        if parent is None:
            return None
        if parent.parent_id is not None:
            return parent.parent
        return parent

    def _autor_objetivo_para_creacion(self, apunte: Apunte, parent: Comentario | None) -> PerfilEstudiante:
        if parent is None:
            return apunte.autor
        return parent.autor

    @transaction.atomic
    def crear_comentario(
        self,
        autor: PerfilEstudiante,
        apunte: Apunte,
        contenido: str,
        parent: Comentario | None = None,
    ) -> Comentario:
        parent_resuelto = self._resolver_parent(parent)
        comentario = Comentario(
            autor=autor,
            apunte=apunte,
            parent=parent_resuelto,
            contenido=contenido,
        )
        comentario.save()
        comentario.editado_en = comentario.creado_en
        comentario.save(update_fields=["editado_en"])

        autor_objetivo = self._autor_objetivo_para_creacion(apunte, parent_resuelto)
        if autor_objetivo.id != autor.id:
            puntos = self.PUNTOS_COMENTARIO_PRINCIPAL if parent_resuelto is None else self.PUNTOS_RESPUESTA
            self.servicio_prestigio.incrementar_prestigio(autor_objetivo, puntos)

        return comentario

    @transaction.atomic
    def editar_comentario(
        self,
        usuario_solicitante: PerfilEstudiante,
        comentario: Comentario,
        nuevo_contenido: str,
    ) -> Comentario:
        if comentario.autor_id != usuario_solicitante.id:
            raise PermissionDenied("Solo el autor puede editar su comentario.")

        comentario.contenido = nuevo_contenido
        comentario.editado_en = timezone.now()
        comentario.save(update_fields=["contenido", "editado_en"])
        return comentario

    @transaction.atomic
    def dar_corazon(
        self,
        usuario_solicitante: PerfilEstudiante,
        comentario: Comentario,
    ) -> Comentario:
        if comentario.apunte.autor_id != usuario_solicitante.id:
            raise PermissionDenied("Solo el autor del apunte puede dar corazón.")
        if comentario.autor_id == usuario_solicitante.id:
            raise PermissionDenied("No se puede dar corazón al propio comentario.")

        comentario = Comentario.objects.select_for_update().select_related("autor", "apunte").get(pk=comentario.pk)
        autor_comentario = comentario.autor

        if comentario.tiene_corazon:
            comentario.tiene_corazon = False
            comentario.save(update_fields=["tiene_corazon"])
            nuevo_total = max(0, autor_comentario.puntos_prestigio - self.PUNTOS_CORAZON)
            self.servicio_prestigio.aplicar_estado(autor_comentario, nuevo_total)
        else:
            comentario.tiene_corazon = True
            comentario.save(update_fields=["tiene_corazon"])
            self.servicio_prestigio.incrementar_prestigio(autor_comentario, self.PUNTOS_CORAZON)

        return comentario
