"""
Configuration de l'app Internationalization
"""
from django.apps import AppConfig


class InternationalizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.internationalization'
    verbose_name = 'Internationalization'
    
    def ready(self):
        """Initialisation de l'app"""
        import apps.internationalization.signals