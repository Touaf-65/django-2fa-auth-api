"""
Modèles pour les métriques Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AnalyticsMetric(TimestampedModel):
    """Définition d'une métrique analytique"""
    
    CATEGORY_CHOICES = [
        ('user', 'Utilisateur'),
        ('security', 'Sécurité'),
        ('performance', 'Performance'),
        ('usage', 'Utilisation'),
        ('business', 'Business'),
        ('system', 'Système'),
    ]
    
    TYPE_CHOICES = [
        ('counter', 'Compteur'),
        ('gauge', 'Jauge'),
        ('histogram', 'Histogramme'),
        ('summary', 'Résumé'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    metric_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Configuration
    unit = models.CharField(max_length=20, blank=True)
    aggregation_method = models.CharField(max_length=50, default='sum')
    retention_days = models.PositiveIntegerField(default=90)
    
    # Calcul et requête
    calculation_query = models.TextField(blank=True)
    data_source = models.CharField(max_length=100, blank=True)
    
    # Seuils et alertes
    warning_threshold = models.FloatField(null=True, blank=True)
    critical_threshold = models.FloatField(null=True, blank=True)
    alert_enabled = models.BooleanField(default=False)
    
    # État
    is_active = models.BooleanField(default=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    calculation_frequency = models.PositiveIntegerField(default=3600)  # en secondes
    
    class Meta:
        verbose_name = "Métrique Analytics"
        verbose_name_plural = "Métriques Analytics"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['metric_type']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.category})"


class MetricValue(TimestampedModel):
    """Valeur d'une métrique à un moment donné"""
    
    metric = models.ForeignKey(AnalyticsMetric, on_delete=models.CASCADE, related_name='values')
    value = models.FloatField()
    timestamp = models.DateTimeField()
    
    # Labels et dimensions
    labels = models.JSONField(default=dict)
    dimensions = models.JSONField(default=dict)
    
    # Métadonnées
    source = models.CharField(max_length=100, blank=True)
    calculated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='calculated_analytics_metrics')
    
    class Meta:
        verbose_name = "Valeur de Métrique"
        verbose_name_plural = "Valeurs de Métriques"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source']),
        ]
        unique_together = ['metric', 'timestamp', 'labels']
    
    def __str__(self):
        return f"{self.metric.name}: {self.value} @ {self.timestamp}"
