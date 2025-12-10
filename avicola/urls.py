"""
URL configuration for avicola project.
Aplicación web monolítica con Django templates.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
# from drf_spectacular.views import (  # Comentado - API REST no se usa
#     SpectacularAPIView,
#     SpectacularRedocView,
#     SpectacularSwaggerView,
# )
from core import views as core_views


def health_check(request):
    """Health check endpoint - verifica que el servidor esté funcionando."""
    return JsonResponse({
        'status': 'ok',
        'message': 'Avícola Eugenio está funcionando correctamente'
    })


urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Vistas principales
    path('', core_views.dashboard_view, name='dashboard'),
    path('login/', core_views.login_view, name='web_login'),
    path('logout/', core_views.logout_view, name='web_logout'),
    path('switch-view/<str:role>/', core_views.switch_view_role, name='switch_view_role'),
    
    # URLs de la aplicación web
    path('web/', include('core.urls')),
    
    # ========================================================================
    # API REST (COMENTADA - No se usa en app monolítica)
    # ========================================================================
    # Descomentar solo si se necesita API REST en el futuro
    # path('api/', include('api.urls')),
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
