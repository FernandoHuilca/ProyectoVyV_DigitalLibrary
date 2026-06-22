from django import forms
from modulo_publicaciones_apuntes.models import Apunte


class ApunteForm(forms.ModelForm):
    """
    Formulario compartido para crear y actualizar apuntes.
    La vista determina si opera en modo CREATE o UPDATE
    pasando una instancia o None al instanciar el form.
    """

    class Meta:
        model = Apunte
        fields = ['titulo', 'descripcion', 'contenido', 'portada']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Ej: Álgebra Lineal - Matrices',
                'class': 'campo-texto',
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Describe brevemente qué cubre este apunte',
                'class': 'campo-texto-area',
                'rows': 3,
            }),
            'contenido': forms.FileInput(attrs={
                'class': 'campo-archivo',
                'accept': '.pdf',
            }),
            'portada': forms.FileInput(attrs={
                'class': 'campo-archivo',
                'accept': 'image/*',
            }),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'contenido': 'Archivo PDF',
            'portada': 'Portada (opcional)',
        }

    def clean_contenido(self):
        """Valida que el PDF no supere 5 MB."""
        archivo = self.cleaned_data.get('contenido')
        if archivo:
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar los 5 MB.')
        return archivo