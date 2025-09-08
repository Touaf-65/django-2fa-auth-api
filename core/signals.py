"""
Signaux pour l'application Core
"""
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour les utilisateurs"""
    if created:
        logger.info(f"Nouvel utilisateur créé: {instance.email}")
    else:
        logger.info(f"Utilisateur mis à jour: {instance.email}")


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """Signal pre-save pour les utilisateurs"""
    if instance.pk:
        # Vérifie si l'email a changé
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.email != instance.email:
                logger.info(f"Email de l'utilisateur {instance.pk} changé de {old_instance.email} vers {instance.email}")
        except User.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """Signal post-delete pour les utilisateurs"""
    logger.info(f"Utilisateur supprimé: {instance.email}")


@receiver(pre_delete, sender=User)
def user_pre_delete(sender, instance, **kwargs):
    """Signal pre-delete pour les utilisateurs"""
    logger.info(f"Suppression de l'utilisateur: {instance.email}")

