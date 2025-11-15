"""
Sistema de permisos - Controla quién puede hacer qué en el sistema.

MATRIZ DE PERMISOS:
==================
| Módulo        | Admin | Worker | Accountant |
|---------------|-------|--------|------------|
| Producción    | RW    | RW     | R          |
| Alimentación  | RW    | RW     | R          |
| Finanzas      | RW    | R      | RW         |
| Usuarios      | RW    | -      | -          |

R = Puede ver
W = Puede modificar
- = Sin acceso
"""
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def get_effective_role(request):
    """
    Obtiene el rol del usuario actual.
    Si el admin está usando "ver como otro rol", devuelve ese rol temporal.
    """
    if hasattr(request, 'effective_role'):
        return request.effective_role
    return request.user.rol if request.user.is_authenticated else None


def role_required(*allowed_roles):
    """
    Verifica que el usuario tenga uno de los roles permitidos.
    
    Ejemplo de uso:
        @role_required('admin', 'accountant')
        def mi_vista(request):
            # Solo admin y contador pueden entrar aquí
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión')
                return redirect('web_login')
            
            effective_role = get_effective_role(request)
            
            if effective_role not in allowed_roles:
                messages.error(request, 'No tienes permisos para realizar esta acción')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# PERMISOS DE FINANZAS
# ============================================================================

def finance_write_required(view_func):
    """
    Solo admin y contador pueden modificar finanzas.
    El trabajador solo puede ver.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('web_login')
        
        effective_role = get_effective_role(request)
        
        if effective_role not in ['admin', 'accountant']:
            messages.error(request, 'Solo administradores y contadores pueden modificar finanzas')
            return redirect('finance_transaction_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# PERMISOS DE PRODUCCIÓN Y ALIMENTACIÓN
# ============================================================================

def production_write_required(view_func):
    """
    Solo admin y trabajador pueden modificar producción/alimentación.
    El contador solo puede ver.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('web_login')
        
        effective_role = get_effective_role(request)
        
        if effective_role not in ['admin', 'worker']:
            messages.error(request, 'Solo administradores y trabajadores pueden modificar producción y alimentación')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# PERMISOS DE ADMINISTRACIÓN
# ============================================================================

def admin_required(view_func):
    """
    Solo el administrador puede acceder.
    Nota: Usa el rol real, no el temporal (para seguridad).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión')
            return redirect('web_login')
        
        # Usar el rol REAL, no el efectivo
        if request.user.rol != 'admin':
            messages.error(request, 'Solo administradores pueden acceder a esta sección')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
