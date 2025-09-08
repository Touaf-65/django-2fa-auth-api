"""
URL configuration for Django 2FA Auth API project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Authentication
    path('api/auth/', include('apps.authentication.urls')),
    
    # API Users
    path('api/users/', include('apps.users.urls')),
    
    # API Notifications
    path('api/notifications/', include('apps.notifications.urls')),
    
    # API Permissions
    path('api/permissions/', include('apps.permissions.urls')),
    
    # API Admin
    path('api/admin/', include('apps.admin_api.urls')),
    
    # API Monitoring
    path('api/monitoring/', include('apps.monitoring.urls')),
]

# Debug toolbar en développement
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Servir les fichiers media et static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
