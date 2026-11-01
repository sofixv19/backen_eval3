"""
Rutas de la app 'cuentas': login/logout, paneles por perfil, gestión de
usuarios, y recuperación de contraseña por correo (vistas oficiales de
Django: PasswordResetView y las 3 que completan su flujo).
"""
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import NuevaClaveForm, RecuperarClaveForm

app_name = 'cuentas'

urlpatterns = [
    # Autenticación
    path('ingresar/', views.login_view, name='login'),
    path('salir/', views.logout_view, name='logout'),

    # Paneles (dashboards) por perfil
    path('panel/', views.panel, name='panel'),
    path('panel/administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    path('panel/supervisor/', views.dashboard_supervisor, name='dashboard_supervisor'),
    path('panel/administrativo/', views.dashboard_administrativo, name='dashboard_administrativo'),

    # Gestión de usuarios (solo perfil Administrador)
    path('usuarios/', views.usuarios_listado, name='usuarios_listado'),
    path('usuarios/nuevo/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:user_id>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:user_id>/estado/', views.usuario_cambiar_estado, name='usuario_cambiar_estado'),

    # Recuperación de contraseña por correo electrónico (flujo completo)
    path(
        'clave/recuperar/',
        auth_views.PasswordResetView.as_view(
            template_name='cuentas/password_reset_form.html',
            email_template_name='cuentas/password_reset_email.html',
            subject_template_name='cuentas/password_reset_subject.txt',
            form_class=RecuperarClaveForm,
            success_url=reverse_lazy('cuentas:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'clave/recuperar/enviado/',
        auth_views.PasswordResetDoneView.as_view(template_name='cuentas/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'clave/restablecer/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='cuentas/password_reset_confirm.html',
            form_class=NuevaClaveForm,
            success_url=reverse_lazy('cuentas:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'clave/restablecer/listo/',
        auth_views.PasswordResetCompleteView.as_view(template_name='cuentas/password_reset_complete.html'),
        name='password_reset_complete',
    ),
]
