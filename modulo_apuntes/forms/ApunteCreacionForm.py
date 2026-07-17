from django import forms
from modulo_apuntes.models import Apunte
from django.contrib.auth.models import User


class ApunteForm(forms.ModelForm):
    # --- CAMPOS NUEVOS PARA LA REVISIÓN POR PARES ---
    revisor = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="Selecciona un estudiante...",
        label="¿Deseas que alguien lo revise? (Opcional)",
        widget=forms.Select(attrs={'class': 'campo-texto'})  # Ajusta la clase CSS si tienes una específica para selects
    )

    comentario_autor = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Ej: Por favor, revisa si los ejercicios prácticos están bien resueltos.',
            'class': 'campo-texto-area',
            'rows': 2,
        }),
        label="Mensaje para el revisor"
    )

    # ------------------------------------------------

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

    def __init__(self, *args, **kwargs):
        # Extraemos el usuario actual si se pasa al inicializar el form
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Excluimos al propio autor de la lista de revisores asi no se selecciona a si mismo jaja pilas hay que ser
        if self.user:
            self.fields['revisor'].queryset = User.objects.exclude(id=self.user.id).filter(is_active=True)

    def clean_contenido(self):
        """Valida que el PDF no supere 5 MB."""
        archivo = self.cleaned_data.get('contenido')
        if archivo:
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar los 5 MB.')
        return archivo