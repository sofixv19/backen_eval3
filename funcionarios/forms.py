from django import forms

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import Funcionario
from .rut import validar_rut


class FuncionarioForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nombre', 'rut', 'email', 'telefono', 'delegacion', 'cargo', 'activo']

    def clean_rut(self):
        # Valida el dígito verificador y guarda siempre el mismo formato
        # (12.345.678-5), así la restricción unique=True detecta duplicados
        # aunque se escriban con o sin puntos.
        return validar_rut(self.cleaned_data['rut'])

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('Escribe el nombre completo.')
        return nombre

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()
