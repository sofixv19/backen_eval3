from django.urls import path

from . import views

app_name = 'delegaciones'

urlpatterns = [
    path('', views.listado, name='listado'),
    path('resumen/', views.inicio, name='inicio'),
    path('nueva/', views.crear, name='crear'),
    path('<slug:slug>/', views.detalle, name='detalle'),
    path('<slug:slug>/editar/', views.editar, name='editar'),
    path('<slug:slug>/eliminar/', views.eliminar, name='eliminar'),
]
