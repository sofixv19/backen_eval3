"""
Vistas de la app 'cargos' (Aplicación 3 — trabajo en equipo).

Tercer mantenedor del sistema: Cargos y Metas institucionales, a partir
del módulo que aportó Ignacio Sepúlveda, ahora con CRUD real y protegido
por perfiles/permisos (igual que Delegaciones y Categorías).
"""
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cuentas.decorators import permiso_requerido

from .forms import CargoFuncionForm, MetaProyectoForm
from .models import CargoFuncion, MetaProyecto


@permiso_requerido('cargos.view_cargofuncion')
def listado(request):
    query = request.GET.get('q', '').strip()
    cargos = CargoFuncion.objects.all()

    if query:
        cargos = cargos.filter(Q(nombre_cargo__icontains=query) | Q(descripcion__icontains=query))

    contexto = {
        'titulo_pagina': 'Cargos y metas',
        'cargos': cargos,
        'query': query,
    }
    return render(request, 'cargos/listado.html', contexto)


@permiso_requerido('cargos.view_cargofuncion')
def detalle(request, cargo_id):
    cargo = get_object_or_404(CargoFuncion, pk=cargo_id)

    contexto = {
        'titulo_pagina': cargo.nombre_cargo,
        'cargo': cargo,
        'metas': cargo.metas.all(),
    }
    return render(request, 'cargos/detalle.html', contexto)


@permiso_requerido('cargos.add_cargofuncion')
def crear(request):
    if request.method == 'POST':
        form = CargoFuncionForm(request.POST)
        if form.is_valid():
            cargo = form.save()
            messages.success(request, f'Cargo "{cargo.nombre_cargo}" creado correctamente.')
            return redirect('cargos:detalle', cargo_id=cargo.pk)
    else:
        form = CargoFuncionForm()

    contexto = {
        'titulo_pagina': 'Agregar cargo',
        'accion': 'Agregar cargo',
        'form': form,
        'volver_url': reverse('cargos:listado'),
    }
    return render(request, 'cargos/form.html', contexto)


@permiso_requerido('cargos.change_cargofuncion')
def editar(request, cargo_id):
    cargo = get_object_or_404(CargoFuncion, pk=cargo_id)

    if request.method == 'POST':
        form = CargoFuncionForm(request.POST, instance=cargo)
        if form.is_valid():
            cargo = form.save()
            messages.success(request, f'Cargo "{cargo.nombre_cargo}" actualizado correctamente.')
            return redirect('cargos:detalle', cargo_id=cargo.pk)
    else:
        form = CargoFuncionForm(instance=cargo)

    contexto = {
        'titulo_pagina': f'Editar {cargo.nombre_cargo}',
        'accion': f'Modificar cargo: {cargo.nombre_cargo}',
        'form': form,
        'volver_url': reverse('cargos:detalle', args=[cargo.pk]),
    }
    return render(request, 'cargos/form.html', contexto)


@permiso_requerido('cargos.delete_cargofuncion')
def eliminar(request, cargo_id):
    cargo = get_object_or_404(CargoFuncion, pk=cargo_id)

    if request.method == 'POST':
        nombre = cargo.nombre_cargo
        try:
            cargo.delete()
        except ProtectedError:
            # Funcionario -> Cargo usa on_delete=PROTECT.
            messages.error(
                request,
                f'No se puede eliminar "{nombre}": hay funcionarios con este cargo. '
                'Cámbiales el cargo o elimínalos primero.',
            )
            return redirect('cargos:detalle', cargo_id=cargo.pk)
        messages.success(request, f'Cargo "{nombre}" eliminado correctamente (junto con sus metas asociadas).')
        return redirect('cargos:listado')

    contexto = {
        'titulo_pagina': f'Eliminar {cargo.nombre_cargo}',
        'accion': f'Eliminar cargo: {cargo.nombre_cargo}',
        'cargo': cargo,
        'volver_url': reverse('cargos:detalle', args=[cargo.pk]),
    }
    return render(request, 'cargos/eliminar.html', contexto)


# ---------------------------------------------------------------------------
# Metas institucionales: mantenedor completo (crear, buscar, listar,
# modificar y eliminar). También se pueden agregar desde la ficha de un cargo.
# ---------------------------------------------------------------------------

@permiso_requerido('cargos.view_metaproyecto')
def metas_listado(request):
    metas = MetaProyecto.objects.select_related('cargo')

    query = request.GET.get('q', '').strip()
    if query:
        metas = metas.filter(
            Q(item_medible__icontains=query)
            | Q(valor_objetivo__icontains=query)
            | Q(cargo__nombre_cargo__icontains=query)
        )

    cargo_id = request.GET.get('cargo', '')
    if cargo_id.isdigit():
        metas = metas.filter(cargo_id=int(cargo_id))

    contexto = {
        'titulo_pagina': 'Metas institucionales',
        'metas': metas,
        'query': query,
        'cargos': CargoFuncion.objects.order_by('nombre_cargo'),
        'cargo_seleccionado': cargo_id,
    }
    return render(request, 'cargos/metas_listado.html', contexto)


@permiso_requerido('cargos.add_metaproyecto')
def meta_crear(request, cargo_id=None):
    cargo = get_object_or_404(CargoFuncion, pk=cargo_id) if cargo_id else None
    volver_url = reverse('cargos:detalle', args=[cargo.pk]) if cargo else reverse('cargos:metas_listado')
    inicial = {'cargo': cargo} if cargo else {}

    if request.method == 'POST':
        form = MetaProyectoForm(request.POST, initial=inicial)
        if form.is_valid():
            meta = form.save()
            messages.success(request, f'Meta "{meta.item_medible}" registrada correctamente.')
            return redirect(volver_url)
    else:
        form = MetaProyectoForm(initial=inicial)

    contexto = {
        'titulo_pagina': 'Agregar meta',
        'accion': f'Agregar meta: {cargo.nombre_cargo}' if cargo else 'Agregar meta institucional',
        'form': form,
        'volver_url': volver_url,
    }
    return render(request, 'cargos/meta_form.html', contexto)


def _volver_meta(request, cargo_id):
    """Si se llegó desde el listado de metas (?desde=metas), se vuelve ahí;
    si no, a la ficha del cargo."""
    if request.GET.get('desde') == 'metas':
        return reverse('cargos:metas_listado')
    return reverse('cargos:detalle', args=[cargo_id])


@permiso_requerido('cargos.change_metaproyecto')
def meta_editar(request, meta_id):
    meta = get_object_or_404(MetaProyecto, pk=meta_id)

    if request.method == 'POST':
        form = MetaProyectoForm(request.POST, instance=meta)
        if form.is_valid():
            meta = form.save()
            messages.success(request, 'Meta actualizada correctamente.')
            return redirect(_volver_meta(request, meta.cargo_id))
    else:
        form = MetaProyectoForm(instance=meta)

    contexto = {
        'titulo_pagina': f'Editar meta: {meta.item_medible}',
        'accion': f'Modificar meta: {meta.item_medible}',
        'form': form,
        'volver_url': _volver_meta(request, meta.cargo_id),
    }
    return render(request, 'cargos/meta_form.html', contexto)


@permiso_requerido('cargos.delete_metaproyecto')
def meta_eliminar(request, meta_id):
    meta = get_object_or_404(MetaProyecto, pk=meta_id)
    volver_url = _volver_meta(request, meta.cargo_id)

    if request.method == 'POST':
        meta.delete()
        messages.success(request, 'Meta eliminada correctamente.')
        return redirect(volver_url)

    contexto = {
        'titulo_pagina': f'Eliminar meta: {meta.item_medible}',
        'accion': f'Eliminar meta: {meta.item_medible}',
        'meta': meta,
        'volver_url': volver_url,
    }
    return render(request, 'cargos/meta_eliminar.html', contexto)
