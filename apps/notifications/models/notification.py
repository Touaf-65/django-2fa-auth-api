"""
Modèles pour les notifications générales
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class NotificationTemplate(models.Model):
    """
    Modèle pour les templates de notifications
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du template"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push'),
            ('in_app', 'In-App'),
        ],
        verbose_name="Type de notification"
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sujet"
    )
    content = models.TextField(
        verbose_name="Contenu"
    )
    html_content = models.TextField(
        blank=True,
        verbose_name="Contenu HTML"
    )
    
    # Variables disponibles dans le template
    available_variables = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Variables disponibles",
        help_text="Liste des variables disponibles dans le template"
    )
    
    # Paramètres de notification
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normal'),
            ('high', 'Élevé'),
            ('urgent', 'Urgent'),
        ],
        default='normal',
        verbose_name="Priorité"
    )
    
    # Métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Template de notification"
        verbose_name_plural = "Templates de notifications"
        db_table = 'notifications_notification_template'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"
    
    def render_content(self, context=None):
        """Rend le contenu du template avec le contexte fourni"""
        if not context:
            context = {}
        
        content = self.content
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        return content
    
    def render_html_content(self, context=None):
        """Rend le contenu HTML du template avec le contexte fourni"""
        if not context:
            context = {}
        
        html_content = self.html_content or self.content
        for key, value in context.items():
            html_content = html_content.replace(f'{{{key}}}', str(value))
        
        return html_content


class Notification(models.Model):
    """
    Modèle principal pour les notifications
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Utilisateur"
    )
    
    # Type et template
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push'),
            ('in_app', 'In-App'),
        ],
        verbose_name="Type de notification"
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template"
    )
    
    # Contenu
    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Sujet"
    )
    content = models.TextField(
        verbose_name="Contenu"
    )
    html_content = models.TextField(
        blank=True,
        verbose_name="Contenu HTML"
    )
    
    # Destinataire
    recipient_email = models.EmailField(
        blank=True,
        verbose_name="Email destinataire"
    )
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone destinataire"
    )
    
    # Statut et priorité
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('sent', 'Envoyé'),
            ('delivered', 'Livré'),
            ('failed', 'Échoué'),
            ('cancelled', 'Annulé'),
        ],
        default='pending',
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normal'),
            ('high', 'Élevé'),
            ('urgent', 'Urgent'),
        ],
        default='normal',
        verbose_name="Priorité"
    )
    
    # Planification
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Planifié pour"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Envoyé le"
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Livré le"
    )
    
    # Métadonnées
    context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Contexte",
        help_text="Variables utilisées pour le rendu du template"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées",
        help_text="Informations supplémentaires (ID externe, etc.)"
    )
    
    # Tentatives
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de tentatives"
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Nombre maximum de tentatives"
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
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} pour {self.user.email} - {self.status}"
    
    def can_retry(self):
        """Vérifie si la notification peut être retentée"""
        return self.retry_count < self.max_retries and self.status in ['failed', 'pending']
    
    def mark_as_sent(self):
        """Marque la notification comme envoyée"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_as_delivered(self):
        """Marque la notification comme livrée"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def mark_as_failed(self):
        """Marque la notification comme échouée"""
        self.status = 'failed'
        self.retry_count += 1
        self.save(update_fields=['status', 'retry_count', 'updated_at'])
    
    def cancel(self):
        """Annule la notification"""
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])
    
    def render_content(self):
        """Rend le contenu avec le contexte"""
        if self.template:
            return self.template.render_content(self.context)
        return self.content
    
    def render_html_content(self):
        """Rend le contenu HTML avec le contexte"""
        if self.template:
            return self.template.render_html_content(self.context)
        return self.html_content or self.content


class NotificationLog(models.Model):
    """
    Modèle pour les logs des notifications
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name="Notification"
    )
    
    # Type d'action
    action = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Créée'),
            ('sent', 'Envoyée'),
            ('delivered', 'Livrée'),
            ('failed', 'Échouée'),
            ('retry', 'Nouvelle tentative'),
            ('cancelled', 'Annulée'),
        ],
        verbose_name="Action"
    )
    
    # Détails
    message = models.TextField(
        verbose_name="Message"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Détails",
        help_text="Informations supplémentaires (erreurs, métadonnées, etc.)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Log de notification"
        verbose_name_plural = "Logs de notifications"
        db_table = 'notifications_notification_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification} - {self.get_action_display()} ({self.created_at})"
    
    @classmethod
    def log_action(cls, notification, action, message, details=None):
        """Enregistre une action dans les logs"""
        return cls.objects.create(
            notification=notification,
            action=action,
            message=message,
            details=details or {}
        )



