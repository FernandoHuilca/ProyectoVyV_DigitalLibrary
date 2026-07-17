from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import Signal, receiver
from django.urls import reverse

from modulo_apuntes.models import Apunte, ApunteGuardado, SolicitudRevision
from modulo_notificaciones.models import Notificacion
from modulo_usuarios.models import PerfilEstudiante

apunte_calificado_signal = Signal()


@receiver(pre_save, sender=Apunte)
def cache_estado_anterior_apunte(sender, instance, **kwargs):
    if not instance.pk:
        instance._estado_anterior = None
        return
    instance._estado_anterior = sender.objects.filter(pk=instance.pk).values_list("estado", flat=True).first()


@receiver(post_save, sender=Apunte)
def notificar_publicacion_apunte(sender, instance, created, **kwargs):
    if instance.estado != "PUBLICADO":
        return

    estado_anterior = getattr(instance, "_estado_anterior", None)
    if not created and estado_anterior == "PUBLICADO":
        return

    autor = instance.autor
    nombre_autor = autor.usuario.first_name or autor.usuario.username
    suscriptores = autor.suscriptores.select_related("usuario")
    for suscriptor in suscriptores:
        Notificacion.objects.create(
            receptor=suscriptor.usuario,
            remitente=autor.usuario,
            mensaje=f"{nombre_autor} ha publicado un nuevo apunte: {instance.titulo}",
            enlace=reverse("publicaciones:vista_apunte", args=[instance.pk]),
        )

@receiver(apunte_calificado_signal)
def notificar_calificacion_util(sender, apunte, calificador, tipo_calificacion, **kwargs):
    if tipo_calificacion != "util":
        return

    if apunte.autor_id == calificador.id:
        return

    Notificacion.objects.create(
        receptor=apunte.autor.usuario,
        remitente=calificador.usuario,
        mensaje=f'Tu apunte "{apunte.titulo}" recibio una nueva calificacion util.',
        enlace=reverse("publicaciones:vista_apunte", args=[apunte.pk]),
    )

@receiver(post_save, sender=ApunteGuardado)
def notificar_descarga_apunte(sender, instance, created, **kwargs):
    if not created:
        return

    apunte = instance.apunte
    guardador = instance.usuario

    if apunte.autor_id == guardador.id:
        return

    Notificacion.objects.create(
        receptor=apunte.autor.usuario,
        remitente=guardador.usuario,
        mensaje=f'Tu apunte "{apunte.titulo}" fue descargado.',
        enlace=reverse("publicaciones:vista_apunte", args=[apunte.pk]),
    )

@receiver(m2m_changed, sender=PerfilEstudiante.suscripciones.through)
def notificar_nuevo_suscriptor(sender, instance, action, pk_set, **kwargs):
    if action != "post_add":
        return

    for publicador_pk in pk_set:
        publicador = PerfilEstudiante.objects.get(pk=publicador_pk)
        nombre_suscriptor = instance.usuario.first_name or instance.usuario.username

        enlace_perfil = reverse("modulo_usuarios:perfil_usuario", args=[instance.pk])

        Notificacion.objects.create(
            receptor=publicador.usuario,
            remitente=instance.usuario,
            mensaje=f"{nombre_suscriptor} se ha suscrito a tu perfil",
            enlace=enlace_perfil,
        )


@receiver(pre_save, sender=SolicitudRevision)
def cache_estado_anterior_solicitud(sender, instance, **kwargs):
    if not instance.pk:
        instance._estado_anterior = None
        return
    instance._estado_anterior = sender.objects.filter(pk=instance.pk).values_list("estado", flat=True).first()


@receiver(post_save, sender=SolicitudRevision)
def notificar_flujo_revision(sender, instance, created, **kwargs):
    apunte = instance.apunte
    autor_user = apunte.autor.usuario
    revisor_user = instance.revisor

    if created:
        Notificacion.objects.create(
            receptor=revisor_user,
            remitente=autor_user,
            mensaje=f'Tienes una nueva solicitud de revision para el apunte: "{apunte.titulo}".',
            enlace=reverse("publicaciones:mis_revisiones"),
        )
        return

    estado_anterior = getattr(instance, "_estado_anterior", None)
    if estado_anterior == instance.estado:
        return

    if instance.estado == "APROBADO":
        Notificacion.objects.create(
            receptor=autor_user,
            remitente=revisor_user,
            mensaje=f'Tu apunte "{apunte.titulo}" ha sido aprobado. Ya puedes publicarlo.',
            enlace=reverse("publicaciones:lista_mis_apuntes"),
        )
        return

    if instance.estado == "RECHAZADO":
        Notificacion.objects.create(
            receptor=autor_user,
            remitente=revisor_user,
            mensaje=f'Se han solicitado cambios para tu apunte "{apunte.titulo}" en revision.',
            enlace=f'{reverse("publicaciones:lista_mis_apuntes")}?editar={apunte.pk}',
        )