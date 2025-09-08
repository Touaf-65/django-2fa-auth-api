"""
Configuration de l'API App
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API Management'
    
    def ready(self):
        """Initialisation de l'app API"""
        import apps.api.signals