from django.urls import path

from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.listado, name='listado'),
    path('resumen/', views.resumen, name='resumen'),
    path('nueva/', views.crear, name='crear'),
    path('<int:actividad_id>/', views.detalle, name='detalle'),
    path('<int:actividad_id>/editar/', views.editar, name='editar'),
    path('<int:actividad_id>/eliminar/', views.eliminar, name='eliminar'),
    path('<int:actividad_id>/seguimiento/', views.registrar_seguimiento, name='registrar_seguimiento'),

    # Mantenedor de Categorías (Evaluación Sumativa 3)
    path('categorias/', views.categoria_listado, name='categoria_listado'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:categoria_id>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
]
