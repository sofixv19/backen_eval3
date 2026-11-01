from django.contrib import admin

from .models import SolicitudVecinal, Vecino


@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'telefono', 'delegacion')
    search_fields = ('nombre', 'rut')


@admin.register(SolicitudVecinal)
class SolicitudVecinalAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'vecino', 'delegacion', 'funcionario', 'tipo', 'prioridad', 'estado', 'fecha')
    list_filter = ('estado', 'tipo', 'prioridad', 'delegacion')
    search_fields = ('codigo', 'vecino__nombre')
