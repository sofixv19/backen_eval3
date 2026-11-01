from django import forms

from funcionarios.models import Funcionario
from funcionarios.rut import validar_rut
from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import SolicitudVecinal, Vecino


class VecinoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Vecino
        fields = ['nombre', 'rut', 'telefono', 'email', 'direccion', 'delegacion']

    def clean_rut(self):
        return validar_rut(self.cleaned_data['rut'])

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('Escribe el nombre completo.')
        return nombre


class FuncionarioSelect(forms.Select):
    """Select de funcionarios que agrega a cada opción el id de su
    delegación (data-delegacion), para filtrar la lista en el navegador."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opcion = super().create_option(name, value, label, selected, index, subindex, attrs)
        instancia = getattr(value, 'instance', None)
        if instancia is not None:
            opcion['attrs']['data-delegacion'] = instancia.delegacion_id
        return opcion


class SolicitudForm(EstiloBootstrapMixin, forms.ModelForm):
    """Tercera transacción: registra una solicitud de un vecino en una
    delegación y la asigna a un funcionario de esa misma delegación."""

    MIN_DESCRIPCION = 15

    class Meta:
        model = SolicitudVecinal
        fields = ['vecino', 'delegacion', 'funcionario', 'tipo', 'prioridad', 'descripcion', 'foto']
        widgets = {
            'funcionario': FuncionarioSelect,
            'foto': forms.FileInput(attrs={'accept': 'image/*'}),
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ej: Solicita poda de árbol que obstruye el alumbrado en la esquina de su pasaje.',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo funcionarios activos pueden recibir solicitudes nuevas.
        self.fields['funcionario'].queryset = (
            Funcionario.objects.filter(activo=True).select_related('delegacion', 'cargo').order_by('nombre')
        )
        self.fields['funcionario'].label_from_instance = lambda f: f'{f.nombre} — {f.cargo} ({f.delegacion})'

    def clean_descripcion(self):
        descripcion = ' '.join(self.cleaned_data['descripcion'].split())
        if len(descripcion) < self.MIN_DESCRIPCION:
            raise forms.ValidationError(f'Describe la solicitud con al menos {self.MIN_DESCRIPCION} caracteres.')
        return descripcion

    def clean(self):
        datos = super().clean()
        delegacion = datos.get('delegacion')
        funcionario = datos.get('funcionario')
        if delegacion and funcionario and funcionario.delegacion_id != delegacion.id:
            self.add_error(
                'funcionario',
                f'{funcionario.nombre} pertenece a la delegación "{funcionario.delegacion}". '
                f'Elige un funcionario de "{delegacion}".',
            )
        return datos


class CerrarSolicitudForm(EstiloBootstrapMixin, forms.Form):
    respuesta = forms.CharField(
        label='Respuesta o solución entregada',
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def clean_respuesta(self):
        respuesta = ' '.join(self.cleaned_data['respuesta'].split())
        if len(respuesta) < 10:
            raise forms.ValidationError('Describe la respuesta con al menos 10 caracteres.')
        return respuesta
