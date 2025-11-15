"""
Agrega variables de permisos a todos los templates.
Esto permite mostrar/ocultar botones según el rol del usuario.
"""

def effective_role(request):
    """
    Agrega variables de permisos que se pueden usar en cualquier template.
    
    Variables disponibles:
    - effective_role: El rol actual del usuario
    - can_write_finance: True si puede modificar finanzas
    - can_write_production: True si puede modificar producción/alimentación
    - is_admin: True si es administrador (rol real)
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Obtener el rol efectivo (puede ser temporal si es admin)
        if hasattr(request, 'effective_role'):
            role = request.effective_role
        else:
            role = request.user.rol
        
        return {
            'effective_role': role,
            'can_write_finance': role in ['admin', 'accountant'],
            'can_write_production': role in ['admin', 'worker'],
            'is_admin': request.user.rol == 'admin',  # Rol real, no temporal
        }
    
    return {
        'effective_role': None,
        'can_write_finance': False,
        'can_write_production': False,
        'is_admin': False,
    }
