from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='cuentas:login', permanent=False)),
    path('cuentas/', include('cuentas.urls')),
    path('delegaciones/', include('delegaciones.urls')),
    path('gestion/', include('gestion.urls')),
    path('cargos/', include('cargos.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('atencion/', include('atencion.urls')),
]

# Sirve las fotos subidas por los usuarios (perfil y evidencias). Se deja
# activo también con DEBUG=False, porque la instancia EC2 usa el servidor
# de Django (runserver) y no un servidor web aparte para los archivos.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
