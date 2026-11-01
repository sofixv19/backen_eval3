"""
Formularios de la app 'gestion' — Evaluación Sumativa 3.

- CategoriaForm: mantenedor de Categorías.
- ActividadForm: la "transacción operacional" exigida por la pauta — un
  formulario que relaciona dos entidades (Delegación y Categoría) para
  registrar una Actividad, con validaciones.
"""
from django import forms

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import Actividad, Categoria, SeguimientoActividad


class CategoriaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class ActividadForm(EstiloBootstrapMixin, forms.ModelForm):
    quitar_foto = forms.BooleanField(label='Quitar la foto actual', required=False)

    class Meta:
        model = Actividad
        fields = ['codigo', 'fecha', 'delegacion', 'categoria', 'descripcion', 'funcionario', 'estado',
                  'foto_evidencia']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'foto_evidencia': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_codigo(self):
        # Normaliza el código (sin espacios al borde, en mayúsculas) antes
        # de que Django valide la restricción unique=True del modelo.
        return self.cleaned_data['codigo'].strip().upper()

    def save(self, commit=True):
        actividad = super().save(commit=False)
        # "Quitar la foto actual" solo aplica si no se subió una nueva.
        if self.cleaned_data.get('quitar_foto') and 'foto_evidencia' not in self.files:
            actividad.foto_evidencia = None
        if commit:
            actividad.save()
        return actividad


class SeguimientoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Segunda transacción: registra el seguimiento (cambio de estado +
    observación) de una actividad."""

    MIN_OBSERVACION = 10

    class Meta:
        model = SeguimientoActividad
        fields = ['estado_nuevo', 'observacion', 'foto']
        widgets = {
            'foto': forms.FileInput(attrs={'accept': 'image/*'}),
            'observacion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ej: Se visitó el sector y se coordinó el retiro de escombros con la cuadrilla municipal.',
            }),
        }

    def __init__(self, *args, actividad, **kwargs):
        super().__init__(*args, **kwargs)
        self.actividad = actividad
        # Solo se ofrecen estados distintos al actual.
        self.fields['estado_nuevo'].choices = [
            (valor, etiqueta) for valor, etiqueta in Actividad.Estado.choices if valor != actividad.estado
        ]
        # Sugiere el siguiente paso natural del flujo.
        siguiente = {
            Actividad.Estado.PENDIENTE: Actividad.Estado.EN_PROCESO,
            Actividad.Estado.EN_PROCESO: Actividad.Estado.REALIZADO,
        }.get(actividad.estado)
        if siguiente and not self.is_bound:
            self.initial['estado_nuevo'] = siguiente

    def clean_estado_nuevo(self):
        estado = self.cleaned_data['estado_nuevo']
        if estado == self.actividad.estado:
            raise forms.ValidationError('El nuevo estado debe ser distinto al estado actual.')
        return estado

    def clean_observacion(self):
        observacion = ' '.join(self.cleaned_data['observacion'].split())
        if len(observacion) < self.MIN_OBSERVACION:
            raise forms.ValidationError(
                f'Describe el seguimiento con al menos {self.MIN_OBSERVACION} caracteres.'
            )
        return observacion
