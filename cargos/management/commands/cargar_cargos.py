"""
Comando de gestión: carga data/cargos.json (basado en el módulo de Ignacio
Sepúlveda) como registros de CargoFuncion + MetaProyecto.

Uso:
    python manage.py cargar_cargos

Es idempotente: usa update_or_create() según el nombre del cargo.
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from cargos.models import CargoFuncion, MetaProyecto


class Command(BaseCommand):
    help = 'Carga data/cargos.json en la base de datos (cargos y sus metas).'

    def handle(self, *args, **options):
        ruta = Path(settings.BASE_DIR) / 'data' / 'cargos.json'

        with open(ruta, encoding='utf-8') as archivo:
            items = json.load(archivo)

        for item in items:
            cargo, _ = CargoFuncion.objects.update_or_create(
                nombre_cargo=item['cargo'],
                defaults={
                    'descripcion': item.get('descripcion', ''),
                    'vigente': True,
                },
            )
            MetaProyecto.objects.update_or_create(
                cargo=cargo,
                item_medible=item['meta'],
                defaults={
                    'valor_objetivo': item['meta'],
                    'unidad': item.get('unidad', 'Porcentaje'),
                    'ponderador': item.get('ponderacion', 0),
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {CargoFuncion.objects.count()} cargos y '
            f'{MetaProyecto.objects.count()} metas disponibles en la base de datos.'
        ))
