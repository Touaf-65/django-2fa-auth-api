"""
Modèle pour les health checks de l'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIHealthCheck(TimestampedModel):
    """Health checks de l'API"""
    
    STATUS_CHOICES = [
        ('healthy', 'En bonne santé'),
        ('degraded', 'Dégradé'),
        ('unhealthy', 'Malsain'),
        ('unknown', 'Inconnu'),
    ]
    
    CHECK_TYPES = [
        ('database', 'Base de données'),
        ('cache', 'Cache'),
        ('external_api', 'API externe'),
        ('storage', 'Stockage'),
        ('queue', 'File d\'attente'),
        ('custom', 'Personnalisé'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES, verbose_name="Type de vérification")
    
    # Configuration
    endpoint_url = models.URLField(blank=True, verbose_name="URL de l'endpoint")
    check_interval = models.IntegerField(default=60, verbose_name="Intervalle de vérification (secondes)")
    timeout = models.IntegerField(default=30, verbose_name="Timeout (secondes)")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Configuration avancée
    expected_status_code = models.IntegerField(default=200, verbose_name="Code de statut attendu")
    expected_response = models.TextField(blank=True, verbose_name="Réponse attendue")
    headers = models.JSONField(default=dict, verbose_name="En-têtes")
    body = models.TextField(blank=True, verbose_name="Corps de la requête")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_health_checks', verbose_name="Créé par")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    class Meta:
        verbose_name = "Health Check d'API"
        verbose_name_plural = "Health Checks d'API"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_check_type_display()})"


class APIHealthCheckResult(TimestampedModel):
    """Résultats des health checks"""
    
    # Informations de base
    health_check = models.ForeignKey(APIHealthCheck, on_delete=models.CASCADE, related_name='results', verbose_name="Health Check")
    status = models.CharField(max_length=20, choices=APIHealthCheck.STATUS_CHOICES, verbose_name="Statut")
    
    # Détails de la vérification
    response_time = models.FloatField(verbose_name="Temps de réponse (ms)")
    status_code = models.IntegerField(null=True, blank=True, verbose_name="Code de statut")
    response_body = models.TextField(blank=True, verbose_name="Corps de la réponse")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    # Métadonnées
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Vérifié à")
    
    class Meta:
        verbose_name = "Résultat de Health Check"
        verbose_name_plural = "Résultats de Health Checks"
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.health_check.name} - {self.get_status_display()} ({self.response_time}ms)"
    
    @property
    def is_healthy(self):
        """Vérifie si le health check est en bonne santé"""
        return self.status == 'healthy'
    
    @property
    def is_degraded(self):
        """Vérifie si le health check est dégradé"""
        return self.status == 'degraded'
    
    @property
    def is_unhealthy(self):
        """Vérifie si le health check est malsain"""
        return self.status == 'unhealthy'


class APISystemStatus(TimestampedModel):
    """Statut global du système API"""
    
    # Informations de base
    overall_status = models.CharField(max_length=20, choices=APIHealthCheck.STATUS_CHOICES, verbose_name="Statut global")
    message = models.TextField(blank=True, verbose_name="Message")
    
    # Métriques
    total_requests = models.IntegerField(default=0, verbose_name="Total des requêtes")
    successful_requests = models.IntegerField(default=0, verbose_name="Requêtes réussies")
    failed_requests = models.IntegerField(default=0, verbose_name="Requêtes échouées")
    average_response_time = models.FloatField(default=0, verbose_name="Temps de réponse moyen (ms)")
    
    # Health checks
    healthy_checks = models.IntegerField(default=0, verbose_name="Health checks sains")
    degraded_checks = models.IntegerField(default=0, verbose_name="Health checks dégradés")
    unhealthy_checks = models.IntegerField(default=0, verbose_name="Health checks malsains")
    
    # Métadonnées
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Vérifié à")
    
    class Meta:
        verbose_name = "Statut du système API"
        verbose_name_plural = "Statuts du système API"
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"Système API - {self.get_overall_status_display()}"
    
    @property
    def success_rate(self):
        """Taux de succès des requêtes"""
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self):
        """Taux d'échec des requêtes"""
        if self.total_requests == 0:
            return 0
        return (self.failed_requests / self.total_requests) * 100

