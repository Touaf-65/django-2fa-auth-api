"""
Modèles pour les métriques de performance
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class PerformanceMetric(TimestampedModel):
    """Métrique de performance"""
    
    CATEGORY_CHOICES = [
        ('response_time', 'Response Time'),
        ('throughput', 'Throughput'),
        ('error_rate', 'Error Rate'),
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('disk_usage', 'Disk Usage'),
        ('network_io', 'Network I/O'),
        ('database_query', 'Database Query'),
        ('cache_hit_rate', 'Cache Hit Rate'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    collection_interval = models.PositiveIntegerField(default=60, help_text="Interval in seconds")
    
    # Seuils de performance
    warning_threshold = models.FloatField(null=True, blank=True)
    critical_threshold = models.FloatField(null=True, blank=True)
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_performance_metric'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({self.category})"
    
    def get_latest_value(self):
        """Récupère la dernière valeur"""
        return self.values.order_by('-timestamp').first()
    
    def get_average_value(self, hours=1):
        """Récupère la valeur moyenne sur une période"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        values = self.values.filter(
            timestamp__gte=start_time,
            timestamp__lte=end_time
        )
        
        if values.exists():
            return sum(v.value for v in values) / values.count()
        return None


class PerformanceReport(TimestampedModel):
    """Rapport de performance"""
    
    REPORT_TYPE_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Métriques incluses
    metrics = models.ManyToManyField(PerformanceMetric, related_name='reports')
    
    # Résultats
    summary = models.JSONField(default=dict, blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    # État
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_performance_report'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"
    
    @property
    def duration(self):
        """Durée de la période"""
        return self.period_end - self.period_start
    
    def generate_summary(self):
        """Génère un résumé du rapport"""
        summary = {
            'total_metrics': self.metrics.count(),
            'period_duration': str(self.duration),
            'report_type': self.report_type,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
        }
        
        # Ajouter des statistiques par métrique
        for metric in self.metrics.all():
            values = metric.values.filter(
                timestamp__gte=self.period_start,
                timestamp__lte=self.period_end
            )
            
            if values.exists():
                metric_summary = {
                    'count': values.count(),
                    'min': min(v.value for v in values),
                    'max': max(v.value for v in values),
                    'avg': sum(v.value for v in values) / values.count(),
                }
                summary[f'metric_{metric.name}'] = metric_summary
        
        return summary
    
    def mark_generated(self, user=None):
        """Marque le rapport comme généré"""
        from django.utils import timezone
        
        self.is_generated = True
        self.generated_at = timezone.now()
        self.generated_by = user
        self.summary = self.generate_summary()
        self.save()

