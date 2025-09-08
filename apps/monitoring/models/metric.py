"""
Modèles pour les métriques de monitoring
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class Metric(TimestampedModel):
    """Métrique de monitoring"""
    
    TYPE_CHOICES = [
        ('counter', 'Counter'),
        ('gauge', 'Gauge'),
        ('histogram', 'Histogram'),
        ('summary', 'Summary'),
    ]
    
    UNIT_CHOICES = [
        ('bytes', 'Bytes'),
        ('seconds', 'Seconds'),
        ('milliseconds', 'Milliseconds'),
        ('count', 'Count'),
        ('percent', 'Percent'),
        ('requests', 'Requests'),
        ('users', 'Users'),
        ('errors', 'Errors'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='count')
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    retention_days = models.PositiveIntegerField(default=30)
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Seuils d'alerte
    warning_threshold = models.FloatField(null=True, blank=True)
    critical_threshold = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'monitoring_metric'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({self.name})"
    
    @property
    def is_counter(self):
        """Vérifie si c'est un compteur"""
        return self.metric_type == 'counter'
    
    @property
    def is_gauge(self):
        """Vérifie si c'est un gauge"""
        return self.metric_type == 'gauge'
    
    @property
    def is_histogram(self):
        """Vérifie si c'est un histogramme"""
        return self.metric_type == 'histogram'
    
    def get_latest_value(self):
        """Récupère la dernière valeur"""
        return self.values.order_by('-timestamp').first()
    
    def get_values_in_range(self, start_time, end_time):
        """Récupère les valeurs dans une plage de temps"""
        return self.values.filter(
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).order_by('timestamp')


class MetricValue(TimestampedModel):
    """Valeur d'une métrique"""
    
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='values')
    value = models.FloatField()
    timestamp = models.DateTimeField(db_index=True)
    
    # Contexte
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    
    # Métadonnées
    labels = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_metric_value'
        indexes = [
            models.Index(fields=['metric', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        ordering = ['-timestamp']
        unique_together = ['metric', 'timestamp', 'labels']
    
    def __str__(self):
        return f"{self.metric.name}: {self.value} at {self.timestamp}"
    
    @property
    def is_above_warning(self):
        """Vérifie si la valeur dépasse le seuil d'avertissement"""
        if self.metric.warning_threshold is None:
            return False
        return self.value > self.metric.warning_threshold
    
    @property
    def is_above_critical(self):
        """Vérifie si la valeur dépasse le seuil critique"""
        if self.metric.critical_threshold is None:
            return False
        return self.value > self.metric.critical_threshold
    
    def get_label_value(self, key, default=None):
        """Récupère une valeur de label"""
        return self.labels.get(key, default)
    
    def set_label(self, key, value):
        """Définit une valeur de label"""
        self.labels[key] = value



