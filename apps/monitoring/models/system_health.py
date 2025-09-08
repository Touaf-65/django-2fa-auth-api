"""
Modèles pour la santé du système
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class SystemHealth(TimestampedModel):
    """Santé générale du système"""
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('unknown', 'Unknown'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    overall_score = models.FloatField(default=0.0, help_text="Score de 0 à 100")
    
    # Composants
    database_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    cache_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    storage_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    external_services_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unknown')
    
    # Métriques système
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    network_latency = models.FloatField(null=True, blank=True)
    
    # Détails
    issues = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_system_health'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"System Health: {self.status} ({self.overall_score}%)"
    
    @property
    def is_healthy(self):
        """Vérifie si le système est en bonne santé"""
        return self.status == 'healthy'
    
    @property
    def is_degraded(self):
        """Vérifie si le système est dégradé"""
        return self.status == 'degraded'
    
    @property
    def is_unhealthy(self):
        """Vérifie si le système est en mauvaise santé"""
        return self.status == 'unhealthy'
    
    def calculate_overall_score(self):
        """Calcule le score global"""
        scores = []
        
        # Score basé sur les composants
        component_scores = {
            'database': 1.0 if self.database_status == 'healthy' else 0.5 if self.database_status == 'degraded' else 0.0,
            'cache': 1.0 if self.cache_status == 'healthy' else 0.5 if self.cache_status == 'degraded' else 0.0,
            'storage': 1.0 if self.storage_status == 'healthy' else 0.5 if self.storage_status == 'degraded' else 0.0,
            'external_services': 1.0 if self.external_services_status == 'healthy' else 0.5 if self.external_services_status == 'degraded' else 0.0,
        }
        
        scores.extend(component_scores.values())
        
        # Score basé sur les métriques système
        if self.cpu_usage is not None:
            cpu_score = max(0, 1.0 - (self.cpu_usage / 100))
            scores.append(cpu_score)
        
        if self.memory_usage is not None:
            memory_score = max(0, 1.0 - (self.memory_usage / 100))
            scores.append(memory_score)
        
        if self.disk_usage is not None:
            disk_score = max(0, 1.0 - (self.disk_usage / 100))
            scores.append(disk_score)
        
        if self.network_latency is not None:
            latency_score = max(0, 1.0 - (self.network_latency / 1000))  # 1000ms = 0 score
            scores.append(latency_score)
        
        if scores:
            self.overall_score = (sum(scores) / len(scores)) * 100
        else:
            self.overall_score = 0.0
        
        return self.overall_score
    
    def update_status(self):
        """Met à jour le statut basé sur le score"""
        score = self.calculate_overall_score()
        
        if score >= 90:
            self.status = 'healthy'
        elif score >= 70:
            self.status = 'degraded'
        else:
            self.status = 'unhealthy'
        
        self.save()


class HealthCheck(TimestampedModel):
    """Vérification de santé spécifique"""
    
    STATUS_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('warn', 'Warning'),
        ('unknown', 'Unknown'),
    ]
    
    TYPE_CHOICES = [
        ('database', 'Database'),
        ('cache', 'Cache'),
        ('storage', 'Storage'),
        ('external_api', 'External API'),
        ('queue', 'Queue'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    check_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    check_interval = models.PositiveIntegerField(default=60, help_text="Interval in seconds")
    timeout = models.PositiveIntegerField(default=30, help_text="Timeout in seconds")
    
    # Configuration de la vérification
    check_config = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_health_check'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({self.check_type})"
    
    def get_latest_result(self):
        """Récupère le dernier résultat"""
        return self.results.order_by('-created_at').first()
    
    def get_success_rate(self, hours=24):
        """Calcule le taux de succès sur une période"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        results = self.results.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        
        if results.exists():
            success_count = results.filter(status='pass').count()
            return (success_count / results.count()) * 100
        return 0.0


class HealthCheckResult(TimestampedModel):
    """Résultat d'une vérification de santé"""
    
    health_check = models.ForeignKey(HealthCheck, on_delete=models.CASCADE, related_name='results')
    status = models.CharField(max_length=10, choices=HealthCheck.STATUS_CHOICES)
    
    # Détails
    message = models.TextField(blank=True)
    response_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_health_check_result'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.health_check.name}: {self.status}"
    
    @property
    def is_pass(self):
        """Vérifie si la vérification a réussi"""
        return self.status == 'pass'
    
    @property
    def is_fail(self):
        """Vérifie si la vérification a échoué"""
        return self.status == 'fail'
    
    @property
    def is_warning(self):
        """Vérifie si la vérification a un avertissement"""
        return self.status == 'warn'

