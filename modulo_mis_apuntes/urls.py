from django.urls import path
from .views.ListaMisApuntesView import ListaMisApuntesView

app_name = 'modulo_mis_apuntes'
urlpatterns = [
    path('', ListaMisApuntesView.as_view(), name='lista_mis_apuntes'),
]