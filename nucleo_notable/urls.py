from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Conectamos el módulo de usuarios.
    # Todo lo que empiece con 'usuarios/' se va para allá.
    path('usuarios/', include('modulo_usuarios.urls')),

    # 2. Dejamos el módulo de apuntes en la raíz limpia ('')
    path('', include(('modulo_publicaciones_apuntes.urls', 'publicaciones'), namespace='publicaciones')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)