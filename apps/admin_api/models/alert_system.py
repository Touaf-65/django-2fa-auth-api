"""
Modèles pour le système d'alertes
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AlertRule(TimestampedModel):
    """Règles d'alerte système"""
    
    ALERT_TYPES = [
        ('system', 'Système'),
        ('performance', 'Performance'),
        ('security', 'Sécurité'),
        ('user', 'Utilisateur'),
        ('database', 'Base de données'),
        ('disk', 'Espace disque'),
        ('memory', 'Mémoire'),
        ('cpu', 'CPU'),
        ('network', 'Réseau'),
        ('api', 'API'),
        ('error', 'Erreur'),
        ('custom', 'Personnalisé'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('paused', 'En pause'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom de la règle")
    description = models.TextField(blank=True, verbose_name="Description")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name="Type d'alerte")
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium', verbose_name="Sévérité")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    
    # Conditions
    condition = models.JSONField(verbose_name="Condition d'alerte")
    threshold_value = models.FloatField(null=True, blank=True, verbose_name="Valeur seuil")
    comparison_operator = models.CharField(max_length=10, default='>', verbose_name="Opérateur de comparaison")
    
    # Configuration
    check_interval = models.IntegerField(default=300, verbose_name="Intervalle de vérification (secondes)")
    cooldown_period = models.IntegerField(default=3600, verbose_name="Période de cooldown (secondes)")
    max_alerts_per_hour = models.IntegerField(default=10, verbose_name="Max alertes par heure")
    
    # Notifications
    notification_channels = models.JSONField(default=list, verbose_name="Canaux de notification")
    escalation_rules = models.JSONField(default=dict, verbose_name="Règles d'escalade")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alert_rules', verbose_name="Créé par")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    class Meta:
        verbose_name = "Règle d'alerte"
        verbose_name_plural = "Règles d'alerte"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_alert_type_display()})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def should_trigger_alert(self, current_value):
        """Vérifie si l'alerte doit être déclenchée"""
        if not self.is_active:
            return False
        
        if self.threshold_value is None:
            return False
        
        # Logique de comparaison
        if self.comparison_operator == '>':
            return current_value > self.threshold_value
        elif self.comparison_operator == '>=':
            return current_value >= self.threshold_value
        elif self.comparison_operator == '<':
            return current_value < self.threshold_value
        elif self.comparison_operator == '<=':
            return current_value <= self.threshold_value
        elif self.comparison_operator == '==':
            return current_value == self.threshold_value
        elif self.comparison_operator == '!=':
            return current_value != self.threshold_value
        
        return False


class SystemAlert(TimestampedModel):
    """Alertes système générées"""
    
    STATUS_CHOICES = [
        ('triggered', 'Déclenchée'),
        ('acknowledged', 'Reconnue'),
        ('resolved', 'Résolue'),
        ('suppressed', 'Supprimée'),
    ]
    
    # Informations de base
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts', verbose_name="Règle d'alerte")
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='triggered', verbose_name="Statut")
    
    # Données de l'alerte
    current_value = models.FloatField(null=True, blank=True, verbose_name="Valeur actuelle")
    threshold_value = models.FloatField(null=True, blank=True, verbose_name="Valeur seuil")
    severity = models.CharField(max_length=20, choices=AlertRule.SEVERITY_LEVELS, verbose_name="Sévérité")
    
    # Métadonnées
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Déclenchée à")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="Reconnue à")
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts', verbose_name="Reconnue par")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Résolue à")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts', verbose_name="Résolue par")
    
    # Données contextuelles
    context_data = models.JSONField(default=dict, verbose_name="Données contextuelles")
    notification_sent = models.BooleanField(default=False, verbose_name="Notification envoyée")
    
    class Meta:
        verbose_name = "Alerte système"
        verbose_name_plural = "Alertes système"
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def acknowledge(self, user):
        """Reconnaître l'alerte"""
        from django.utils import timezone
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save()
    
    def resolve(self, user):
        """Résoudre l'alerte"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()
    
    def suppress(self):
        """Supprimer l'alerte"""
        self.status = 'suppressed'
        self.save()


class AlertNotification(TimestampedModel):
    """Notifications d'alerte envoyées"""
    
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('failed', 'Échouée'),
        ('delivered', 'Livrée'),
    ]
    
    # Informations de base
    alert = models.ForeignKey(SystemAlert, on_delete=models.CASCADE, related_name='notifications', verbose_name="Alerte")
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES, verbose_name="Type de canal")
    recipient = models.CharField(max_length=500, verbose_name="Destinataire")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Contenu
    subject = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    
    # Métadonnées
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyée à")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Livrée à")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    retry_count = models.IntegerField(default=0, verbose_name="Nombre de tentatives")
    
    class Meta:
        verbose_name = "Notification d'alerte"
        verbose_name_plural = "Notifications d'alerte"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert.title} - {self.get_channel_type_display()}"

