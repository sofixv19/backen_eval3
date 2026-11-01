"""
Modelos de la app 'cuentas'.

Para usuarios y perfiles (Administrador, Supervisor, Administrativo) se usa
directamente el sistema de autenticación de Django (User y Group).

Se agrega solo un modelo pequeño, PerfilUsuario, para la página "Mi perfil":
guarda la foto de cada usuario, relacionado 1 a 1 con el User de Django.
"""
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

EXTENSIONES_FOTO = ['jpg', 'jpeg', 'png', 'webp', 'gif']


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario',
    )
    # Se usa FileField + validación de extensión (en vez de ImageField) para
    # no depender de la librería Pillow.
    foto = models.FileField(
        'Foto de perfil',
        upload_to='fotos_perfil/',
        blank=True,
        validators=[FileExtensionValidator(EXTENSIONES_FOTO)],
    )

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.usuario.get_username()}'
