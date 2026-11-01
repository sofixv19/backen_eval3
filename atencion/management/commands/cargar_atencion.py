"""
Comando de gestión: carga vecinos y solicitudes vecinales de ejemplo
(datos ficticios).

Uso (después de cargar_datos_iniciales, cargar_cargos y cargar_funcionarios):
    python manage.py cargar_atencion

Es idempotente: los vecinos se identifican por RUT y las solicitudes de
ejemplo no se duplican si ya existen.
"""
from django.core.management.base import BaseCommand

from atencion.models import SolicitudVecinal, Vecino
from delegaciones.models import Delegacion
from funcionarios.models import Funcionario
from funcionarios.rut import calcular_dv, formatear_rut

VECINOS_EJEMPLO = [
    ('Rosa Alvarado Díaz', 9876543, 'Pasaje Los Aromos 1234'),
    ('Juan Castro Molina', 11222333, 'Av. Francisco de Aguirre 567'),
    ('Paula Fuentes Rivera', 14555666, 'Calle Las Rosas 89'),
    ('Héctor Navarro Silva', 8765432, 'Villa El Milagro, block 3, depto 12'),
    ('Javiera Espinoza León', 19333444, 'Los Copihues 2210'),
]

SOLICITUDES_EJEMPLO = [
    ('Reclamo', 'Alta', 'Luminaria apagada hace dos semanas en la esquina del pasaje, el sector queda muy oscuro de noche.'),
    ('Solicitud', 'Media', 'Solicita retiro de escombros y ramas acumuladas en el bandejón frente a su domicilio.'),
    ('Consulta', 'Baja', 'Consulta por requisitos para postular al subsidio de mejoramiento de vivienda.'),
]


class Command(BaseCommand):
    help = 'Carga vecinos y solicitudes vecinales de ejemplo.'

    def handle(self, *args, **options):
        delegaciones = list(Delegacion.objects.order_by('nombre'))
        if not delegaciones:
            self.stderr.write(self.style.WARNING('No hay delegaciones. Ejecuta primero "cargar_datos_iniciales".'))
            return

        vecinos = []
        for i, (nombre, numero, direccion) in enumerate(VECINOS_EJEMPLO):
            vecino, _ = Vecino.objects.update_or_create(
                rut=formatear_rut(numero, calcular_dv(numero)),
                defaults={
                    'nombre': nombre,
                    'telefono': f'+56 9 {6200_0000 + i * 2357:08d}',
                    'direccion': f'{direccion}, La Serena',
                    'delegacion': delegaciones[i % len(delegaciones)],
                },
            )
            vecinos.append(vecino)

        if not SolicitudVecinal.objects.exists():
            for i, (tipo, prioridad, descripcion) in enumerate(SOLICITUDES_EJEMPLO):
                vecino = vecinos[i]
                funcionario = (
                    Funcionario.objects.filter(activo=True, delegacion=vecino.delegacion).first()
                    or Funcionario.objects.filter(activo=True).first()
                )
                if funcionario is None:
                    self.stderr.write(self.style.WARNING(
                        'No hay funcionarios. Ejecuta primero "cargar_funcionarios" para crear solicitudes.'
                    ))
                    break
                solicitud = SolicitudVecinal.objects.create(
                    codigo=f'TMP-EJEMPLO-{i}',
                    vecino=vecino,
                    delegacion=funcionario.delegacion,
                    funcionario=funcionario,
                    tipo=tipo,
                    prioridad=prioridad,
                    descripcion=descripcion,
                )
                solicitud.codigo = f'SOL-{solicitud.pk:05d}'
                solicitud.save(update_fields=['codigo'])

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Vecino.objects.count()} vecinos y '
            f'{SolicitudVecinal.objects.count()} solicitudes disponibles en la base de datos.'
        ))
