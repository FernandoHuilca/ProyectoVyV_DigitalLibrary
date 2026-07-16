from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from modulo_apuntes.models import Apunte, ApunteGuardado
from modulo_notificaciones.models import Notificacion


apunte_calificado_signal = Signal()


@receiver(post_save, sender=Apunte)
def notificar_publicacion_apunte(sender, instance, created, **kwargs):
    if not created:
        return

    autor = instance.autor
    nombre_autor = autor.usuario.first_name or autor.usuario.username
    suscriptores = autor.suscriptores.select_related("usuario")
    for suscriptor in suscriptores:
        Notificacion.objects.create(
            receptor=suscriptor.usuario,
            remitente=autor.usuario,
            mensaje=f"{nombre_autor} ha publicado un nuevo apunte: {instance.titulo}",
            enlace=f"/apuntes/{instance.pk}/",
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
        enlace=f"/apuntes/{apunte.pk}/",
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
        enlace=f"/apuntes/{apunte.pk}/",
    )


