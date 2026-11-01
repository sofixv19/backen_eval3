"""
Modelos de la app 'gestion' (Aplicación 2).

Evaluación Sumativa 2: la información que en la Evaluación 1 vivía en
`data/actividades.json` ahora se modela con relaciones reales hacia
`delegaciones.Delegacion`, más un catálogo de categorías.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse

from delegaciones.models import Delegacion


class Categoria(models.Model):
    """Catálogo de categorías de actividad (Diserco, Social, Seguridad, etc.).

    Se modela como tabla propia (y no como texto libre) para demostrar
    una segunda relación (ForeignKey) además de la que existe con
    Delegacion, y para que se pueda administrar desde Django Admin.
    """

    nombre = models.CharField('Nombre', max_length=80, unique=True)
    descripcion = models.CharField('Descripción', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    """Una actividad / solicitud registrada por una delegación."""

    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        EN_PROCESO = 'En proceso', 'En proceso'
        REALIZADO = 'Realizado', 'Realizado'

    codigo = models.CharField('Código', max_length=20, unique=True)
    fecha = models.DateField('Fecha')
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='Delegación',
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='actividades',
        verbose_name='Categoría',
    )
    descripcion = models.TextField('Descripción')
    funcionario = models.CharField(
        'Funcionario a cargo', max_length=120,
        help_text='Dato de ejemplo, no corresponde a una persona real.',
    )
    estado = models.CharField(
        'Estado', max_length=20, choices=Estado.choices, default=Estado.PENDIENTE,
    )

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-fecha', 'codigo']

    def __str__(self):
        return f'{self.codigo} · {self.delegacion.nombre}'

    def get_absolute_url(self):
        return reverse('gestion:detalle', args=[self.pk])


class SeguimientoActividad(models.Model):
    """Segunda transacción operacional (trabajo en equipo): registro del
    seguimiento de una actividad.

    Cada registro relaciona una Actividad con el Usuario que la revisó,
    guarda el cambio de estado (anterior -> nuevo) y una observación. Al
    guardarse, también actualiza el estado de la Actividad, ambas cosas
    dentro de una misma transacción de base de datos (transaction.atomic).
    """

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='seguimientos',
        verbose_name='Actividad',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seguimientos_realizados',
        verbose_name='Registrado por',
    )
    estado_anterior = models.CharField('Estado anterior', max_length=20, choices=Actividad.Estado.choices)
    estado_nuevo = models.CharField('Nuevo estado', max_length=20, choices=Actividad.Estado.choices)
    observacion = models.TextField('Observación')
    fecha = models.DateTimeField('Fecha del seguimiento', auto_now_add=True)

    class Meta:
        verbose_name = 'Seguimiento de actividad'
        verbose_name_plural = 'Seguimientos de actividades'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.actividad.codigo}: {self.estado_anterior} -> {self.estado_nuevo}'
