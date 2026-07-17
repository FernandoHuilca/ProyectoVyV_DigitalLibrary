# modulo_notificaciones/context_processors.py

def notificaciones_usuario(request):
    if request.user.is_authenticated:
        # Traemos las últimas 5 notificaciones sin leer
        alertas = request.user.notificaciones.filter(leido=False).order_by('-creado_en')[:5]
        sin_leer = request.user.notificaciones.filter(leido=False).count()
        return {
            'mis_notificaciones': alertas,
            'notificaciones_pendientes_count': sin_leer
        }
    return {}