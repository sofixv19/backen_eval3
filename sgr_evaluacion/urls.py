from django.conf import settings
from django.conf.urls.static import static
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
    path('funcionarios/', include('funcionarios.urls')),
    path('atencion/', include('atencion.urls')),
]

# Sirve las fotos de perfil subidas por los usuarios (solo con DEBUG=True,
# que es como corre el servidor de desarrollo en local y en la instancia EC2).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
