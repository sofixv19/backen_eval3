"""
Vistas de la app 'funcionarios' — cuarto mantenedor del sistema
(crear, buscar, listar, modificar y eliminar), protegido por permisos.
"""
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cuentas.decorators import permiso_requerido
from delegaciones.models import Delegacion

from .forms import FuncionarioForm
from .models import Funcionario


@permiso_requerido('funcionarios.view_funcionario')
def listado(request):
    funcionarios = Funcionario.objects.select_related('delegacion', 'cargo')

    query = request.GET.get('q', '').strip()
    if query:
        funcionarios = funcionarios.filter(
            Q(nombre__icontains=query)
            | Q(rut__icontains=query)
            | Q(email__icontains=query)
            | Q(cargo__nombre_cargo__icontains=query)
        )

    delegacion_id = request.GET.get('delegacion', '')
    if delegacion_id.isdigit():
        funcionarios = funcionarios.filter(delegacion_id=int(delegacion_id))

    contexto = {
        'titulo_pagina': 'Funcionarios',
        'funcionarios': funcionarios,
        'query': query,
        'delegaciones': Delegacion.objects.order_by('nombre'),
        'delegacion_seleccionada': delegacion_id,
    }
    return render(request, 'funcionarios/listado.html', contexto)


@permiso_requerido('funcionarios.add_funcionario')
def crear(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            funcionario = form.save()
            messages.success(request, f'Funcionario "{funcionario.nombre}" registrado correctamente.')
            return redirect('funcionarios:listado')
    else:
        form = FuncionarioForm()

    contexto = {
        'titulo_pagina': 'Agregar funcionario',
        'accion': 'Agregar funcionario',
        'form': form,
        'volver_url': reverse('funcionarios:listado'),
    }
    return render(request, 'funcionarios/form.html', contexto)


@permiso_requerido('funcionarios.change_funcionario')
def editar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            funcionario = form.save()
            messages.success(request, f'Funcionario "{funcionario.nombre}" actualizado correctamente.')
            return redirect('funcionarios:listado')
    else:
        form = FuncionarioForm(instance=funcionario)

    contexto = {
        'titulo_pagina': f'Editar {funcionario.nombre}',
        'accion': f'Modificar funcionario: {funcionario.nombre}',
        'form': form,
        'volver_url': reverse('funcionarios:listado'),
    }
    return render(request, 'funcionarios/form.html', contexto)


@permiso_requerido('funcionarios.delete_funcionario')
def eliminar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)

    if request.method == 'POST':
        nombre = funcionario.nombre
        try:
            funcionario.delete()
            messages.success(request, f'Funcionario "{nombre}" eliminado correctamente.')
        except ProtectedError:
            # SolicitudVecinal -> Funcionario usa on_delete=PROTECT.
            messages.error(
                request,
                f'No se puede eliminar a "{nombre}": tiene solicitudes vecinales asignadas. '
                'Puedes marcarlo como inactivo en "Modificar".',
            )
        return redirect('funcionarios:listado')

    total_solicitudes = funcionario.solicitudes.count()
    contexto = {
        'titulo_pagina': f'Eliminar {funcionario.nombre}',
        'accion': f'Eliminar funcionario: {funcionario.nombre}',
        'aviso': (
            f'Tiene {total_solicitudes} solicitud(es) vecinal(es) asignada(s), por lo que no podrá eliminarse.'
            if total_solicitudes else ''
        ),
        'volver_url': reverse('funcionarios:listado'),
    }
    return render(request, 'funcionarios/eliminar.html', contexto)
