"""
Middleware personalizado - Procesa todas las peticiones antes de llegar a las vistas.
"""

import logging
import time

logger = logging.getLogger('api')


class RequestLoggingMiddleware:
    """
    Registra todas las peticiones en el log.
    Útil para debugging y monitoreo del sistema.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Guardar tiempo de inicio
        start_time = time.time()
        
        # Obtener usuario (si está logueado)
        user = 'Anónimo'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = getattr(request.user, 'email', str(request.user))
        
        # Procesar la petición
        response = self.get_response(request)
        
        # Calcular cuánto tardó
        duration = time.time() - start_time
        
        # Guardar en el log
        logger.info(
            f"{request.method} {request.path} - "
            f"Status: {response.status_code} - "
            f"Usuario: {user} - "
            f"Duración: {duration:.2f}s"
        )
        
        return response


class ViewAsRoleMiddleware:
    """
    Permite que el admin vea el sistema como si fuera otro rol.
    Agrega el atributo 'effective_role' a cada petición.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo si el usuario está logueado
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Si es admin y está usando "ver como otro rol"
            if request.user.rol == 'admin' and 'view_as_role' in request.session:
                # Usar el rol temporal
                request.effective_role = request.session['view_as_role']
            else:
                # Usar el rol real
                request.effective_role = request.user.rol
        
        response = self.get_response(request)
        return response
