from django.contrib import admin

from .models import CargoFuncion, MetaProyecto


@admin.register(CargoFuncion)
class CargoFuncionAdmin(admin.ModelAdmin):
    list_display = ('nombre_cargo', 'vigente', 'creado')
    search_fields = ('nombre_cargo', 'descripcion')
    list_filter = ('vigente',)
    ordering = ('nombre_cargo',)


@admin.register(MetaProyecto)
class MetaProyectoAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'item_medible', 'ponderador')
    search_fields = ('item_medible', 'cargo__nombre_cargo')
    list_filter = ('cargo',)
    ordering = ('cargo__nombre_cargo',)
