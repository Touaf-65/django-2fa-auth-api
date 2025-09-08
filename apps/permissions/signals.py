"""
Signaux pour l'app permissions
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PermissionManager

User = get_user_model()


@receiver(post_save, sender=User)
def create_permission_manager_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil de gestionnaire de permissions lors de la création d'un utilisateur"""
    if created:
        PermissionManager.get_or_create_for_user(instance)

