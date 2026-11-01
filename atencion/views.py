"""
Vistas de la app 'atencion':
- Mantenedor de Vecinos (crear, buscar, listar, modificar, eliminar).
- Tercera transacción: Solicitudes vecinales (registrar, listar, ver detalle
  y cerrar con respuesta).
"""
import uuid

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from cuentas.decorators import permiso_requerido

from .forms import CerrarSolicitudForm, SolicitudForm, VecinoForm
from .models import SolicitudVecinal, Vecino


# ---------------------------------------------------------------------------
# Mantenedor de Vecinos
# ---------------------------------------------------------------------------

@permiso_requerido('atencion.view_vecino')
def vecinos_listado(request):
    vecinos = Vecino.objects.select_related('delegacion')
    query = request.GET.get('q', '').strip()
    if query:
        vecinos = vecinos.filter(
            Q(nombre__icontains=query)
            | Q(rut__icontains=query)
            | Q(direccion__icontains=query)
            | Q(delegacion__nombre__icontains=query)
        )

    contexto = {'titulo_pagina': 'Vecinos', 'vecinos': vecinos, 'query': query}
    return render(request, 'atencion/vecinos_listado.html', contexto)


@permiso_requerido('atencion.add_vecino')
def vecino_crear(request):
    if request.method == 'POST':
        form = VecinoForm(request.POST)
        if form.is_valid():
            vecino = form.save()
            messages.success(request, f'Vecino/a "{vecino.nombre}" registrado/a correctamente.')
            return redirect('atencion:vecinos_listado')
    else:
        form = VecinoForm()

    contexto = {
        'titulo_pagina': 'Agregar vecino',
        'accion': 'Agregar vecino/a',
        'form': form,
        'volver_url': reverse('atencion:vecinos_listado'),
    }
    return render(request, 'atencion/form.html', contexto)


@permiso_requerido('atencion.change_vecino')
def vecino_editar(request, vecino_id):
    vecino = get_object_or_404(Vecino, pk=vecino_id)
    if request.method == 'POST':
        form = VecinoForm(request.POST, instance=vecino)
        if form.is_valid():
            vecino = form.save()
            messages.success(request, f'Vecino/a "{vecino.nombre}" actualizado/a correctamente.')
            return redirect('atencion:vecinos_listado')
    else:
        form = VecinoForm(instance=vecino)

    contexto = {
        'titulo_pagina': f'Editar {vecino.nombre}',
        'accion': f'Modificar vecino/a: {vecino.nombre}',
        'form': form,
        'volver_url': reverse('atencion:vecinos_listado'),
    }
    return render(request, 'atencion/form.html', contexto)


@permiso_requerido('atencion.delete_vecino')
def vecino_eliminar(request, vecino_id):
    vecino = get_object_or_404(Vecino, pk=vecino_id)
    if request.method == 'POST':
        nombre = vecino.nombre
        try:
            vecino.delete()
            messages.success(request, f'Vecino/a "{nombre}" eliminado/a correctamente.')
        except ProtectedError:
            messages.error(request, f'No se puede eliminar a "{nombre}": tiene solicitudes registradas.')
        return redirect('atencion:vecinos_listado')

    contexto = {
        'titulo_pagina': f'Eliminar {vecino.nombre}',
        'accion': f'Eliminar vecino/a: {vecino.nombre}',
        'aviso': (
            f'Tiene {vecino.solicitudes.count()} solicitud(es) registrada(s), por lo que no podrá eliminarse.'
            if vecino.solicitudes.exists() else ''
        ),
        'volver_url': reverse('atencion:vecinos_listado'),
    }
    return render(request, 'atencion/eliminar.html', contexto)


# ---------------------------------------------------------------------------
# Tercera transacción: Solicitudes vecinales
# ---------------------------------------------------------------------------

@permiso_requerido('atencion.view_solicitudvecinal')
def solicitudes_listado(request):
    solicitudes = SolicitudVecinal.objects.select_related('vecino', 'delegacion', 'funcionario')

    estado = request.GET.get('estado', '')
    if estado in SolicitudVecinal.Estado.values:
        solicitudes = solicitudes.filter(estado=estado)

    query = request.GET.get('q', '').strip()
    if query:
        solicitudes = solicitudes.filter(
            Q(codigo__icontains=query)
            | Q(vecino__nombre__icontains=query)
            | Q(vecino__rut__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(funcionario__nombre__icontains=query)
        )

    contexto = {
        'titulo_pagina': 'Solicitudes vecinales',
        'solicitudes': solicitudes,
        'estados': SolicitudVecinal.Estado.values,
        'estado_seleccionado': estado,
        'query': query,
    }
    return render(request, 'atencion/solicitudes_listado.html', contexto)


@permiso_requerido('atencion.add_solicitudvecinal')
def solicitud_crear(request):
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                solicitud = form.save(commit=False)
                solicitud.registrada_por = request.user
                solicitud.codigo = f'TMP-{uuid.uuid4().hex[:12]}'
                solicitud.save()
                # El código definitivo se arma con el id asignado por la BD.
                solicitud.codigo = f'SOL-{solicitud.pk:05d}'
                solicitud.save(update_fields=['codigo'])
            messages.success(
                request,
                f'Solicitud {solicitud.codigo} registrada y asignada a {solicitud.funcionario.nombre}.',
            )
            return redirect(solicitud.get_absolute_url())
    else:
        inicial = {}
        vecino_id = request.GET.get('vecino', '')
        if vecino_id.isdigit():
            vecino = Vecino.objects.filter(pk=int(vecino_id)).first()
            if vecino:
                inicial = {'vecino': vecino, 'delegacion': vecino.delegacion}
        form = SolicitudForm(initial=inicial)

    contexto = {
        'titulo_pagina': 'Registrar solicitud vecinal',
        'form': form,
    }
    return render(request, 'atencion/solicitud_form.html', contexto)


@permiso_requerido('atencion.view_solicitudvecinal')
def solicitud_detalle(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudVecinal.objects.select_related('vecino', 'delegacion', 'funcionario__cargo', 'registrada_por'),
        pk=solicitud_id,
    )
    contexto = {
        'titulo_pagina': f'Solicitud {solicitud.codigo}',
        'solicitud': solicitud,
        'form_cierre': CerrarSolicitudForm(),
    }
    return render(request, 'atencion/solicitud_detalle.html', contexto)


@permiso_requerido('atencion.change_solicitudvecinal')
def solicitud_cerrar(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudVecinal, pk=solicitud_id)
    if request.method != 'POST':
        return redirect(solicitud.get_absolute_url())

    if solicitud.estado == SolicitudVecinal.Estado.CERRADA:
        messages.warning(request, f'La solicitud {solicitud.codigo} ya estaba cerrada.')
        return redirect(solicitud.get_absolute_url())

    form = CerrarSolicitudForm(request.POST)
    if form.is_valid():
        solicitud.estado = SolicitudVecinal.Estado.CERRADA
        solicitud.respuesta = form.cleaned_data['respuesta']
        solicitud.fecha_cierre = timezone.now()
        solicitud.save(update_fields=['estado', 'respuesta', 'fecha_cierre'])
        messages.success(request, f'Solicitud {solicitud.codigo} cerrada correctamente.')
        return redirect(solicitud.get_absolute_url())

    contexto = {
        'titulo_pagina': f'Solicitud {solicitud.codigo}',
        'solicitud': solicitud,
        'form_cierre': form,
    }
    return render(request, 'atencion/solicitud_detalle.html', contexto)
