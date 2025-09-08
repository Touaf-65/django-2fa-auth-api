from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.permissions"
    verbose_name = "Gestion des Permissions"
    
    def ready(self):
        """
        Configuration de l'app lors du démarrage
        """
        # Importer les signaux
        from . import signals
