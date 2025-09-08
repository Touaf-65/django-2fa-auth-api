"""
Modèles pour les notifications SMS
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class SMSNotification(models.Model):
    """
    Modèle pour les notifications SMS
    """
    notification = models.OneToOneField(
        'notifications.Notification',
        on_delete=models.CASCADE,
        related_name='sms_notification',
        verbose_name="Notification"
    )
    
    # Destinataire
    to_phone = models.CharField(
        max_length=20,
        verbose_name="Numéro de téléphone destinataire"
    )
    
    # Contenu
    message = models.TextField(
        max_length=1600,  # Limite SMS
        verbose_name="Message"
    )
    
    # Statut Twilio
    twilio_sid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="SID Twilio"
    )
    twilio_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Statut Twilio"
    )
    twilio_error_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code d'erreur Twilio"
    )
    twilio_error_message = models.TextField(
        blank=True,
        verbose_name="Message d'erreur Twilio"
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
        verbose_name = "Notification SMS"
        verbose_name_plural = "Notifications SMS"
        db_table = 'notifications_sms_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS pour {self.to_phone} - {self.message[:50]}..."
    
    def get_twilio_data(self):
        """Retourne les données formatées pour Twilio"""
        return {
            'to': self.to_phone,
            'from_': settings.TWILIO_PHONE_NUMBER,
            'body': self.message
        }
    
    def update_twilio_status(self, sid, status, error_code=None, error_message=None):
        """Met à jour le statut Twilio"""
        self.twilio_sid = sid
        self.twilio_status = status
        if error_code:
            self.twilio_error_code = error_code
        if error_message:
            self.twilio_error_message = error_message
        self.save(update_fields=[
            'twilio_sid', 'twilio_status', 
            'twilio_error_code', 'twilio_error_message', 'updated_at'
        ])

