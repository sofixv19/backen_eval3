from django.urls import path

from . import views

app_name = 'funcionarios'

urlpatterns = [
    path('', views.listado, name='listado'),
    path('nuevo/', views.crear, name='crear'),
    path('<int:funcionario_id>/editar/', views.editar, name='editar'),
    path('<int:funcionario_id>/eliminar/', views.eliminar, name='eliminar'),
]
