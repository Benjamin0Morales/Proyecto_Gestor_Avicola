"""
Vistas para el módulo de visión por computadora
Maneja la carga de imágenes, procesamiento y confirmación de conteo automático
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import os
from datetime import datetime

from core.decorators import production_write_required
from core.forms import VisionCountForm
from core.models import EggProduction
from core.vision_service import EggCounterService


@login_required
@production_write_required
def vision_count_eggs(request):
    """Vista para subir imagen y procesar con visión."""
    if request.method == 'POST':
        form = VisionCountForm(request.POST, request.FILES)
        if form.is_valid():
            # Obtener datos del formulario
            image = form.cleaned_data['image']
            production_date = form.cleaned_data['production_date']
            size_code = form.cleaned_data['size_code']
            
            # Guardar imagen temporalmente
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_vision')
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"egg_count_{timestamp}.jpg"
            temp_path = os.path.join(temp_dir, filename)
            
            # Guardar archivo
            with open(temp_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # Procesar con visión (método mejorado con preprocesamiento)
            try:
                service = EggCounterService()
                result = service.count_eggs(temp_path)  # Método con mejor preprocesamiento
                
                if 'error' in result:
                    messages.error(request, f'Error al procesar imagen: {result["error"]}')
                    return redirect('vision_count_eggs')
                
                # Guardar resultado en sesión para confirmación
                request.session['vision_result'] = {
                    'count': result['count'],
                    'confidence': float(result['confidence']),
                    'production_date': str(production_date),
                    'size_code': size_code,
                    'temp_image_path': temp_path,
                    'processed_image_path': result['processed_image_path'],
                    'detections': result['detections']
                }
                
                return redirect('vision_confirm')
                
            except Exception as e:
                messages.error(request, f'Error al procesar imagen: {str(e)}')
                return redirect('vision_count_eggs')
    else:
        # Inicializar con fecha de hoy
        form = VisionCountForm(initial={'production_date': datetime.now().date()})
    
    context = {
        'form': form,
        'title': 'Conteo Automático con Visión',
        'icon': 'bi-camera'
    }
    return render(request, 'vision/count.html', context)


@login_required
@production_write_required
def vision_confirm(request):
    """Vista para confirmar o corregir el conteo automático."""
    # Obtener resultado de la sesión
    result = request.session.get('vision_result')
    
    if not result:
        messages.warning(request, 'No hay resultado de visión para confirmar')
        return redirect('vision_count_eggs')
    
    if request.method == 'POST':
        # Usuario confirma o corrige
        final_count = int(request.POST.get('quantity', result['count']))
        
        try:
            # Verificar si ya existe registro para esta fecha y tamaño
            existing = EggProduction.objects.filter(
                production_date=result['production_date'],
                size_code=result['size_code'],
                is_active=True
            ).first()
            
            if existing:
                # Actualizar registro existente
                existing.quantity = final_count
                existing.detected_count = result['count']
                existing.confidence_level = result['confidence']
                existing.source_method = 'vision'
                existing.is_validated = True
                existing.updated_by = request.user.id
                
                # Mover imagen a ubicación permanente
                if result.get('processed_image_path'):
                    existing.image = result['processed_image_path']
                
                existing.save()
                messages.success(request, 'Registro de producción actualizado con visión')
            else:
                # Crear nuevo registro
                production = EggProduction.objects.create(
                    production_date=result['production_date'],
                    size_code=result['size_code'],
                    quantity=final_count,
                    detected_count=result['count'],
                    confidence_level=result['confidence'],
                    source_method='vision',
                    is_validated=True,
                    image=result.get('processed_image_path'),
                    created_by=request.user.id
                )
                messages.success(request, 'Producción registrada exitosamente con visión')
            
            # Limpiar sesión
            del request.session['vision_result']
            
            return redirect('egg_production_list')
            
        except Exception as e:
            messages.error(request, f'Error al guardar registro: {str(e)}')
            return redirect('vision_confirm')
    
    # Preparar URL de imagen procesada para mostrar
    if result.get('processed_image_path'):
        result['processed_image_url'] = os.path.join(settings.MEDIA_URL, result['processed_image_path'])
    
    context = {
        'result': result,
        'title': 'Confirmar Conteo Automático',
        'icon': 'bi-check-circle'
    }
    return render(request, 'vision/confirm.html', context)


@login_required
@production_write_required
def vision_cancel(request):
    """Cancelar proceso de visión y limpiar sesión."""
    if 'vision_result' in request.session:
        # Limpiar archivos temporales si existen
        result = request.session['vision_result']
        if result.get('temp_image_path') and os.path.exists(result['temp_image_path']):
            try:
                os.remove(result['temp_image_path'])
            except:
                pass
        
        del request.session['vision_result']
    
    messages.info(request, 'Proceso de visión cancelado')
    return redirect('egg_production_list')
