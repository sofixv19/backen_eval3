"""
Modelos de la app 'atencion' (Aplicación 5 — trabajo en equipo).

- Vecino: mantenedor de vecinos/as que se atienden en las delegaciones
  (inspirado en los campos "vecino contacto" del proyecto de Ignacio).
- SolicitudVecinal: tercera transacción operacional. Relaciona un Vecino,
  una Delegación y el Funcionario asignado (que debe pertenecer a esa
  delegación), y deja registro del usuario que la ingresó.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse

from delegaciones.models import Delegacion
from funcionarios.models import Funcionario


class Vecino(models.Model):
    nombre = models.CharField('Nombre completo', max_length=120)
    rut = models.CharField('RUT', max_length=12, unique=True, help_text='Ejemplo: 12.345.678-5')
    telefono = models.CharField('Teléfono', max_length=20)
    email = models.EmailField('Correo electrónico', blank=True)
    direccion = models.CharField('Dirección', max_length=200)
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.PROTECT,
        related_name='vecinos',
        verbose_name='Delegación de su sector',
    )
    creado = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Vecino'
        verbose_name_plural = 'Vecinos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.rut})'


class SolicitudVecinal(models.Model):
    class Tipo(models.TextChoices):
        SOLICITUD = 'Solicitud', 'Solicitud'
        RECLAMO = 'Reclamo', 'Reclamo'
        CONSULTA = 'Consulta', 'Consulta'
        SUGERENCIA = 'Sugerencia', 'Sugerencia'

    class Prioridad(models.TextChoices):
        BAJA = 'Baja', 'Baja'
        MEDIA = 'Media', 'Media'
        ALTA = 'Alta', 'Alta'

    class Estado(models.TextChoices):
        ABIERTA = 'Abierta', 'Abierta'
        CERRADA = 'Cerrada', 'Cerrada'

    codigo = models.CharField('Código', max_length=20, unique=True, editable=False)
    vecino = models.ForeignKey(Vecino, on_delete=models.PROTECT, related_name='solicitudes', verbose_name='Vecino')
    delegacion = models.ForeignKey(
        Delegacion, on_delete=models.PROTECT, related_name='solicitudes', verbose_name='Delegación',
    )
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.PROTECT, related_name='solicitudes', verbose_name='Funcionario asignado',
    )
    tipo = models.CharField('Tipo', max_length=20, choices=Tipo.choices, default=Tipo.SOLICITUD)
    prioridad = models.CharField('Prioridad', max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    descripcion = models.TextField('Descripción de la solicitud')
    estado = models.CharField('Estado', max_length=10, choices=Estado.choices, default=Estado.ABIERTA)
    respuesta = models.TextField('Respuesta / cierre', blank=True)
    registrada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes_registradas',
        verbose_name='Registrada por',
    )
    fecha = models.DateTimeField('Fecha de ingreso', auto_now_add=True)
    fecha_cierre = models.DateTimeField('Fecha de cierre', null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitud vecinal'
        verbose_name_plural = 'Solicitudes vecinales'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.codigo} · {self.vecino.nombre}'

    def get_absolute_url(self):
        return reverse('atencion:solicitud_detalle', args=[self.pk])
