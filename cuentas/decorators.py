"""
Decoradores para proteger vistas según el perfil (grupo) o los permisos del
usuario autenticado — Evaluación Sumativa 3, requisitos "Protección de
vistas mediante autenticación" y "Restricción de acceso según perfil".

Se definen dos niveles de control, usados en distintos puntos del sistema:

- `grupo_requerido(...)`: control "grueso", por nombre de perfil. Se usa en
  los paneles (dashboards) y en la gestión de usuarios, que son exclusivos
  de un perfil específico (ej. solo "Administrador").

- `permiso_requerido(...)`: control "fino", usando el sistema de permisos
  de Django (los permisos add_x/change_x/delete_x/view_x que Django genera
  automáticamente por cada modelo). Se usa en las operaciones CRUD de los
  mantenedores y en la transacción, porque esos permisos ya están asignados
  de forma diferenciada a cada grupo (ver cuentas/management/commands/
  crear_grupos.py).

Ambos exigen primero que el usuario haya iniciado sesión (login_required);
si no cumple el grupo/permiso exigido, se le redirige con un mensaje de
error en vez de mostrar un error técnico.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def grupo_requerido(*nombres_grupo):
    """Exige que el usuario pertenezca a alguno de los grupos indicados
    (los superusuarios siempre tienen acceso, como en cualquier sistema)."""

    def decorador(vista):
        @wraps(vista)
        @login_required(login_url='cuentas:login')
        def vista_envuelta(request, *args, **kwargs):
            if request.user.is_superuser or request.user.groups.filter(name__in=nombres_grupo).exists():
                return vista(request, *args, **kwargs)
            messages.error(request, 'No tienes acceso a esta sección con tu perfil actual.')
            return redirect('cuentas:panel')
        return vista_envuelta
    return decorador


def permiso_requerido(*permisos):
    """Exige que el usuario tenga TODOS los permisos Django indicados
    (formato 'app_label.codename', ej. 'delegaciones.add_delegacion')."""

    def decorador(vista):
        @wraps(vista)
        @login_required(login_url='cuentas:login')
        def vista_envuelta(request, *args, **kwargs):
            if request.user.is_superuser or request.user.has_perms(permisos):
                return vista(request, *args, **kwargs)
            messages.error(request, 'No tienes permisos suficientes para realizar esta acción.')
            return redirect('cuentas:panel')
        return vista_envuelta
    return decorador
