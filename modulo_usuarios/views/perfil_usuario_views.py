from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.contrib import messages

from ..forms import PerfilEstudianteForm
from ..models import PerfilEstudiante


class PerfilDetailView(LoginRequiredMixin, DetailView):
    model = PerfilEstudiante
    template_name = 'usuarios/perfil_usuario.html'
    context_object_name = 'perfil_estudiante'

    def get_object(self, queryset=None):
        # Si no se provee pk en la URL, renderiza el perfil del usuario autenticado
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(PerfilEstudiante, pk=pk)
        return get_object_or_404(PerfilEstudiante, usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.object

        # ========== APUNTES ==========
        apuntes = perfil.apuntes.order_by('-fecha_creacion')
        context['apuntes'] = apuntes
        context['total_apuntes'] = perfil.apuntes.count()

        # ========== VALIDACION DE SUSCRIPCION ==========
        ya_suscrito = False
        user_autenticado = self.request.user

        if hasattr(user_autenticado, 'perfil'):
            mi_perfil = user_autenticado.perfil
            if mi_perfil != perfil:
                ya_suscrito = mi_perfil.suscripciones.filter(pk=perfil.pk).exists()
        context['ya_suscrito'] = ya_suscrito

        # ========== ESTADÍSTICAS (agregar lógica según tus modelos) ==========
        context['total_vistas'] = 0
        context['total_me_gustas'] = 0
        context['total_descargas'] = 0  # Agregar si tienes este campo
        context['total_comentarios'] = 0  # Agregar si tienes este campo

        # Contamos el número de seguidores
        context['total_seguidores'] = perfil.suscriptores.count()

        return context

class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = PerfilEstudiante
    form_class = PerfilEstudianteForm
    template_name = 'usuarios/perfil_usuario_edicion.html'
    success_url = reverse_lazy('modulo_usuarios:mi_perfil')


    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(PerfilEstudiante, pk=pk)
        return get_object_or_404(PerfilEstudiante, usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "¡Tu perfil ha sido actualizado con éxito!")
        return super().form_valid(form)