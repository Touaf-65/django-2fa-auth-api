"""
Modèles pour les notifications email
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class EmailTemplate(models.Model):
    """
    Modèle pour les templates d'emails
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du template"
    )
    
    # Contenu de l'email
    subject = models.CharField(
        max_length=200,
        verbose_name="Sujet"
    )
    html_content = models.TextField(
        verbose_name="Contenu HTML"
    )
    text_content = models.TextField(
        blank=True,
        verbose_name="Contenu texte"
    )
    
    # En-têtes
    from_email = models.EmailField(
        default=settings.DEFAULT_FROM_EMAIL,
        verbose_name="Email expéditeur"
    )
    from_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom expéditeur"
    )
    reply_to = models.EmailField(
        blank=True,
        verbose_name="Email de réponse"
    )
    
    # Variables disponibles
    available_variables = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Variables disponibles"
    )
    
    # Paramètres
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
    
    class Meta:
        verbose_name = "Template email"
        verbose_name_plural = "Templates email"
        db_table = 'notifications_email_template'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def render_subject(self, context=None):
        """Rend le sujet avec le contexte"""
        if not context:
            context = {}
        
        subject = self.subject
        for key, value in context.items():
            subject = subject.replace(f'{{{key}}}', str(value))
        
        return subject
    
    def render_html_content(self, context=None):
        """Rend le contenu HTML avec le contexte"""
        if not context:
            context = {}
        
        html_content = self.html_content
        for key, value in context.items():
            html_content = html_content.replace(f'{{{key}}}', str(value))
        
        return html_content
    
    def render_text_content(self, context=None):
        """Rend le contenu texte avec le contexte"""
        if not context:
            context = {}
        
        text_content = self.text_content or self.html_content
        for key, value in context.items():
            text_content = text_content.replace(f'{{{key}}}', str(value))
        
        return text_content


class EmailNotification(models.Model):
    """
    Modèle pour les notifications email
    """
    notification = models.OneToOneField(
        'notifications.Notification',
        on_delete=models.CASCADE,
        related_name='email_notification',
        verbose_name="Notification"
    )
    
    # Template
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template email"
    )
    
    # Destinataire
    to_email = models.EmailField(
        verbose_name="Email destinataire"
    )
    to_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom destinataire"
    )
    
    # En-têtes
    from_email = models.EmailField(
        default=settings.DEFAULT_FROM_EMAIL,
        verbose_name="Email expéditeur"
    )
    from_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom expéditeur"
    )
    reply_to = models.EmailField(
        blank=True,
        verbose_name="Email de réponse"
    )
    
    # Contenu
    subject = models.CharField(
        max_length=200,
        verbose_name="Sujet"
    )
    html_content = models.TextField(
        verbose_name="Contenu HTML"
    )
    text_content = models.TextField(
        blank=True,
        verbose_name="Contenu texte"
    )
    
    # Pièces jointes
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Pièces jointes",
        help_text="Liste des fichiers à joindre"
    )
    
    # Statut SendGrid
    sendgrid_message_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID message SendGrid"
    )
    sendgrid_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Statut SendGrid"
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
        verbose_name = "Notification email"
        verbose_name_plural = "Notifications email"
        db_table = 'notifications_email_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email pour {self.to_email} - {self.subject}"
    
    def prepare_content(self):
        """Prépare le contenu de l'email avec le contexte"""
        if self.template:
            self.subject = self.template.render_subject(self.context)
            self.html_content = self.template.render_html_content(self.context)
            self.text_content = self.template.render_text_content(self.context)
            self.from_email = self.template.from_email
            self.from_name = self.template.from_name
            self.reply_to = self.template.reply_to
        
        self.save(update_fields=[
            'subject', 'html_content', 'text_content',
            'from_email', 'from_name', 'reply_to'
        ])
    
    def get_sendgrid_data(self):
        """Retourne les données formatées pour SendGrid"""
        return {
            'to': [{'email': self.to_email, 'name': self.to_name}],
            'from': {'email': self.from_email, 'name': self.from_name},
            'subject': self.subject,
            'content': [
                {
                    'type': 'text/plain',
                    'value': self.text_content
                },
                {
                    'type': 'text/html',
                    'value': self.html_content
                }
            ],
            'reply_to': {'email': self.reply_to} if self.reply_to else None,
            'attachments': self.attachments
        }

