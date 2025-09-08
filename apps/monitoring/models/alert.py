"""
Modèles pour les alertes de monitoring
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AlertRule(TimestampedModel):
    """Règle d'alerte"""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('testing', 'Testing'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric = models.ForeignKey('monitoring.Metric', on_delete=models.CASCADE)
    
    # Condition d'alerte
    condition = models.CharField(max_length=20, choices=[
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('eq', 'Equal'),
        ('neq', 'Not Equal'),
    ])
    threshold = models.FloatField()
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    
    # Configuration
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_enabled = models.BooleanField(default=True)
    
    # Notifications
    notification_channels = models.JSONField(default=list, blank=True)
    notification_template = models.TextField(blank=True)
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_alert_rule'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.severity})"
    
    @property
    def is_active(self):
        """Vérifie si la règle est active"""
        return self.status == 'active' and self.is_enabled
    
    def evaluate(self, metric_value):
        """Évalue si la règle doit déclencher une alerte"""
        if not self.is_active:
            return False
        
        value = metric_value.value
        
        if self.condition == 'gt':
            return value > self.threshold
        elif self.condition == 'gte':
            return value >= self.threshold
        elif self.condition == 'lt':
            return value < self.threshold
        elif self.condition == 'lte':
            return value <= self.threshold
        elif self.condition == 'eq':
            return value == self.threshold
        elif self.condition == 'neq':
            return value != self.threshold
        
        return False


class Alert(TimestampedModel):
    """Alerte déclenchée"""
    
    STATUS_CHOICES = [
        ('firing', 'Firing'),
        ('resolved', 'Resolved'),
        ('acknowledged', 'Acknowledged'),
        ('silenced', 'Silenced'),
    ]
    
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts')
    metric_value = models.ForeignKey('monitoring.MetricValue', on_delete=models.CASCADE)
    
    # État de l'alerte
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='firing')
    severity = models.CharField(max_length=10, choices=AlertRule.SEVERITY_CHOICES)
    
    # Détails
    message = models.TextField()
    value = models.FloatField()
    threshold = models.FloatField()
    
    # Gestion
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    labels = models.JSONField(default=dict, blank=True)
    annotations = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_alert'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['rule', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rule.name} - {self.status}"
    
    @property
    def is_firing(self):
        """Vérifie si l'alerte est en cours"""
        return self.status == 'firing'
    
    @property
    def is_resolved(self):
        """Vérifie si l'alerte est résolue"""
        return self.status == 'resolved'
    
    @property
    def is_acknowledged(self):
        """Vérifie si l'alerte est acquittée"""
        return self.status == 'acknowledged'
    
    def acknowledge(self, user):
        """Acquitte l'alerte"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = models.DateTimeField(auto_now=True)
        self.save()
    
    def resolve(self):
        """Résout l'alerte"""
        self.status = 'resolved'
        self.resolved_at = models.DateTimeField(auto_now=True)
        self.save()


class AlertNotification(TimestampedModel):
    """Notification d'alerte"""
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=500)
    
    # Contenu
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # État
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'monitoring_alert_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert.rule.name} -> {self.recipient} ({self.status})"
    
    @property
    def is_sent(self):
        """Vérifie si la notification a été envoyée"""
        return self.status in ['sent', 'delivered']
    
    def mark_sent(self):
        """Marque la notification comme envoyée"""
        self.status = 'sent'
        self.sent_at = models.DateTimeField(auto_now=True)
        self.save()
    
    def mark_delivered(self):
        """Marque la notification comme livrée"""
        self.status = 'delivered'
        self.delivered_at = models.DateTimeField(auto_now=True)
        self.save()
    
    def mark_failed(self, error_message):
        """Marque la notification comme échouée"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()



