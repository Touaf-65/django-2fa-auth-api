"""
Modèle pour les actions d'administration
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AdminAction(TimestampedModel):
    """
    Modèle pour enregistrer les actions d'administration
    """
    ACTION_TYPES = [
        ('user_create', 'Création d\'utilisateur'),
        ('user_update', 'Modification d\'utilisateur'),
        ('user_delete', 'Suppression d\'utilisateur'),
        ('user_activate', 'Activation d\'utilisateur'),
        ('user_deactivate', 'Désactivation d\'utilisateur'),
        ('user_suspend', 'Suspension d\'utilisateur'),
        ('user_unsuspend', 'Réactivation d\'utilisateur'),
        ('permission_grant', 'Octroi de permission'),
        ('permission_revoke', 'Révocation de permission'),
        ('role_assign', 'Attribution de rôle'),
        ('role_unassign', 'Suppression de rôle'),
        ('group_add', 'Ajout à un groupe'),
        ('group_remove', 'Suppression d\'un groupe'),
        ('system_config', 'Configuration système'),
        ('backup_create', 'Création de sauvegarde'),
        ('backup_restore', 'Restauration de sauvegarde'),
        ('log_export', 'Export de logs'),
        ('data_export', 'Export de données'),
        ('data_import', 'Import de données'),
        ('security_alert', 'Alerte de sécurité'),
        ('maintenance_mode', 'Mode maintenance'),
        ('cache_clear', 'Vidage du cache'),
        ('email_send', 'Envoi d\'email'),
        ('notification_send', 'Envoi de notification'),
        ('api_key_create', 'Création de clé API'),
        ('api_key_revoke', 'Révocation de clé API'),
        ('integration_create', 'Création d\'intégration'),
        ('integration_update', 'Modification d\'intégration'),
        ('integration_delete', 'Suppression d\'intégration'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevé'),
        ('urgent', 'Urgent'),
        ('critical', 'Critique'),
    ]
    
    # Informations de base
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        verbose_name="Type d'action"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name="Priorité"
    )
    
    # Utilisateur et cible
    admin_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_actions',
        verbose_name="Administrateur"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_admin_actions',
        verbose_name="Utilisateur cible"
    )
    
    # Détails de l'action
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    details = models.JSONField(
        default=dict,
        verbose_name="Détails"
    )
    
    # Résultat
    result = models.JSONField(
        default=dict,
        verbose_name="Résultat"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Message d'erreur"
    )
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Clé de session"
    )
    
    # Timestamps spécifiques
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Début"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin"
    )
    duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Durée"
    )
    
    class Meta:
        verbose_name = "Action d'administration"
        verbose_name_plural = "Actions d'administration"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['status']),
            models.Index(fields=['admin_user']),
            models.Index(fields=['target_user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.title}"
    
    def start(self):
        """Démarre l'action"""
        from django.utils import timezone
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self, result=None, error_message=None):
        """Termine l'action"""
        from django.utils import timezone
        self.status = 'completed' if not error_message else 'failed'
        self.completed_at = timezone.now()
        
        if result:
            self.result = result
        if error_message:
            self.error_message = error_message
        
        # Calcule la durée
        if self.started_at:
            self.duration = self.completed_at - self.started_at
        
        self.save()
    
    def cancel(self, reason=None):
        """Annule l'action"""
        from django.utils import timezone
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        
        if reason:
            self.error_message = f"Annulé: {reason}"
        
        # Calcule la durée
        if self.started_at:
            self.duration = self.completed_at - self.started_at
        
        self.save()
    
    @property
    def is_completed(self):
        """Vérifie si l'action est terminée"""
        return self.status in ['completed', 'failed', 'cancelled']
    
    @property
    def is_successful(self):
        """Vérifie si l'action a réussi"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Vérifie si l'action a échoué"""
        return self.status == 'failed'
    
    @property
    def is_cancelled(self):
        """Vérifie si l'action a été annulée"""
        return self.status == 'cancelled'
    
    @property
    def is_in_progress(self):
        """Vérifie si l'action est en cours"""
        return self.status == 'in_progress'
    
    @property
    def is_pending(self):
        """Vérifie si l'action est en attente"""
        return self.status == 'pending'
    
    @classmethod
    def get_actions_by_type(cls, action_type):
        """Récupère les actions par type"""
        return cls.objects.filter(action_type=action_type)
    
    @classmethod
    def get_actions_by_admin(cls, admin_user):
        """Récupère les actions par administrateur"""
        return cls.objects.filter(admin_user=admin_user)
    
    @classmethod
    def get_actions_by_target(cls, target_user):
        """Récupère les actions par utilisateur cible"""
        return cls.objects.filter(target_user=target_user)
    
    @classmethod
    def get_recent_actions(cls, days=7):
        """Récupère les actions récentes"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(created_at__gte=cutoff)
    
    @classmethod
    def get_failed_actions(cls):
        """Récupère les actions échouées"""
        return cls.objects.filter(status='failed')
    
    @classmethod
    def get_pending_actions(cls):
        """Récupère les actions en attente"""
        return cls.objects.filter(status='pending')
    
    @classmethod
    def get_in_progress_actions(cls):
        """Récupère les actions en cours"""
        return cls.objects.filter(status='in_progress')

