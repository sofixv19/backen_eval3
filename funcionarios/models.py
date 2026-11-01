"""
Modelos de la app 'funcionarios' (Aplicación 4 — trabajo en equipo).

Basado en el modelo "Funcionario" del proyecto de Ignacio Sepúlveda
(registroActividadesApp): cada funcionario municipal pertenece a una
Delegación y ocupa un Cargo. Se conecta con las tablas ya existentes de
este sistema (delegaciones.Delegacion y cargos.CargoFuncion).

Ambas relaciones usan on_delete=PROTECT: no se puede eliminar una
delegación ni un cargo mientras tengan funcionarios asignados.
"""
from django.db import models

from cargos.models import CargoFuncion
from delegaciones.models import Delegacion


class Funcionario(models.Model):
    nombre = models.CharField('Nombre completo', max_length=120)
    rut = models.CharField('RUT', max_length=12, unique=True, help_text='Ejemplo: 12.345.678-5')
    email = models.EmailField('Correo electrónico', unique=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.PROTECT,
        related_name='funcionarios',
        verbose_name='Delegación asignada',
    )
    cargo = models.ForeignKey(
        CargoFuncion,
        on_delete=models.PROTECT,
        related_name='funcionarios',
        verbose_name='Cargo',
    )
    activo = models.BooleanField('¿Activo?', default=True)
    creado = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cargo})'
