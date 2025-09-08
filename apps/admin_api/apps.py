"""
Configuration de l'application Admin API
"""
from django.apps import AppConfig


class AdminApiConfig(AppConfig):
    """Configuration de l'application Admin API"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_api'
    verbose_name = 'Admin API'
    
    def ready(self):
        """Initialisation de l'application"""
        # Import des signaux si nécessaire
        try:
            import apps.admin_api.signals
        except ImportError:
            pass

