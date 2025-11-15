"""
Vistas del módulo de Producción - Estado de Granja, Producción de Huevos y Mortalidad.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from core.models import FarmStatus, EggProduction, MortalityEvent
from core.forms import FarmStatusForm, EggProductionForm, MortalityEventForm
from core.decorators import production_write_required


# ============================================================================
# ESTADO DE GRANJA
# ============================================================================

@login_required
def farm_status_list(request):
    """Muestra la lista de estados de granja."""
    farm_statuses = FarmStatus.objects.filter(is_active=True).order_by('-status_date')
    paginator = Paginator(farm_statuses, 20)
    page = request.GET.get('page')
    farm_statuses = paginator.get_page(page)
    return render(request, 'farm_status/list.html', {'farm_statuses': farm_statuses})


@login_required
@production_write_required
def farm_status_create(request):
    """Crear nuevo estado de granja."""
    if request.method == 'POST':
        form = FarmStatusForm(request.POST)
        if form.is_valid():
            farm_status = form.save(commit=False)
            farm_status.created_by = request.user.id
            farm_status.save()
            messages.success(request, 'Estado de granja creado exitosamente')
            return redirect('farm_status_list')
    else:
        form = FarmStatusForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Estado de Granja',
        'cancel_url': 'farm_status_list',
        'icon': 'bi-clipboard-data'
    }
    return render(request, 'farm_status/form.html', context)


@login_required
@production_write_required
def farm_status_edit(request, pk):
    """Editar estado de granja existente."""
    farm_status = get_object_or_404(FarmStatus, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = FarmStatusForm(request.POST, instance=farm_status)
        if form.is_valid():
            farm_status = form.save(commit=False)
            farm_status.updated_by = request.user.id
            farm_status.save()
            messages.success(request, 'Estado de granja actualizado exitosamente')
            return redirect('farm_status_list')
    else:
        form = FarmStatusForm(instance=farm_status)
    
    context = {
        'form': form,
        'title': 'Editar Estado de Granja',
        'cancel_url': 'farm_status_list',
        'icon': 'bi-clipboard-data'
    }
    return render(request, 'farm_status/form.html', context)


@login_required
@production_write_required
def farm_status_delete(request, pk):
    """Eliminar estado de granja (soft delete)."""
    farm_status = get_object_or_404(FarmStatus, pk=pk, is_active=True)
    farm_status.is_active = False
    farm_status.updated_by = request.user.id
    farm_status.save()
    messages.success(request, 'Estado de granja eliminado exitosamente')
    return redirect('farm_status_list')


# ============================================================================
# PRODUCCIÓN DE HUEVOS
# ============================================================================

@login_required
def egg_production_list(request):
    """Muestra la lista de producción de huevos."""
    productions = EggProduction.objects.filter(is_active=True).order_by('-production_date', 'size_code')
    paginator = Paginator(productions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Producción de Huevos'
    }
    return render(request, 'egg_production/list.html', context)


@login_required
@production_write_required
def egg_production_create(request):
    """Crear nuevo registro de producción de huevos."""
    if request.method == 'POST':
        form = EggProductionForm(request.POST)
        if form.is_valid():
            production = form.save(commit=False)
            production.created_by = request.user.id
            production.save()
            messages.success(request, 'Producción creada exitosamente')
            return redirect('egg_production_list')
    else:
        form = EggProductionForm()
    
    context = {
        'form': form,
        'title': 'Nueva Producción de Huevos',
        'cancel_url': 'egg_production_list',
        'icon': 'bi-egg-fried'
    }
    return render(request, 'egg_production/form.html', context)


@login_required
@production_write_required
def egg_production_edit(request, pk):
    """Editar registro de producción de huevos."""
    production = get_object_or_404(EggProduction, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = EggProductionForm(request.POST, instance=production)
        if form.is_valid():
            production = form.save(commit=False)
            production.updated_by = request.user.id
            production.save()
            messages.success(request, 'Producción actualizada exitosamente')
            return redirect('egg_production_list')
    else:
        form = EggProductionForm(instance=production)
    
    context = {
        'form': form,
        'title': 'Editar Producción de Huevos',
        'cancel_url': 'egg_production_list',
        'icon': 'bi-egg-fried'
    }
    return render(request, 'egg_production/form.html', context)


@login_required
@production_write_required
def egg_production_delete(request, pk):
    """Eliminar registro de producción (soft delete)."""
    production = get_object_or_404(EggProduction, pk=pk, is_active=True)
    production.is_active = False
    production.updated_by = request.user.id
    production.save()
    messages.success(request, 'Producción eliminada exitosamente')
    return redirect('egg_production_list')


# ============================================================================
# MORTALIDAD
# ============================================================================

@login_required
def mortality_list(request):
    """Muestra la lista de eventos de mortalidad."""
    events = MortalityEvent.objects.filter(is_active=True).order_by('-event_date')
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mortality/list.html', {'events': page_obj})


@login_required
@production_write_required
def mortality_create(request):
    """Crear evento de mortalidad."""
    if request.method == 'POST':
        form = MortalityEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user.id
            event.save()
            messages.success(request, 'Evento de mortalidad creado exitosamente')
            return redirect('mortality_list')
    else:
        form = MortalityEventForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Evento de Mortalidad',
        'cancel_url': 'mortality_list',
        'icon': 'bi-exclamation-triangle'
    }
    return render(request, 'mortality/form.html', context)


@login_required
@production_write_required
def mortality_edit(request, pk):
    """Editar evento de mortalidad."""
    event = get_object_or_404(MortalityEvent, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = MortalityEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.updated_by = request.user.id
            event.save()
            messages.success(request, 'Evento de mortalidad actualizado exitosamente')
            return redirect('mortality_list')
    else:
        form = MortalityEventForm(instance=event)
    
    context = {
        'form': form,
        'title': 'Editar Evento de Mortalidad',
        'cancel_url': 'mortality_list',
        'icon': 'bi-exclamation-triangle'
    }
    return render(request, 'mortality/form.html', context)


@login_required
@production_write_required
def mortality_delete(request, pk):
    """Eliminar evento de mortalidad (soft delete)."""
    event = get_object_or_404(MortalityEvent, pk=pk, is_active=True)
    event.is_active = False
    event.updated_by = request.user.id
    event.save()
    messages.success(request, 'Evento de mortalidad eliminado exitosamente')
    return redirect('mortality_list')
