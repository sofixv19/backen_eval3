"""
Vistas de la app 'cuentas' — Evaluación Sumativa 3.

Incluye: inicio/cierre de sesión (usando las utilidades oficiales de
Django: AuthenticationForm, login(), logout()), el enrutador de panel por
perfil, los 3 paneles (dashboards) diferenciados, y la gestión de usuarios
(creación y asignación de grupos), exclusiva del perfil Administrador.

La recuperación de contraseña NO tiene vistas propias aquí: se usan las
vistas basadas en clases que trae Django (PasswordResetView y similares),
declaradas directamente en cuentas/urls.py, solo personalizando sus
templates para mantener el estilo del sitio.
"""
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from delegaciones.models import Delegacion
from gestion.models import Actividad, Categoria

from .decorators import grupo_requerido
from .forms import LoginForm, UsuarioCreacionForm, UsuarioEdicionForm

Usuario = get_user_model()

# Nombre del grupo (perfil) -> nombre de la URL de su panel.
GRUPOS_DASHBOARD = {
    'Administrador': 'cuentas:dashboard_administrador',
    'Supervisor': 'cuentas:dashboard_supervisor',
    'Administrativo': 'cuentas:dashboard_administrativo',
}


def login_view(request):
    """Inicio de sesión mediante usuario y contraseña."""
    if request.user.is_authenticated:
        return redirect('cuentas:panel')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Bienvenido/a, {form.get_user().get_username()}.')
        return redirect('cuentas:panel')

    return render(request, 'cuentas/login.html', {'form': form, 'titulo_pagina': 'Iniciar sesión'})


def logout_view(request):
    """Cierre de sesión. Solo acepta POST (botón en la barra de navegación),
    que es la forma recomendada por Django desde la versión 4.1."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('cuentas:login')


@login_required(login_url='cuentas:login')
def panel(request):
    """Redirige a cada usuario autenticado al panel que corresponde a su
    perfil (grupo). Es el valor de LOGIN_REDIRECT_URL."""
    for nombre_grupo, nombre_url in GRUPOS_DASHBOARD.items():
        if request.user.groups.filter(name=nombre_grupo).exists():
            return redirect(nombre_url)

    if request.user.is_superuser:
        return redirect('cuentas:dashboard_administrador')

    messages.warning(request, 'Tu usuario no tiene un perfil (grupo) asignado. Contacta a un administrador.')
    return redirect('cuentas:login')


@grupo_requerido('Administrador')
def dashboard_administrador(request):
    contexto = {
        'titulo_pagina': 'Panel de Administrador',
        'total_delegaciones': Delegacion.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_actividades': Actividad.objects.count(),
        'total_usuarios': Usuario.objects.count(),
    }
    return render(request, 'cuentas/dashboard_administrador.html', contexto)


@grupo_requerido('Supervisor')
def dashboard_supervisor(request):
    contexto = {
        'titulo_pagina': 'Panel de Supervisor',
        'total_delegaciones': Delegacion.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_actividades': Actividad.objects.count(),
        'actividades_pendientes': Actividad.objects.filter(estado=Actividad.Estado.PENDIENTE).count(),
    }
    return render(request, 'cuentas/dashboard_supervisor.html', contexto)


@grupo_requerido('Administrativo')
def dashboard_administrativo(request):
    contexto = {
        'titulo_pagina': 'Panel Administrativo',
        'total_actividades': Actividad.objects.count(),
        'actividades_pendientes': Actividad.objects.filter(estado=Actividad.Estado.PENDIENTE).count(),
        'actividades_realizadas': Actividad.objects.filter(estado=Actividad.Estado.REALIZADO).count(),
    }
    return render(request, 'cuentas/dashboard_administrativo.html', contexto)


# ---------------------------------------------------------------------------
# Gestión de usuarios (mínimo "Creación de usuarios" / "Asignación de
# grupos" exigido por la pauta). Exclusiva del perfil Administrador.
# ---------------------------------------------------------------------------

@grupo_requerido('Administrador')
def usuarios_listado(request):
    usuarios = Usuario.objects.all().order_by('username').prefetch_related('groups')
    contexto = {'titulo_pagina': 'Usuarios del sistema', 'usuarios': usuarios}
    return render(request, 'cuentas/usuarios_listado.html', contexto)


@grupo_requerido('Administrador')
def usuario_crear(request):
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" creado correctamente.')
            return redirect('cuentas:usuarios_listado')
    else:
        form = UsuarioCreacionForm()

    contexto = {
        'titulo_pagina': 'Crear usuario',
        'accion': 'Crear usuario',
        'form': form,
        'volver_url': reverse('cuentas:usuarios_listado'),
    }
    return render(request, 'cuentas/usuario_form.html', contexto)


@grupo_requerido('Administrador')
def usuario_editar(request, user_id):
    usuario = get_object_or_404(Usuario, pk=user_id)
    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado correctamente.')
            return redirect('cuentas:usuarios_listado')
    else:
        form = UsuarioEdicionForm(instance=usuario)

    contexto = {
        'titulo_pagina': f'Editar {usuario.username}',
        'accion': f'Modificar usuario: {usuario.username}',
        'form': form,
        'volver_url': reverse('cuentas:usuarios_listado'),
    }
    return render(request, 'cuentas/usuario_form.html', contexto)


@grupo_requerido('Administrador')
def usuario_cambiar_estado(request, user_id):
    """Activa/desactiva un usuario (se usa en vez de eliminarlo, para no
    perder el historial de qué usuario creó/modificó cada registro)."""
    usuario = get_object_or_404(Usuario, pk=user_id)
    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            usuario.is_active = not usuario.is_active
            usuario.save(update_fields=['is_active'])
            estado = 'activado' if usuario.is_active else 'desactivado'
            messages.success(request, f'Usuario "{usuario.username}" {estado} correctamente.')
    return redirect('cuentas:usuarios_listado')
