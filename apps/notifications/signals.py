"""
Signaux pour l'application notifications
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Notification, NotificationLog

User = get_user_model()


@receiver(post_save, sender=Notification)
def log_notification_creation(sender, instance, created, **kwargs):
    """
    Enregistre la création d'une notification
    """
    if created:
        NotificationLog.log_action(
            notification=instance,
            action='created',
            message=f"Notification {instance.notification_type} créée"
        )


@receiver(post_delete, sender=Notification)
def log_notification_deletion(sender, instance, **kwargs):
    """
    Enregistre la suppression d'une notification
    """
    # Note: Cette fonctionnalité peut être étendue selon les besoins
    pass
