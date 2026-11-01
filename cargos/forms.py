from django import forms

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import CargoFuncion, MetaProyecto


class CargoFuncionForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = CargoFuncion
        fields = ['nombre_cargo', 'descripcion', 'vigente']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class MetaProyectoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = MetaProyecto
        fields = ['cargo', 'item_medible', 'valor_objetivo', 'unidad', 'ponderador']
