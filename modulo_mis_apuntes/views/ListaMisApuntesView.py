from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import context
from django.views.generic.list import ListView
from modulo_publicaciones_apuntes.models import Apunte

class ListaMisApuntesView(LoginRequiredMixin, ListView):
    model = Apunte
    template_name = 'lista_mis_apuntes.html'
    context_object_name = 'apuntes'

    def get_queryset(self):

        return Apunte.objects.filter(autor__usuario=self.request.user).order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apuntes = self.get_queryset()

        # Agregar estadísticas al contexto
        context['total_apuntes'] = apuntes.count()
        #context['total_vistas'] = sum(getattr(a, 'vistas_count', 0) for a in apuntes)
        #context['total_me_gustas'] = sum(getattr(a, 'me_gusta_count', 0) for a in apuntes)

        return context