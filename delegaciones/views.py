"""
Vistas de la app 'delegaciones' (Aplicación 1).

Evaluación Sumativa 3: se elimina la dependencia de Django Admin. Las
operaciones de creación/modificación/eliminación ahora son formularios
reales con Django Templates, protegidas con el sistema de permisos de
Django (ver cuentas/decorators.py y cuentas/management/commands/
crear_grupos.py para el detalle de qué perfil tiene cada permiso).
"""
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cuentas.decorators import permiso_requerido
from gestion.models import Actividad
from gestion.services import grados_donut, resumen_por_estado

from .forms import DelegacionForm
from .models import Delegacion


def _actividades_por_delegacion():
    """Cuenta cuántas actividades tiene cada delegación (para el gráfico de
    barras de la portada), mediante una consulta ORM agregada."""
    filas = (
        Actividad.objects.values('delegacion__nombre')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )
    if not filas:
        return []

    maximo = max(fila['cantidad'] for fila in filas)
    return [
        {
            'nombre': fila['delegacion__nombre'],
            'cantidad': fila['cantidad'],
            'porcentaje': round(fila['cantidad'] / maximo * 100),
        }
        for fila in filas
    ]


@permiso_requerido('delegaciones.view_delegacion')
def inicio(request):
    """Resumen general con gráficos (accesible para cualquier perfil autenticado)."""

    total = Delegacion.objects.count()

    if total > 0:
        mensaje_resumen = f'Actualmente hay {total} delegaciones registradas.'
    else:
        mensaje_resumen = 'Aún no hay delegaciones registradas.'

    conteo_estado, total_actividades = resumen_por_estado()

    contexto = {
        'titulo_pagina': 'Delegaciones Municipales - La Serena',
        'total_delegaciones': total,
        'mensaje_resumen': mensaje_resumen,
        'actividades_por_delegacion': _actividades_por_delegacion(),
        'conteo_estado': conteo_estado,
        'total_actividades': total_actividades,
        'donut_grados': grados_donut(conteo_estado, total_actividades),
    }
    return render(request, 'delegaciones/inicio.html', contexto)


@permiso_requerido('delegaciones.view_delegacion')
def listado(request):
    """Listado de delegaciones, con búsqueda opcional por texto (?q=)."""

    query = request.GET.get('q', '').strip()
    delegaciones = Delegacion.objects.all()

    if query:
        delegaciones = delegaciones.filter(
            Q(nombre__icontains=query)
            | Q(encargado__icontains=query)
            | Q(territorio__icontains=query)
        )

    contexto = {
        'titulo_pagina': 'Listado de Delegaciones',
        'delegaciones': delegaciones,
        'query': query,
    }
    return render(request, 'delegaciones/listado.html', contexto)


@permiso_requerido('delegaciones.view_delegacion')
def detalle(request, slug):
    """Ficha de detalle de una delegación específica, buscada por su slug."""

    delegacion = get_object_or_404(Delegacion, slug=slug)

    contexto = {
        'titulo_pagina': delegacion.nombre,
        'delegacion': delegacion,
    }
    return render(request, 'delegaciones/detalle.html', contexto)


# ---------------------------------------------------------------------------
# CRUD funcional (Evaluación Sumativa 3): crear, modificar y eliminar
# delegaciones mediante formularios propios, sin usar Django Admin.
# ---------------------------------------------------------------------------

@permiso_requerido('delegaciones.add_delegacion')
def crear(request):
    if request.method == 'POST':
        form = DelegacionForm(request.POST)
        if form.is_valid():
            delegacion = form.save()
            messages.success(request, f'Delegación "{delegacion.nombre}" creada correctamente.')
            return redirect(delegacion.get_absolute_url())
    else:
        form = DelegacionForm()

    contexto = {
        'titulo_pagina': 'Agregar delegación',
        'accion': 'Agregar delegación',
        'form': form,
        'volver_url': reverse('delegaciones:listado'),
    }
    return render(request, 'delegaciones/form.html', contexto)


@permiso_requerido('delegaciones.change_delegacion')
def editar(request, slug):
    delegacion = get_object_or_404(Delegacion, slug=slug)

    if request.method == 'POST':
        form = DelegacionForm(request.POST, instance=delegacion)
        if form.is_valid():
            delegacion = form.save()
            messages.success(request, f'Delegación "{delegacion.nombre}" actualizada correctamente.')
            return redirect(delegacion.get_absolute_url())
    else:
        form = DelegacionForm(instance=delegacion)

    contexto = {
        'titulo_pagina': f'Editar {delegacion.nombre}',
        'accion': f'Modificar delegación: {delegacion.nombre}',
        'form': form,
        'volver_url': reverse('delegaciones:detalle', args=[delegacion.slug]),
    }
    return render(request, 'delegaciones/form.html', contexto)


@permiso_requerido('delegaciones.delete_delegacion')
def eliminar(request, slug):
    delegacion = get_object_or_404(Delegacion, slug=slug)

    if request.method == 'POST':
        nombre = delegacion.nombre
        try:
            delegacion.delete()
        except ProtectedError:
            # Funcionario, Vecino y SolicitudVecinal -> Delegacion usan PROTECT.
            messages.error(
                request,
                f'No se puede eliminar "{nombre}": tiene funcionarios, vecinos o solicitudes asociadas. '
                'Reasígnalos a otra delegación primero.',
            )
            return redirect(delegacion.get_absolute_url())
        messages.success(request, f'Delegación "{nombre}" eliminada correctamente.')
        return redirect('delegaciones:listado')

    contexto = {
        'titulo_pagina': f'Eliminar {delegacion.nombre}',
        'accion': f'Eliminar delegación: {delegacion.nombre}',
        'delegacion': delegacion,
        'volver_url': reverse('delegaciones:detalle', args=[delegacion.slug]),
    }
    return render(request, 'delegaciones/eliminar.html', contexto)
