"""
Rutas principales del proyecto SGR - Evaluación 3 (Programación Backend).

Django Admin se mantiene registrado (por si se necesita para alguna
tarea puntual de soporte), pero NO se usa para ninguna operación del
sistema: todas las operaciones (login, CRUD, recuperación de contraseña)
se realizan a través de las rutas propias de cada app, con Django
Templates.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='cuentas:login', permanent=False)),
    path('cuentas/', include('cuentas.urls')),
    path('delegaciones/', include('delegaciones.urls')),
    path('gestion/', include('gestion.urls')),
    path('cargos/', include('cargos.urls')),
]
