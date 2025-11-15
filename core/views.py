"""
Vistas principales del sistema - Login, Logout y Dashboard.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json

from core.models import (
    User, FarmStatus, EggProduction, MortalityEvent,
    FeedItem, FeedMix, FeedConsumption, FinanceCategory, FinanceTransaction
)


def login_view(request):
    """Página de inicio de sesión."""
    # Si ya está logueado, ir al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Si envió el formulario
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Intentar autenticar
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login exitoso
            auth_login(request, user)
            messages.success(request, f'Bienvenido, {user.full_name}!')
            return redirect('dashboard')
        else:
            # Login fallido
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'login.html')


def logout_view(request):
    """Cerrar sesión."""
    auth_logout(request)
    messages.info(request, 'Sesión cerrada exitosamente')
    return redirect('web_login')


@login_required
def dashboard_view(request):
    """Dashboard principal con estadísticas y gráficos."""
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    week_ago = today - timedelta(days=7)
    
    # Daily Checklist - Check if today's records exist
    checklist = [
        {
            'name': 'Estado de Granja',
            'icon': 'bi-clipboard-data',
            'completed': FarmStatus.objects.filter(
                status_date=today,
                is_active=True
            ).exists(),
            'url': 'farm_status_create',
            'description': 'Registro diario del conteo de aves'
        },
        {
            'name': 'Producción de Huevos',
            'icon': 'bi-egg-fried',
            'completed': EggProduction.objects.filter(
                production_date=today,
                is_active=True
            ).exists(),
            'url': 'egg_production_create',
            'description': 'Registro de huevos producidos hoy'
        },
        {
            'name': 'Consumo de Alimento',
            'icon': 'bi-graph-down',
            'completed': FeedConsumption.objects.filter(
                consumption_date=today,
                is_active=True
            ).exists(),
            'url': 'feed_consumption_create',
            'description': 'Registro del alimento consumido'
        },
    ]
    
    # Count completed tasks
    completed_tasks = sum(1 for task in checklist if task['completed'])
    total_tasks = len(checklist)
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # ========================================================================
    # INDICADORES PRODUCTIVOS CLAVE
    # ========================================================================
    
    # Estado de granja actual
    latest_farm_status = FarmStatus.objects.filter(is_active=True).first()
    total_birds = latest_farm_status.total_birds if latest_farm_status else 0
    hens_count = latest_farm_status.hens_count if latest_farm_status else 0
    
    # 1. Producción total de huevos por día (HOY)
    eggs_today = EggProduction.objects.filter(
        production_date=today,
        is_active=True
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # 2. Porcentaje de postura = (Huevos producidos / Gallinas totales) × 100
    if hens_count > 0:
        porcentaje_postura = (eggs_today / hens_count) * 100
    else:
        porcentaje_postura = 0
    
    # 3. Consumo de alimento por período (última semana)
    consumo_semanal = FeedConsumption.objects.filter(
        consumption_date__gte=week_ago,
        consumption_date__lte=today,
        is_active=True
    ).aggregate(total=Sum('total_consumed_kg'))['total'] or 0
    
    # 4. Conversión alimenticia (kg de alimento por docena de huevos)
    # Producción semanal
    produccion_semanal = EggProduction.objects.filter(
        production_date__gte=week_ago,
        production_date__lte=today,
        is_active=True
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    docenas_semanales = produccion_semanal / 12 if produccion_semanal > 0 else 0
    
    if docenas_semanales > 0:
        # Convertir a float para evitar error de tipos
        conversion_alimenticia = float(consumo_semanal) / docenas_semanales
    else:
        conversion_alimenticia = 0
    
    # Mortalidad del mes
    mortality_month = MortalityEvent.objects.filter(
        event_date__gte=current_month_start,
        is_active=True
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # ========================================================================
    # INDICADORES FINANCIEROS CLAVE
    # ========================================================================
    
    # Transacciones del mes
    transactions = FinanceTransaction.objects.filter(
        transaction_date__gte=current_month_start,
        is_active=True
    ).select_related('category')
    
    # Ingresos y gastos del mes
    income_month = sum(t.amount_clp for t in transactions if t.category.type == 'income')
    expense_month = sum(t.amount_clp for t in transactions if t.category.type == 'expense')
    balance_month = income_month - expense_month
    
    # Ingresos y gastos de la semana
    transactions_week = FinanceTransaction.objects.filter(
        transaction_date__gte=week_ago,
        transaction_date__lte=today,
        is_active=True
    ).select_related('category')
    
    income_week = sum(t.amount_clp for t in transactions_week if t.category.type == 'income')
    expense_week = sum(t.amount_clp for t in transactions_week if t.category.type == 'expense')
    balance_week = income_week - expense_week
    
    # Indicadores financieros adicionales
    # 1. Utilidad operativa = Ingresos - Egresos (ya calculado como balance_month)
    utilidad_operativa = balance_month
    
    # 2. Margen operativo (%) = (Utilidad / Ingresos) × 100
    if income_month > 0:
        margen_operativo = (utilidad_operativa / income_month) * 100
    else:
        margen_operativo = 0
    
    # 3. Costo promedio por huevo
    # Total producción del mes
    produccion_mes = EggProduction.objects.filter(
        production_date__gte=current_month_start,
        production_date__lte=today,
        is_active=True
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    if produccion_mes > 0:
        costo_promedio_huevo = expense_month / produccion_mes
    else:
        costo_promedio_huevo = 0
    
    # Chart data - Last 7 days egg production
    chart_data = []
    chart_labels = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%d/%m'))
        
        daily_production = EggProduction.objects.filter(
            production_date=date,
            is_active=True
        ).values('size_code').annotate(total=Sum('quantity'))
        
        day_data = {'small': 0, 'medium': 0, 'large': 0}
        for prod in daily_production:
            day_data[prod['size_code']] = prod['total']
        
        chart_data.append(day_data)
    
    chart_small = [d['small'] for d in chart_data]
    chart_medium = [d['medium'] for d in chart_data]
    chart_large = [d['large'] for d in chart_data]
    
    # Size distribution (last 7 days)
    size_dist = EggProduction.objects.filter(
        production_date__gte=week_ago,
        is_active=True
    ).values('size_code').annotate(total=Sum('quantity'))
    
    size_distribution = [0, 0, 0]  # small, medium, large
    for item in size_dist:
        if item['size_code'] == 'small':
            size_distribution[0] = item['total']
        elif item['size_code'] == 'medium':
            size_distribution[1] = item['total']
        elif item['size_code'] == 'large':
            size_distribution[2] = item['total']
    
    # Recent activity
    recent_production = EggProduction.objects.filter(
        is_active=True
    ).order_by('-production_date', '-created_at')[:5]
    
    recent_transactions = FinanceTransaction.objects.filter(
        is_active=True
    ).select_related('category').order_by('-transaction_date', '-created_at')[:5]
    
    context = {
        'current_date': timezone.now(),
        'checklist': checklist,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'completion_percentage': completion_percentage,
        
        # Indicadores productivos
        'indicadores_productivos': {
            'produccion_hoy': eggs_today,
            'porcentaje_postura': round(porcentaje_postura, 2),
            'consumo_semanal': round(consumo_semanal, 2),
            'conversion_alimenticia': round(conversion_alimenticia, 2),
            'gallinas_totales': hens_count,
            'docenas_semanales': round(docenas_semanales, 2),
            'produccion_semanal': produccion_semanal,
        },
        
        # Indicadores financieros
        'indicadores_financieros': {
            'ingresos_mes': income_month,
            'gastos_mes': expense_month,
            'balance_mes': balance_month,
            'ingresos_semana': income_week,
            'gastos_semana': expense_week,
            'balance_semana': balance_week,
            'utilidad_operativa': utilidad_operativa,
            'margen_operativo': round(margen_operativo, 2),
            'costo_promedio_huevo': round(costo_promedio_huevo, 2),
            'produccion_mes': produccion_mes,
        },
        
        # Stats originales (mantener compatibilidad)
        'stats': {
            'total_birds': total_birds,
            'eggs_today': eggs_today,
            'mortality_month': mortality_month,
            'balance_month': balance_month,
        },
        
        # Gráficos
        'chart_labels': json.dumps(chart_labels),
        'chart_small': json.dumps(chart_small),
        'chart_medium': json.dumps(chart_medium),
        'chart_large': json.dumps(chart_large),
        'size_distribution': json.dumps(size_distribution),
        
        # Actividad reciente
        'recent_production': recent_production,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def switch_view_role(request, role):
    """
    Permite al admin cambiar temporalmente la vista según un rol.
    Solo disponible para usuarios admin.
    """
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para cambiar de vista')
        return redirect('dashboard')
    
    valid_roles = ['admin', 'worker', 'accountant']
    
    if role not in valid_roles:
        messages.error(request, 'Rol inválido')
        return redirect('dashboard')
    
    # Guardar el rol temporal en la sesión
    request.session['view_as_role'] = role
    
    if role == 'admin':
        messages.success(request, 'Vista restaurada a Admin')
        # Limpiar la sesión si vuelve a admin
        if 'view_as_role' in request.session:
            del request.session['view_as_role']
    else:
        role_names = {
            'worker': 'Trabajador',
            'accountant': 'Contador'
        }
        messages.info(request, f'Viendo el sistema como: {role_names.get(role, role)}')
    
    return redirect('dashboard')
