from django.urls import path

from . import views

app_name = 'cargos'

urlpatterns = [
    path('', views.listado, name='listado'),
    path('nuevo/', views.crear, name='crear'),
    path('<int:cargo_id>/', views.detalle, name='detalle'),
    path('<int:cargo_id>/editar/', views.editar, name='editar'),
    path('<int:cargo_id>/eliminar/', views.eliminar, name='eliminar'),
    path('<int:cargo_id>/metas/nueva/', views.meta_crear, name='meta_crear'),
    path('metas/', views.metas_listado, name='metas_listado'),
    path('metas/nueva/', views.meta_crear, name='meta_nueva'),
    path('metas/<int:meta_id>/editar/', views.meta_editar, name='meta_editar'),
    path('metas/<int:meta_id>/eliminar/', views.meta_eliminar, name='meta_eliminar'),
]
