"""
Configuration de l'application Core
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration de l'application Core"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
    
    def ready(self):
        """Initialisation de l'application"""
        # Import des signaux si nécessaire
        try:
            import core.signals
        except ImportError:
            pass

