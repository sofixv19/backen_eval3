"""
Modelos de la app 'cargos' (Aplicación 3 — trabajo en equipo).

Origen: estos dos modelos (CargoFuncion y MetaProyecto) parten del módulo
"gestionCargosApp" que desarrolló Ignacio Sepúlveda para su propio avance
del proyecto municipal. Se integraron aquí para que el sistema final sea
un trabajo conjunto, conectándolos con el sistema de autenticación,
perfiles y permisos de Django que ya existía en esta Evaluación 3 (algo
que el módulo original de Ignacio todavía no tenía: operaba solo con
vistas de lectura y Django Admin).

Se agrega como tercer mantenedor del sistema (superando el mínimo de 2
que pide la pauta), dejando el dominio de Delegaciones/Categorías/
Actividades tal como ya estaba, sin duplicarlo.
"""
from django.db import models


class CargoFuncion(models.Model):
    """Un cargo o función municipal (p. ej. "Funcionario Operativo")."""

    nombre_cargo = models.CharField('Cargo municipal', max_length=100, unique=True)
    descripcion = models.TextField('Descripción de funciones', blank=True)
    vigente = models.BooleanField('¿Vigente?', default=True)
    creado = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos y funciones'
        ordering = ['nombre_cargo']

    def __str__(self):
        return self.nombre_cargo


class MetaProyecto(models.Model):
    """Una meta institucional medible, asociada a un cargo."""

    cargo = models.ForeignKey(
        CargoFuncion,
        on_delete=models.CASCADE,
        related_name='metas',
        verbose_name='Cargo relacionado',
    )
    item_medible = models.CharField('Ítem / nombre de la meta', max_length=120)
    valor_objetivo = models.CharField('Meta asignada (valor objetivo)', max_length=255)
    unidad = models.CharField('Unidad de medida', max_length=50, default='Porcentaje')
    ponderador = models.PositiveIntegerField('Ponderación (%)', default=0)
    creado = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas institucionales'
        ordering = ['cargo__nombre_cargo', 'item_medible']

    def __str__(self):
        return f'{self.cargo.nombre_cargo} · {self.item_medible}'
