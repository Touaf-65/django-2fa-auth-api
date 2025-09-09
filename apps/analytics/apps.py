"""
Configuration de l'app Analytics
"""
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Analytics'

    def ready(self):
        """Import des signals lors du démarrage de l'app"""
        import apps.analytics.signals

