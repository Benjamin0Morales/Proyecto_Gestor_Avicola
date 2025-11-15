"""
Vistas del módulo de Alimentación - Items, Mezclas y Consumo de Alimento.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from core.models import FeedItem, FeedInventory, FeedInventoryMovement, FeedMix, FeedConsumption
from core.forms import FeedItemForm, FeedInventoryMovementForm, FeedMixForm, FeedConsumptionForm
from core.decorators import production_write_required
from django.db.models import Sum
from django.utils import timezone


# ============================================================================
# ITEMS DE ALIMENTO
# ============================================================================

@login_required
def feed_item_list(request):
    """Muestra la lista de items de alimento."""
    items = FeedItem.objects.filter(is_active=True).order_by('item_name')
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'feed_item/list.html', {'items': page_obj})


@login_required
@production_write_required
def feed_item_create(request):
    """Crear item de alimento."""
    if request.method == 'POST':
        form = FeedItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user.id
            item.save()
            messages.success(request, 'Item de alimento creado exitosamente')
            return redirect('feed_item_list')
    else:
        form = FeedItemForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Item de Alimento',
        'cancel_url': 'feed_item_list',
        'icon': 'bi-box'
    }
    return render(request, 'feed_item/form.html', context)


@login_required
@production_write_required
def feed_item_edit(request, pk):
    """Editar item de alimento."""
    item = get_object_or_404(FeedItem, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = FeedItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.updated_by = request.user.id
            item.save()
            messages.success(request, 'Item de alimento actualizado exitosamente')
            return redirect('feed_item_list')
    else:
        form = FeedItemForm(instance=item)
    
    context = {
        'form': form,
        'title': 'Editar Item de Alimento',
        'cancel_url': 'feed_item_list',
        'icon': 'bi-box'
    }
    return render(request, 'feed_item/form.html', context)


@login_required
@production_write_required
def feed_item_delete(request, pk):
    """Eliminar item de alimento (soft delete)."""
    item = get_object_or_404(FeedItem, pk=pk, is_active=True)
    item.is_active = False
    item.updated_by = request.user.id
    item.save()
    messages.success(request, 'Item de alimento eliminado exitosamente')
    return redirect('feed_item_list')


# ============================================================================
# MEZCLAS DE ALIMENTO
# ============================================================================

@login_required
def feed_mix_list(request):
    """Muestra la lista de mezclas de alimento."""
    mixes = FeedMix.objects.filter(is_active=True).order_by('-mix_date')
    paginator = Paginator(mixes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'feed_mix/list.html', {'mixes': page_obj})


@login_required
@production_write_required
def feed_mix_create(request):
    """Crear mezcla de alimento con items disponibles."""
    # Obtener items con inventario disponible
    available_items = FeedItem.objects.filter(
        is_active=True,
        inventory__quantity__gt=0
    ).select_related('inventory').order_by('item_name')
    
    if request.method == 'POST':
        form = FeedMixForm(request.POST)
        if form.is_valid():
            mix = form.save(commit=False)
            mix.created_by = request.user.id
            mix.save()
            
            # Procesar items de la mezcla
            total_weight = 0
            items_added = 0
            
            for item in available_items:
                # Obtener cantidad del POST
                quantity_key = f'item_{item.pk}_quantity'
                quantity = request.POST.get(quantity_key, '0')
                
                try:
                    from decimal import Decimal
                    quantity = Decimal(str(quantity))
                    if quantity > 0:
                        # Verificar stock disponible
                        if item.inventory.quantity >= quantity:
                            # Crear FeedMixItem
                            from core.models import FeedMixItem
                            FeedMixItem.objects.create(
                                feed_mix=mix,
                                feed_item=item,
                                weight_kg=quantity,
                                proportion_pct=0,  # Se calculará después
                                created_by=request.user.id
                            )
                            
                            # Descontar del inventario
                            item.inventory.quantity -= quantity
                            item.inventory.updated_by = request.user.id
                            item.inventory.save()
                            
                            # Registrar movimiento
                            FeedInventoryMovement.objects.create(
                                feed_item=item,
                                movement_type='usage',
                                quantity=quantity,
                                unit_type=item.unit_type,
                                movement_date=mix.mix_date,
                                reference=f'Mezcla del {mix.mix_date}',
                                created_by=request.user.id
                            )
                            
                            total_weight += float(quantity)
                            items_added += 1
                        else:
                            messages.warning(request, f'Stock insuficiente de {item.item_name}. Disponible: {item.inventory.quantity} kg')
                except (ValueError, AttributeError, TypeError):
                    pass
            
            # Actualizar peso total y proporciones
            if total_weight > 0:
                mix.total_weight_kg = total_weight
                mix.save()
                
                # Calcular proporciones
                from core.models import FeedMixItem
                mix_items = FeedMixItem.objects.filter(feed_mix=mix)
                for mix_item in mix_items:
                    mix_item.proportion_pct = (mix_item.weight_kg / total_weight) * 100
                    mix_item.save()
                
                # Crear item de mezcla en el catálogo si no existe
                from decimal import Decimal
                import datetime
                
                # Crear nombre único para la mezcla
                timestamp = datetime.datetime.now().strftime('%H:%M')
                mix_name = f"Mezcla {mix.mix_date.strftime('%d/%m/%Y')} {timestamp}"
                if mix.description:
                    mix_name = f"{mix.description} ({mix.mix_date.strftime('%d/%m/%Y')} {timestamp})"
                
                # Calcular costo promedio de la mezcla
                total_cost = Decimal('0')
                for mix_item in mix_items:
                    item_cost = mix_item.feed_item.unit_cost_clp * mix_item.weight_kg
                    total_cost += item_cost
                
                unit_cost = total_cost / Decimal(str(total_weight)) if total_weight > 0 else Decimal('0')
                
                # Crear o actualizar el item de mezcla
                mix_feed_item, created = FeedItem.objects.get_or_create(
                    item_name=mix_name,
                    defaults={
                        'supplier_name': 'Producción Propia',
                        'unit_cost_clp': unit_cost,
                        'unit_type': 'kg',
                        'created_by': request.user.id
                    }
                )
                
                if not created:
                    # Si ya existe, actualizar el costo
                    mix_feed_item.unit_cost_clp = unit_cost
                    mix_feed_item.updated_by = request.user.id
                    mix_feed_item.save()
                
                # Agregar la mezcla al inventario
                mix_inventory, inv_created = FeedInventory.objects.get_or_create(
                    feed_item=mix_feed_item,
                    defaults={
                        'quantity': Decimal(str(total_weight)),
                        'unit_type': 'kg',
                        'created_by': request.user.id
                    }
                )
                
                if not inv_created:
                    # Si ya existe, sumar la cantidad
                    mix_inventory.quantity += Decimal(str(total_weight))
                    mix_inventory.updated_by = request.user.id
                    mix_inventory.save()
                
                # Registrar movimiento de entrada de la mezcla
                FeedInventoryMovement.objects.create(
                    feed_item=mix_feed_item,
                    movement_type='purchase',
                    quantity=Decimal(str(total_weight)),
                    unit_type='kg',
                    movement_date=mix.mix_date,
                    reference=f'Producción de mezcla',
                    unit_cost_clp=unit_cost,
                    created_by=request.user.id
                )
            
            if items_added > 0:
                messages.success(request, f'Mezcla creada con {items_added} items ({total_weight} kg total) y agregada al inventario')
            else:
                messages.warning(request, 'Mezcla creada pero sin items agregados')
            
            return redirect('feed_mix_list')
    else:
        form = FeedMixForm()
    
    context = {
        'form': form,
        'available_items': available_items,
        'title': 'Nueva Mezcla de Alimento',
        'cancel_url': 'feed_mix_list',
        'icon': 'bi-diagram-3'
    }
    return render(request, 'feed_mix/form.html', context)


@login_required
def feed_mix_edit(request, pk):
    """Ver detalle de mezcla de alimento (solo lectura)."""
    mix = get_object_or_404(FeedMix, pk=pk, is_active=True)
    
    # Obtener items de la mezcla
    from core.models import FeedMixItem
    mix_items = FeedMixItem.objects.filter(feed_mix=mix, is_active=True).select_related('feed_item')
    
    context = {
        'mix': mix,
        'mix_items': mix_items,
        'title': 'Detalle de Mezcla',
        'cancel_url': 'feed_mix_list',
        'icon': 'bi-diagram-3'
    }
    return render(request, 'feed_mix/detail.html', context)


@login_required
def feed_mix_delete(request, pk):
    """Eliminar mezcla de alimento (soft delete - solo admin)."""
    # Verificar que sea admin
    if request.user.role != 'admin':
        messages.error(request, 'Solo administradores pueden eliminar registros de mezclas')
        return redirect('feed_mix_list')
    
    mix = get_object_or_404(FeedMix, pk=pk, is_active=True)
    mix.is_active = False
    mix.updated_by = request.user.id
    mix.save()
    messages.warning(request, f'Registro de mezcla eliminado por admin: {mix.mix_date}')
    return redirect('feed_mix_list')


# ============================================================================
# CONSUMO DE ALIMENTO
# ============================================================================

@login_required
def feed_consumption_list(request):
    """Muestra la lista de registros de consumo."""
    consumptions = FeedConsumption.objects.filter(is_active=True).order_by('-consumption_date')
    paginator = Paginator(consumptions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'feed_consumption/list.html', {'consumptions': page_obj})


@login_required
@production_write_required
def feed_consumption_create(request):
    """Crear registro de consumo de alimento."""
    if request.method == 'POST':
        form = FeedConsumptionForm(request.POST)
        if form.is_valid():
            consumption = form.save(commit=False)
            consumption.created_by = request.user.id
            consumption.save()
            messages.success(request, 'Consumo de alimento creado exitosamente')
            return redirect('feed_consumption_list')
    else:
        form = FeedConsumptionForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Consumo de Alimento',
        'cancel_url': 'feed_consumption_list',
        'icon': 'bi-graph-down'
    }
    return render(request, 'feed_consumption/form.html', context)


@login_required
@production_write_required
def feed_consumption_edit(request, pk):
    """Editar registro de consumo de alimento."""
    consumption = get_object_or_404(FeedConsumption, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = FeedConsumptionForm(request.POST, instance=consumption)
        if form.is_valid():
            consumption = form.save(commit=False)
            consumption.updated_by = request.user.id
            consumption.save()
            messages.success(request, 'Consumo de alimento actualizado exitosamente')
            return redirect('feed_consumption_list')
    else:
        form = FeedConsumptionForm(instance=consumption)
    
    context = {
        'form': form,
        'title': 'Editar Consumo de Alimento',
        'cancel_url': 'feed_consumption_list',
        'icon': 'bi-graph-down'
    }
    return render(request, 'feed_consumption/form.html', context)


@login_required
@production_write_required
def feed_consumption_delete(request, pk):
    """Eliminar registro de consumo (soft delete)."""
    consumption = get_object_or_404(FeedConsumption, pk=pk, is_active=True)
    consumption.is_active = False
    consumption.updated_by = request.user.id
    consumption.save()
    messages.success(request, 'Consumo de alimento eliminado exitosamente')
    return redirect('feed_consumption_list')


# ============================================================================
# INVENTARIO DE ALIMENTOS
# ============================================================================

@login_required
def feed_inventory_list(request):
    """Muestra el inventario actual de todos los items."""
    # Obtener todos los items con su inventario
    items = FeedItem.objects.filter(is_active=True).select_related('inventory').order_by('item_name')
    
    # Crear inventario para items que no lo tengan
    for item in items:
        if not hasattr(item, 'inventory'):
            FeedInventory.objects.create(
                feed_item=item,
                quantity=0,
                unit_type=item.unit_type,
                created_by=request.user.id
            )
    
    # Recargar con inventario
    items = FeedItem.objects.filter(is_active=True).select_related('inventory').order_by('item_name')
    
    context = {
        'items': items,
        'title': 'Inventario de Alimentos'
    }
    return render(request, 'feed_inventory/list.html', context)


@login_required
def feed_inventory_movements(request):
    """Muestra el historial de movimientos de inventario."""
    movements = FeedInventoryMovement.objects.filter(
        is_active=True
    ).select_related('feed_item').order_by('-movement_date', '-created_at')
    
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'feed_inventory/movements.html', {'movements': page_obj})


@login_required
@production_write_required
def feed_inventory_movement_create(request):
    """Registrar movimiento de inventario (compra, ajuste, etc)."""
    # Obtener todos los items para mostrar info de precios
    feed_items = FeedItem.objects.filter(is_active=True).order_by('item_name')
    items_data = {}
    for item in feed_items:
        items_data[item.pk] = {
            'name': item.item_name,
            'unit_type': item.get_unit_type_display(),
            'unit_cost': float(item.unit_cost_clp)
        }
    
    if request.method == 'POST':
        form = FeedInventoryMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user.id
            
            # Obtener el item y su unidad
            feed_item = movement.feed_item
            movement.unit_type = feed_item.unit_type
            
            # Si no se especificó costo unitario, usar el del item
            if not movement.unit_cost_clp and movement.movement_type == 'purchase':
                movement.unit_cost_clp = feed_item.unit_cost_clp
            
            # Guardar el movimiento
            movement.save()
            
            # Actualizar o crear inventario
            inventory, created = FeedInventory.objects.get_or_create(
                feed_item=feed_item,
                defaults={
                    'quantity': 0,
                    'unit_type': feed_item.unit_type,
                    'created_by': request.user.id
                }
            )
            
            # Actualizar cantidad según tipo de movimiento
            if movement.movement_type == 'purchase':
                # Compras suman
                inventory.quantity += abs(movement.quantity)
            elif movement.movement_type in ['usage', 'waste']:
                # Uso y desperdicio restan
                inventory.quantity -= abs(movement.quantity)
                # Evitar negativos
                if inventory.quantity < 0:
                    inventory.quantity = 0
            
            inventory.updated_by = request.user.id
            inventory.save()
            
            # Calcular costo total
            total_cost = 0
            if movement.unit_cost_clp:
                total_cost = float(movement.quantity) * float(movement.unit_cost_clp)
            elif feed_item.unit_cost_clp:
                # Si no se especificó costo, usar el del item
                total_cost = float(movement.quantity) * float(feed_item.unit_cost_clp)
            
            # Si es desperdicio, registrar pérdida financiera
            if movement.movement_type == 'waste' and total_cost > 0:
                from core.models import FinanceCategory, FinanceTransaction
                from decimal import Decimal
                
                # Buscar o crear categoría de desperdicios
                waste_category, created = FinanceCategory.objects.get_or_create(
                    category_name='Desperdicios de Alimento',
                    defaults={
                        'type': 'expense',
                        'description': 'Pérdidas por desperdicio de alimento',
                        'created_by': request.user.id
                    }
                )
                
                # Crear transacción financiera de pérdida
                FinanceTransaction.objects.create(
                    category=waste_category,
                    transaction_date=movement.movement_date,
                    amount_clp=Decimal(str(total_cost)),
                    payment_method='N/A',
                    reference_doc=f'Desperdicio-{movement.id}',
                    description=f'Pérdida por desperdicio de {movement.quantity} {movement.unit_type} de {feed_item.item_name}',
                    created_by=request.user.id
                )
                
                messages.warning(request, f'Desperdicio registrado: {movement.get_movement_type_display()} - Pérdida: ${total_cost:,.0f}')
            elif total_cost > 0:
                messages.success(request, f'Movimiento registrado: {movement.get_movement_type_display()} - Total: ${total_cost:,.0f}')
            else:
                messages.success(request, f'Movimiento registrado: {movement.get_movement_type_display()}')
            
            return redirect('feed_inventory_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = FeedInventoryMovementForm()
    
    import json
    context = {
        'form': form,
        'items_data_json': json.dumps(items_data),
        'title': 'Registrar Movimiento de Inventario',
        'cancel_url': 'feed_inventory_list',
        'icon': 'bi-arrow-left-right'
    }
    return render(request, 'feed_inventory/movement_form.html', context)
