"""
La app 'cuentas' no define modelos propios: usa directamente el modelo de
usuario de Django (django.contrib.auth.models.User) y los grupos
(django.contrib.auth.models.Group) como "perfiles" (Administrador,
Supervisor, Administrativo), tal como permite y recomienda el sistema de
autenticación de Django.
"""
