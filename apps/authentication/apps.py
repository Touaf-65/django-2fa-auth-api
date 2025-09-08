"""
Configuration de l'application authentication
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Authentification'
    
    def ready(self):
        """Code exécuté au démarrage de l'application"""
        # Import des signaux si nécessaire
        pass

