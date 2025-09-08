"""
Modèle pour les événements de sécurité
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class SecurityEvent(models.Model):
    """
    Modèle pour enregistrer les événements de sécurité
    """
    # Utilisateur concerné (peut être null pour les événements généraux)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='security_events',
        verbose_name="Utilisateur"
    )
    
    # Type d'événement
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILED = 'login_failed'
    LOGIN_BLOCKED = 'login_blocked'
    PASSWORD_CHANGED = 'password_changed'
    PASSWORD_RESET = 'password_reset'
    PROFILE_UPDATED = 'profile_updated'
    TWO_FA_ENABLED = '2fa_enabled'
    TWO_FA_DISABLED = '2fa_disabled'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'
    IP_BLOCKED = 'ip_blocked'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    UNUSUAL_LOCATION = 'unusual_location'
    MULTIPLE_DEVICES = 'multiple_devices'
    
    EVENT_TYPE_CHOICES = [
        (LOGIN_SUCCESS, 'Connexion réussie'),
        (LOGIN_FAILED, 'Connexion échouée'),
        (LOGIN_BLOCKED, 'Connexion bloquée'),
        (PASSWORD_CHANGED, 'Mot de passe changé'),
        (PASSWORD_RESET, 'Mot de passe réinitialisé'),
        (PROFILE_UPDATED, 'Profil mis à jour'),
        (TWO_FA_ENABLED, '2FA activée'),
        (TWO_FA_DISABLED, '2FA désactivée'),
        (SUSPICIOUS_ACTIVITY, 'Activité suspecte'),
        (IP_BLOCKED, 'IP bloquée'),
        (RATE_LIMIT_EXCEEDED, 'Limite de taux dépassée'),
        (UNUSUAL_LOCATION, 'Localisation inhabituelle'),
        (MULTIPLE_DEVICES, 'Multiples appareils'),
    ]
    
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        verbose_name="Type d'événement"
    )
    
    # Niveau de gravité
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    
    SEVERITY_CHOICES = [
        (LOW, 'Faible'),
        (MEDIUM, 'Moyen'),
        (HIGH, 'Élevé'),
        (CRITICAL, 'Critique'),
    ]
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default=MEDIUM,
        verbose_name="Gravité"
    )
    
    # Description de l'événement
    title = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    
    # Informations de la requête
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Pays (code ISO)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville"
    )
    
    # Données supplémentaires
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées"
    )
    
    # Statut de traitement
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    IGNORED = 'ignored'
    ESCALATED = 'escalated'
    
    STATUS_CHOICES = [
        (PROCESSING, 'En cours de traitement'),
        (PROCESSED, 'Traité'),
        (IGNORED, 'Ignoré'),
        (ESCALATED, 'Escaladé'),
    ]
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PROCESSING,
        verbose_name="Statut"
    )
    
    # Actions prises
    actions_taken = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Actions prises"
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
        verbose_name = "Événement de sécurité"
        verbose_name_plural = "Événements de sécurité"
        db_table = 'security_security_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.title}"
    
    @classmethod
    def create_event(cls, event_type, title, description, ip_address, 
                    user=None, severity=None, user_agent=None, 
                    country=None, city=None, metadata=None):
        """
        Crée un nouvel événement de sécurité
        """
        # Déterminer la gravité par défaut selon le type
        if severity is None:
            severity_map = {
                cls.LOGIN_SUCCESS: cls.LOW,
                cls.LOGIN_FAILED: cls.MEDIUM,
                cls.LOGIN_BLOCKED: cls.HIGH,
                cls.PASSWORD_CHANGED: cls.MEDIUM,
                cls.PASSWORD_RESET: cls.MEDIUM,
                cls.PROFILE_UPDATED: cls.LOW,
                cls.TWO_FA_ENABLED: cls.LOW,
                cls.TWO_FA_DISABLED: cls.HIGH,
                cls.SUSPICIOUS_ACTIVITY: cls.HIGH,
                cls.IP_BLOCKED: cls.HIGH,
                cls.RATE_LIMIT_EXCEEDED: cls.MEDIUM,
                cls.UNUSUAL_LOCATION: cls.MEDIUM,
                cls.MULTIPLE_DEVICES: cls.MEDIUM,
            }
            severity = severity_map.get(event_type, cls.MEDIUM)
        
        return cls.objects.create(
            user=user,
            event_type=event_type,
            severity=severity,
            title=title,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent or '',
            country=country or '',
            city=city or '',
            metadata=metadata or {}
        )
    
    def add_action(self, action, details=None):
        """
        Ajoute une action prise pour cet événement
        """
        if not self.actions_taken:
            self.actions_taken = []
        
        action_data = {
            'action': action,
            'details': details or '',
            'timestamp': timezone.now().isoformat()
        }
        
        self.actions_taken.append(action_data)
        self.save(update_fields=['actions_taken', 'updated_at'])
    
    def mark_as_processed(self):
        """
        Marque l'événement comme traité
        """
        self.status = self.PROCESSED
        self.save(update_fields=['status', 'updated_at'])
    
    def escalate(self):
        """
        Escalade l'événement
        """
        self.status = self.ESCALATED
        self.add_action('escalated', 'Événement escaladé pour investigation')
        self.save(update_fields=['status', 'updated_at'])



