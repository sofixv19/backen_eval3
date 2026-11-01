"""
Formulario de la app 'delegaciones' — Evaluación Sumativa 3.

Reemplaza la pantalla "en construcción" de la Evaluación 2: ahora el
formulario crea/modifica registros reales en la base de datos.
"""
from django import forms

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import Delegacion


class DelegacionForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Delegacion
        fields = ['nombre', 'encargado', 'direccion', 'telefono', 'email', 'territorio', 'enfoque']
        widgets = {
            'enfoque': forms.Textarea(attrs={'rows': 4}),
        }
