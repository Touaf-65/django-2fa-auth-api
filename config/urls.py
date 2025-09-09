"""
URL configuration for Django 2FA Auth API project.
Configuration modulaire des URLs basée sur les apps activées.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Configuration modulaire des URLs
from config.settings.apps_settings import ENABLED_URLS

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Authentication (toujours activée)
    path('api/auth/', include('apps.authentication.urls')),
    
    # API Users (toujours activée)
    path('api/users/', include('apps.users.urls')),
]

# Ajouter les URLs des apps activées
for url_config in ENABLED_URLS:
    urlpatterns.append(
        path(url_config['path'], include(url_config['include']))
    )

# Debug toolbar en développement
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Servir les fichiers media et static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
