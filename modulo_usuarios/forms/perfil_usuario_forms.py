from django import forms
from ..models import PerfilEstudiante

class PerfilEstudianteForm(forms.ModelForm):
    class Meta:
        model = PerfilEstudiante
        fields = [
            'carrera',
            'semestre_actual',
            'foto_perfil',
            'ira',
            'email_contacto',
            'temas_interes',
            'descripcion',
        ]
        widgets = {
            'carrera': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Ingeniería en Sistemas'
            }),
            'semestre_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': '1'
            }),
            'ira': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'max': 40,
                'placeholder': '33.5'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'temas_interes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Historia, Literatura, Filosofía'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cuéntanos sobre ti...'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }
        labels = {
            'carrera': 'Carrera',
            'semestre_actual': 'Semestre',
            'foto_perfil': 'Foto de Perfil',
            'ira': 'I.R.A.',
            'email_contacto': 'Email de Contacto',
            'temas_interes': 'Temas de Interés',
            'descripcion': 'Descripción',
        }