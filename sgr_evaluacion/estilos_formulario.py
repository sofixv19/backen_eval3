"""
Utilidad compartida para la Evaluación Sumativa 3.

Los formularios de autenticación y de recuperación de contraseña que trae
Django (AuthenticationForm, PasswordResetForm, SetPasswordForm) no agregan
la clase "form-control" de Bootstrap a sus campos. Este mixin la agrega
automáticamente a cualquier formulario que lo herede, para que se vean
igual que el resto de los formularios del sitio (delegaciones, categorías,
actividades, usuarios).
"""
from django import forms


class EstiloBootstrapMixin:
    """Agrega clases de Bootstrap a todos los widgets de un formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            clase_actual = campo.widget.attrs.get('class', '')
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs['class'] = (clase_actual + ' form-check-input').strip()
            elif isinstance(campo.widget, forms.Select):
                # "form-select" muestra la flecha de lista desplegable.
                campo.widget.attrs['class'] = (clase_actual + ' form-select').strip()
            else:
                campo.widget.attrs['class'] = (clase_actual + ' form-control').strip()
