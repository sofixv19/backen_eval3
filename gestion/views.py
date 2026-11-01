"""
Vistas de la app 'gestion' (Aplicación 2).

Evaluación Sumativa 3: se agrega el mantenedor de Categorías (antes solo
administrable desde Django Admin) y se implementa de forma funcional el
CRUD de Actividades, que además es la "transacción operacional" exigida
por la pauta (relaciona Delegación + Categoría, con formulario y
validaciones). Todo protegido con el sistema de permisos de Django.
"""
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cuentas.decorators import permiso_requerido

from .forms import ActividadForm, CategoriaForm, SeguimientoForm
from .models import Actividad, Categoria
from .services import grados_donut, resumen_por_estado


@permiso_requerido('gestion.view_actividad')
def listado(request):
    """Actividades registradas, con filtro por estado (?estado=) y búsqueda
    de texto (?q=), ambos resueltos con consultas ORM."""

    actividades = Actividad.objects.select_related('delegacion', 'categoria').all()

    estado_seleccionado = request.GET.get('estado')
    if estado_seleccionado in Actividad.Estado.values:
        actividades = actividades.filter(estado=estado_seleccionado)

    query = request.GET.get('q', '').strip()
    if query:
        actividades = actividades.filter(
            Q(codigo__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(delegacion__nombre__icontains=query)
            | Q(categoria__nombre__icontains=query)
        )

    contexto = {
        'titulo_pagina': 'Actividades registradas',
        'actividades': actividades,
        'estados': Actividad.Estado.values,
        'estado_seleccionado': estado_seleccionado,
        'query': query,
        'total': actividades.count(),
    }
    return render(request, 'gestion/listado.html', contexto)


@permiso_requerido('gestion.view_actividad')
def detalle(request, actividad_id):
    """Ficha de detalle de una actividad, con su historial de seguimiento."""

    actividad = get_object_or_404(
        Actividad.objects.select_related('delegacion', 'categoria'),
        pk=actividad_id,
    )

    contexto = {
        'titulo_pagina': f'Actividad {actividad.codigo}',
        'actividad': actividad,
        'seguimientos': actividad.seguimientos.select_related('responsable'),
    }
    return render(request, 'gestion/detalle.html', contexto)


# ---------------------------------------------------------------------------
# Segunda transacción: seguimiento de una actividad. Guarda el registro de
# seguimiento Y actualiza el estado de la actividad dentro de una misma
# transacción de base de datos (si algo falla, no se guarda ninguno).
# ---------------------------------------------------------------------------

@permiso_requerido('gestion.add_seguimientoactividad')
def registrar_seguimiento(request, actividad_id):
    actividad = get_object_or_404(Actividad.objects.select_related('delegacion', 'categoria'), pk=actividad_id)

    if request.method == 'POST':
        form = SeguimientoForm(request.POST, actividad=actividad)
        if form.is_valid():
            with transaction.atomic():
                # Bloquea la fila para que dos usuarios no cambien el estado a la vez.
                actividad = Actividad.objects.select_for_update().get(pk=actividad.pk)
                seguimiento = form.save(commit=False)
                seguimiento.actividad = actividad
                seguimiento.responsable = request.user
                seguimiento.estado_anterior = actividad.estado
                seguimiento.save()
                actividad.estado = seguimiento.estado_nuevo
                actividad.save(update_fields=['estado'])
            messages.success(
                request,
                f'Seguimiento registrado: "{actividad.codigo}" pasó de '
                f'{seguimiento.estado_anterior} a {seguimiento.estado_nuevo}.',
            )
            return redirect(actividad.get_absolute_url())
    else:
        form = SeguimientoForm(actividad=actividad)

    contexto = {
        'titulo_pagina': f'Seguimiento de {actividad.codigo}',
        'actividad': actividad,
        'form': form,
    }
    return render(request, 'gestion/seguimiento_form.html', contexto)


@permiso_requerido('gestion.view_actividad')
def resumen(request):
    """Vista tipo 'semáforo': totaliza actividades por estado."""

    conteo, total = resumen_por_estado()

    if total > 0:
        porcentaje_realizado = round((conteo['realizado'] / total) * 100, 1)
    else:
        porcentaje_realizado = 0

    contexto = {
        'titulo_pagina': 'Resumen de gestión',
        'conteo': conteo,
        'total': total,
        'porcentaje_realizado': porcentaje_realizado,
        'donut_grados': grados_donut(conteo, total),
    }
    return render(request, 'gestion/resumen.html', contexto)


# ---------------------------------------------------------------------------
# Actividades: CRUD funcional. "crear" es, además, la transacción
# operacional exigida por la pauta (relaciona Delegación + Categoría).
# ---------------------------------------------------------------------------

@permiso_requerido('gestion.add_actividad')
def crear(request):
    if request.method == 'POST':
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save()
            messages.success(request, f'Actividad "{actividad.codigo}" registrada correctamente.')
            return redirect(actividad.get_absolute_url())
    else:
        form = ActividadForm(initial={'estado': Actividad.Estado.PENDIENTE})

    contexto = {
        'titulo_pagina': 'Registrar actividad',
        'accion': 'Registrar actividad',
        'form': form,
        'volver_url': reverse('gestion:listado'),
    }
    return render(request, 'gestion/actividad_form.html', contexto)


@permiso_requerido('gestion.change_actividad')
def editar(request, actividad_id):
    actividad = get_object_or_404(Actividad, pk=actividad_id)

    if request.method == 'POST':
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            actividad = form.save()
            messages.success(request, f'Actividad "{actividad.codigo}" actualizada correctamente.')
            return redirect(actividad.get_absolute_url())
    else:
        form = ActividadForm(instance=actividad)

    contexto = {
        'titulo_pagina': f'Editar {actividad.codigo}',
        'accion': f'Modificar actividad: {actividad.codigo}',
        'form': form,
        'volver_url': reverse('gestion:detalle', args=[actividad.pk]),
    }
    return render(request, 'gestion/actividad_form.html', contexto)


@permiso_requerido('gestion.delete_actividad')
def eliminar(request, actividad_id):
    actividad = get_object_or_404(Actividad, pk=actividad_id)

    if request.method == 'POST':
        codigo = actividad.codigo
        actividad.delete()
        messages.success(request, f'Actividad "{codigo}" eliminada correctamente.')
        return redirect('gestion:listado')

    contexto = {
        'titulo_pagina': f'Eliminar {actividad.codigo}',
        'accion': f'Eliminar actividad: {actividad.codigo}',
        'actividad': actividad,
        'volver_url': reverse('gestion:detalle', args=[actividad.pk]),
    }
    return render(request, 'gestion/actividad_eliminar.html', contexto)


# ---------------------------------------------------------------------------
# Categorías: segundo mantenedor completo (crear/buscar/listar/
# modificar/eliminar), exigido por la pauta.
# ---------------------------------------------------------------------------

@permiso_requerido('gestion.view_categoria')
def categoria_listado(request):
    query = request.GET.get('q', '').strip()
    categorias = Categoria.objects.all()

    if query:
        categorias = categorias.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    contexto = {
        'titulo_pagina': 'Categorías',
        'categorias': categorias,
        'query': query,
    }
    return render(request, 'gestion/categoria_listado.html', contexto)


@permiso_requerido('gestion.add_categoria')
def categoria_crear(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
            return redirect('gestion:categoria_listado')
    else:
        form = CategoriaForm()

    contexto = {
        'titulo_pagina': 'Agregar categoría',
        'accion': 'Agregar categoría',
        'form': form,
        'volver_url': reverse('gestion:categoria_listado'),
    }
    return render(request, 'gestion/categoria_form.html', contexto)


@permiso_requerido('gestion.change_categoria')
def categoria_editar(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect('gestion:categoria_listado')
    else:
        form = CategoriaForm(instance=categoria)

    contexto = {
        'titulo_pagina': f'Editar {categoria.nombre}',
        'accion': f'Modificar categoría: {categoria.nombre}',
        'form': form,
        'volver_url': reverse('gestion:categoria_listado'),
    }
    return render(request, 'gestion/categoria_form.html', contexto)


@permiso_requerido('gestion.delete_categoria')
def categoria_eliminar(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    if request.method == 'POST':
        nombre = categoria.nombre
        try:
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
        except ProtectedError:
            # La relación Actividad -> Categoria usa on_delete=PROTECT:
            # no se puede eliminar una categoría que tiene actividades.
            messages.error(
                request,
                f'No se puede eliminar "{nombre}": tiene actividades asociadas. '
                'Reasigna o elimina esas actividades primero.',
            )
        return redirect('gestion:categoria_listado')

    contexto = {
        'titulo_pagina': f'Eliminar {categoria.nombre}',
        'accion': f'Eliminar categoría: {categoria.nombre}',
        'categoria': categoria,
        'volver_url': reverse('gestion:categoria_listado'),
    }
    return render(request, 'gestion/categoria_eliminar.html', contexto)
