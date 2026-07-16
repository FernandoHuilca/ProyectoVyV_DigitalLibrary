from django.db.models.signals import post_save, m2m_changed
from django.dispatch import Signal, receiver
from django.urls import reverse  # <--- IMPORTANTE: Importa reverse aquí

from modulo_apuntes.models import Apunte, ApunteGuardado
from modulo_notificaciones.models import Notificacion
from modulo_usuarios.models import PerfilEstudiante

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
            # Reemplazamos el string hardcoded por reverse
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
        # Reemplazamos el string hardcoded por reverse
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
        # Reemplazamos el string hardcoded por reverse
        enlace=reverse("publicaciones:vista_apunte", args=[apunte.pk]),
    )

@receiver(m2m_changed, sender=PerfilEstudiante.suscripciones.through)
def notificar_nuevo_suscriptor(sender, instance, action, pk_set, **kwargs):
    if action != "post_add":
        return

    for publicador_pk in pk_set:
        publicador = PerfilEstudiante.objects.get(pk=publicador_pk)
        nombre_suscriptor = instance.usuario.first_name or instance.usuario.username

        # CONSTRUCCIÓN DINÁMICA DEL ENLACE AL PERFIL DEL SUSCRIPTOR
        enlace_perfil = reverse("modulo_usuarios:perfil_usuario", args=[instance.pk])

        Notificacion.objects.create(
            receptor=publicador.usuario,
            remitente=instance.usuario,
            mensaje=f"{nombre_suscriptor} se ha suscrito a tu perfil",
            enlace=enlace_perfil,  # <-- Ahora sí tiene un enlace funcional
        )