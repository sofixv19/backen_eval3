"""
Formularios de la app 'gestion' — Evaluación Sumativa 3.

- CategoriaForm: mantenedor de Categorías.
- ActividadForm: la "transacción operacional" exigida por la pauta — un
  formulario que relaciona dos entidades (Delegación y Categoría) para
  registrar una Actividad, con validaciones.
"""
from django import forms

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import Actividad, Categoria


class CategoriaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class ActividadForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['codigo', 'fecha', 'delegacion', 'categoria', 'descripcion', 'funcionario', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_codigo(self):
        # Normaliza el código (sin espacios al borde, en mayúsculas) antes
        # de que Django valide la restricción unique=True del modelo.
        return self.cleaned_data['codigo'].strip().upper()
