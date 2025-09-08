"""
Signaux pour l'application users
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile, UserPreference

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil et des préférences pour un nouvel utilisateur
    """
    if created:
        # Créer le profil utilisateur
        UserProfile.objects.get_or_create(user=instance)
        
        # Créer les préférences utilisateur
        UserPreference.objects.get_or_create(user=instance)
        
        # Enregistrer l'activité
        from .models import UserActivity
        UserActivity.log_activity(
            user=instance,
            activity_type='account_created',
            description='Compte créé'
        )

