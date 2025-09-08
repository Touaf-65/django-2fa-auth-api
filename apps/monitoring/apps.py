"""
Configuration de l'app Monitoring
"""
from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'Monitoring & Observability'
    
    def ready(self):
        """Initialisation de l'app"""
        import apps.monitoring.signals