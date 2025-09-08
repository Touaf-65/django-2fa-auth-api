"""
Signaux pour l'Admin API
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import AdminLog
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save_admin_log(sender, instance, created, **kwargs):
    """Log automatique des modifications d'utilisateur"""
    if created:
        AdminLog.objects.create(
            admin_user=instance,  # L'utilisateur qui se crée
            action='user_create',
            target_model='User',
            target_id=str(instance.id),
            message=f'Utilisateur créé: {instance.email}',
            level='info'
        )
    else:
        AdminLog.objects.create(
            admin_user=instance,  # L'utilisateur modifié
            action='user_update',
            target_model='User',
            target_id=str(instance.id),
            message=f'Utilisateur modifié: {instance.email}',
            level='info'
        )


@receiver(post_delete, sender=User)
def user_post_delete_admin_log(sender, instance, **kwargs):
    """Log automatique de la suppression d'utilisateur"""
    AdminLog.objects.create(
        admin_user=instance,  # L'utilisateur supprimé
        action='user_delete',
        target_model='User',
        target_id=str(instance.id),
        message=f'Utilisateur supprimé: {instance.email}',
        level='warning'
    )



