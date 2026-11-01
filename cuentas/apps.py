from django.apps import AppConfig


class CuentasConfig(AppConfig):
    """App de la Evaluación Sumativa 3: autenticación, perfiles de usuario
    (grupos), recuperación de contraseña y paneles (dashboards) por perfil."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'
    verbose_name = 'Cuentas y perfiles'
