from django.urls import path

from . import views

app_name = 'atencion'

urlpatterns = [
    # Mantenedor de Vecinos
    path('vecinos/', views.vecinos_listado, name='vecinos_listado'),
    path('vecinos/nuevo/', views.vecino_crear, name='vecino_crear'),
    path('vecinos/<int:vecino_id>/editar/', views.vecino_editar, name='vecino_editar'),
    path('vecinos/<int:vecino_id>/eliminar/', views.vecino_eliminar, name='vecino_eliminar'),

    # Transacción: Solicitudes vecinales
    path('solicitudes/', views.solicitudes_listado, name='solicitudes_listado'),
    path('solicitudes/nueva/', views.solicitud_crear, name='solicitud_crear'),
    path('solicitudes/<int:solicitud_id>/', views.solicitud_detalle, name='solicitud_detalle'),
    path('solicitudes/<int:solicitud_id>/cerrar/', views.solicitud_cerrar, name='solicitud_cerrar'),
]
