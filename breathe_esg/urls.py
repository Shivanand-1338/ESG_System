"""
URL configuration for breathe_esg project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone


def health_check(request):
    """Health check endpoint for monitoring."""
    try:
        from django.db import connection
        connection.ensure_connection()
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    
    return JsonResponse({
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'database': db_status,
        'timestamp': timezone.now().isoformat()
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/v1/', include('ingestion.urls')),
]
