"""
Modèles pour les notifications push
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class PushToken(models.Model):
    """
    Modèle pour les tokens de notifications push
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_tokens',
        verbose_name="Utilisateur"
    )
    
    # Token
    token = models.TextField(
        verbose_name="Token push"
    )
    
    # Type de device
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web'),
        ],
        verbose_name="Type de device"
    )
    
    # Informations du device
    device_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID du device"
    )
    device_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du device"
    )
    app_version = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Version de l'app"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière utilisation"
    )
    
    class Meta:
        verbose_name = "Token push"
        verbose_name_plural = "Tokens push"
        db_table = 'notifications_push_token'
        unique_together = ['user', 'token']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token {self.device_type} pour {self.user.email}"
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at', 'updated_at'])


class PushNotification(models.Model):
    """
    Modèle pour les notifications push
    """
    notification = models.OneToOneField(
        'notifications.Notification',
        on_delete=models.CASCADE,
        related_name='push_notification',
        verbose_name="Notification"
    )
    
    # Destinataire
    push_token = models.ForeignKey(
        PushToken,
        on_delete=models.CASCADE,
        verbose_name="Token push"
    )
    
    # Contenu
    title = models.CharField(
        max_length=100,
        verbose_name="Titre"
    )
    body = models.TextField(
        max_length=200,
        verbose_name="Corps du message"
    )
    
    # Données supplémentaires
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données supplémentaires",
        help_text="Données JSON à envoyer avec la notification"
    )
    
    # Paramètres de notification
    sound = models.CharField(
        max_length=50,
        default='default',
        verbose_name="Son"
    )
    badge = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Badge"
    )
    
    # Statut
    fcm_message_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID message FCM"
    )
    fcm_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Statut FCM"
    )
    
    # Métadonnées
    context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Contexte"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Notification push"
        verbose_name_plural = "Notifications push"
        db_table = 'notifications_push_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Push pour {self.push_token.user.email} - {self.title}"
    
    def get_fcm_data(self):
        """Retourne les données formatées pour Firebase Cloud Messaging"""
        return {
            'to': self.push_token.token,
            'notification': {
                'title': self.title,
                'body': self.body,
                'sound': self.sound,
                'badge': self.badge
            },
            'data': self.data
        }
    
    def update_fcm_status(self, message_id, status):
        """Met à jour le statut FCM"""
        self.fcm_message_id = message_id
        self.fcm_status = status
        self.save(update_fields=['fcm_message_id', 'fcm_status', 'updated_at'])

