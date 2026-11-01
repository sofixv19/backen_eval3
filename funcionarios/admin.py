from django.contrib import admin

from .models import Funcionario


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'delegacion', 'cargo', 'activo')
    search_fields = ('nombre', 'rut', 'email')
    list_filter = ('delegacion', 'cargo', 'activo')
