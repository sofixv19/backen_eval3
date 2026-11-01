"""
Comando de gestión: crea (o actualiza) los 3 perfiles de usuario exigidos
por la Evaluación Sumativa 3, cada uno con un conjunto distinto de permisos
Django (los permisos add_x/change_x/delete_x/view_x que Django genera
automáticamente para cada modelo al migrar).

Uso:
    python manage.py crear_grupos

Resumen de los permisos que otorga cada perfil:

- Administrador: acceso total (crear/modificar/eliminar/ver) a
  Delegaciones, Categorías, Actividades y Cargos/Metas, más gestión de
  usuarios.
- Supervisor: ve todo; puede administrar Categorías, Actividades y
  Cargos/Metas (crear/modificar), pero NO puede eliminar ni gestionar
  Delegaciones.
- Administrativo: solo puede ver la información y registrar actividades
  nuevas (la "transacción"); no puede modificar ni eliminar nada.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# (app_label, nombre_modelo, [acciones]) -> se traduce a permisos
# "accion_nombremodelo" (ej. 'add_delegacion'), tal como los nombra Django.
PERMISOS_POR_GRUPO = {
    'Administrador': [
        ('delegaciones', 'delegacion', ['add', 'change', 'delete', 'view']),
        ('gestion', 'categoria', ['add', 'change', 'delete', 'view']),
        ('gestion', 'actividad', ['add', 'change', 'delete', 'view']),
        ('cargos', 'cargofuncion', ['add', 'change', 'delete', 'view']),
        ('cargos', 'metaproyecto', ['add', 'change', 'delete', 'view']),
        ('auth', 'user', ['add', 'change', 'view']),
    ],
    'Supervisor': [
        ('delegaciones', 'delegacion', ['view']),
        ('gestion', 'categoria', ['add', 'change', 'view']),
        ('gestion', 'actividad', ['add', 'change', 'view']),
        ('cargos', 'cargofuncion', ['add', 'change', 'view']),
        ('cargos', 'metaproyecto', ['add', 'change', 'view']),
    ],
    'Administrativo': [
        ('delegaciones', 'delegacion', ['view']),
        ('gestion', 'categoria', ['view']),
        ('gestion', 'actividad', ['add', 'view']),
        ('cargos', 'cargofuncion', ['view']),
        ('cargos', 'metaproyecto', ['view']),
    ],
}


class Command(BaseCommand):
    help = 'Crea/actualiza los grupos Administrador, Supervisor y Administrativo con sus permisos.'

    def handle(self, *args, **options):
        for nombre_grupo, reglas in PERMISOS_POR_GRUPO.items():
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            permisos = []
            for app_label, nombre_modelo, acciones in reglas:
                for accion in acciones:
                    codename = f'{accion}_{nombre_modelo}'
                    try:
                        permiso = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename,
                        )
                        permisos.append(permiso)
                    except Permission.DoesNotExist:
                        self.stderr.write(self.style.WARNING(
                            f'  Permiso no encontrado: {app_label}.{codename} '
                            f'(¿ejecutaste "python manage.py migrate" antes?)'
                        ))

            grupo.permissions.set(permisos)
            accion_txt = 'creado' if creado else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Grupo "{nombre_grupo}" {accion_txt} con {len(permisos)} permisos.'
            ))

        self.stdout.write(self.style.SUCCESS('\nListo. Ya puedes asignar estos perfiles a los usuarios '
                                              'desde "Gestión de usuarios" (solo visible para el perfil Administrador).'))
