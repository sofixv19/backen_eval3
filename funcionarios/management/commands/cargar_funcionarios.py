"""
Comando de gestión: carga funcionarios de ejemplo (datos ficticios),
asignados a las delegaciones y cargos que ya existan en la base de datos.

Uso (después de cargar_datos_iniciales y cargar_cargos):
    python manage.py cargar_funcionarios

Es idempotente: usa update_or_create() según el RUT.
"""
from django.core.management.base import BaseCommand

from cargos.models import CargoFuncion
from delegaciones.models import Delegacion
from funcionarios.models import Funcionario
from funcionarios.rut import calcular_dv, formatear_rut

# (nombre, número de RUT sin dígito verificador) — datos ficticios.
FUNCIONARIOS_EJEMPLO = [
    ('María Soto Pizarro', 15678234),
    ('Carlos Ruiz Araya', 12345678),
    ('Valentina Rojas Castillo', 18234567),
    ('Diego Pérez Tapia', 16543210),
    ('Camila Torres Vega', 20123456),
    ('Felipe González Muñoz', 17890123),
]


class Command(BaseCommand):
    help = 'Carga funcionarios de ejemplo asignados a delegaciones y cargos existentes.'

    def handle(self, *args, **options):
        delegaciones = list(Delegacion.objects.order_by('nombre'))
        cargos = list(CargoFuncion.objects.filter(vigente=True).order_by('nombre_cargo'))
        if not delegaciones or not cargos:
            self.stderr.write(self.style.WARNING(
                'Faltan delegaciones o cargos. Ejecuta primero "cargar_datos_iniciales" y "cargar_cargos".'
            ))
            return

        for i, (nombre, numero) in enumerate(FUNCIONARIOS_EJEMPLO):
            rut = formatear_rut(numero, calcular_dv(numero))
            usuario_correo = nombre.split()[0].lower() + '.' + nombre.split()[1].lower()
            usuario_correo = usuario_correo.translate(str.maketrans('áéíóúñ', 'aeioun'))
            Funcionario.objects.update_or_create(
                rut=rut,
                defaults={
                    'nombre': nombre,
                    'email': f'{usuario_correo}@laserena.example',
                    'telefono': f'+56 9 {5100_0000 + i * 1111:08d}'[:16],
                    'delegacion': delegaciones[i % len(delegaciones)],
                    'cargo': cargos[i % len(cargos)],
                    'activo': True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Funcionario.objects.count()} funcionarios disponibles en la base de datos.'
        ))
