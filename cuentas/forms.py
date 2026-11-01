"""
Formularios de la app 'cuentas': inicio de sesión, recuperación de
contraseña (ambos son subclases de los formularios que trae Django, solo
agregando estilos de Bootstrap) y gestión de usuarios/perfiles.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import Group

from sgr_evaluacion.estilos_formulario import EstiloBootstrapMixin

from .models import PerfilUsuario

Usuario = get_user_model()

TAMANO_MAXIMO_FOTO_MB = 2


class MisDatosForm(EstiloBootstrapMixin, forms.ModelForm):
    """Datos personales que cada usuario puede editar en "Mi perfil"."""

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }
        help_texts = {
            'email': 'Se usa para recuperar tu contraseña.',
        }


class FotoPerfilForm(EstiloBootstrapMixin, forms.ModelForm):
    """Foto de perfil (opcional), con límite de tamaño."""

    class Meta:
        model = PerfilUsuario
        fields = ['foto']
        widgets = {
            'foto': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto and foto.size > TAMANO_MAXIMO_FOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f'La foto no puede pesar más de {TAMANO_MAXIMO_FOTO_MB} MB.')
        return foto


class CambiarClaveForm(EstiloBootstrapMixin, PasswordChangeForm):
    """Cambio de contraseña del propio usuario (pide la contraseña actual)."""


class LoginForm(EstiloBootstrapMixin, AuthenticationForm):
    """Formulario de inicio de sesión (usa el AuthenticationForm oficial de
    Django, que valida usuario/contraseña contra el backend de autenticación)."""


class RecuperarClaveForm(EstiloBootstrapMixin, PasswordResetForm):
    """Formulario para solicitar el enlace de recuperación por correo."""


class NuevaClaveForm(EstiloBootstrapMixin, SetPasswordForm):
    """Formulario para definir la nueva contraseña tras validar el token."""


class UsuarioCreacionForm(EstiloBootstrapMixin, forms.ModelForm):
    """Crea un usuario nuevo y lo asigna a un perfil (grupo)."""

    password1 = forms.CharField(
        label='Contraseña', widget=forms.PasswordInput, min_length=8,
        help_text='Mínimo 8 caracteres.',
    )
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    grupo = forms.ModelChoiceField(
        label='Perfil', queryset=Group.objects.all(), empty_label='Selecciona un perfil…',
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }

    def clean(self):
        datos = super().clean()
        p1, p2 = datos.get('password1'), datos.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
            usuario.groups.set([self.cleaned_data['grupo']])
        return usuario


class UsuarioEdicionForm(EstiloBootstrapMixin, forms.ModelForm):
    """Edita los datos y el perfil (grupo) de un usuario existente."""

    grupo = forms.ModelChoiceField(label='Perfil', queryset=Group.objects.all())

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'is_active']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'is_active': 'Usuario activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            grupo_actual = self.instance.groups.first()
            if grupo_actual:
                self.fields['grupo'].initial = grupo_actual.pk

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.groups.set([self.cleaned_data['grupo']])
        return usuario
