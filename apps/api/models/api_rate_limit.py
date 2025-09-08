"""
Modèle pour la gestion des limites de taux d'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIRateLimit(TimestampedModel):
    """Limites de taux pour l'API"""
    
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('user', 'Utilisateur'),
        ('ip', 'Adresse IP'),
        ('endpoint', 'Endpoint'),
        ('api_key', 'Clé API'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, verbose_name="Portée")
    
    # Configuration des limites
    requests_per_minute = models.IntegerField(default=60, verbose_name="Requêtes par minute")
    requests_per_hour = models.IntegerField(default=1000, verbose_name="Requêtes par heure")
    requests_per_day = models.IntegerField(default=10000, verbose_name="Requêtes par jour")
    burst_limit = models.IntegerField(default=10, verbose_name="Limite de rafale")
    
    # Configuration avancée
    window_size = models.IntegerField(default=60, verbose_name="Taille de fenêtre (secondes)")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Cibles spécifiques
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='rate_limits', verbose_name="Utilisateur cible")
    target_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP cible")
    target_endpoint = models.ForeignKey('api.APIEndpoint', on_delete=models.CASCADE, null=True, blank=True, related_name='rate_limits', verbose_name="Endpoint cible")
    target_api_key = models.CharField(max_length=100, blank=True, verbose_name="Clé API cible")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rate_limits', verbose_name="Créé par")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    class Meta:
        verbose_name = "Limite de taux d'API"
        verbose_name_plural = "Limites de taux d'API"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_scope_display()})"
    
    def get_limit_for_period(self, period):
        """Récupère la limite pour une période donnée"""
        if period == 'minute':
            return self.requests_per_minute
        elif period == 'hour':
            return self.requests_per_hour
        elif period == 'day':
            return self.requests_per_day
        return self.requests_per_minute
    
    def is_applicable_to(self, user=None, ip=None, endpoint=None, api_key=None):
        """Vérifie si cette limite s'applique à la requête"""
        if not self.is_active:
            return False
        
        if self.scope == 'global':
            return True
        elif self.scope == 'user' and user and self.target_user == user:
            return True
        elif self.scope == 'ip' and ip and self.target_ip == ip:
            return True
        elif self.scope == 'endpoint' and endpoint and self.target_endpoint == endpoint:
            return True
        elif self.scope == 'api_key' and api_key and self.target_api_key == api_key:
            return True
        
        return False


class APIRateLimitUsage(TimestampedModel):
    """Suivi de l'utilisation des limites de taux"""
    
    # Informations de base
    rate_limit = models.ForeignKey(APIRateLimit, on_delete=models.CASCADE, related_name='usage_logs', verbose_name="Limite de taux")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rate_limit_usage', verbose_name="Utilisateur")
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    endpoint = models.ForeignKey('api.APIEndpoint', on_delete=models.SET_NULL, null=True, blank=True, related_name='rate_limit_usage', verbose_name="Endpoint")
    api_key = models.CharField(max_length=100, blank=True, verbose_name="Clé API")
    
    # Compteurs
    requests_count = models.IntegerField(default=0, verbose_name="Nombre de requêtes")
    window_start = models.DateTimeField(verbose_name="Début de fenêtre")
    window_end = models.DateTimeField(verbose_name="Fin de fenêtre")
    
    # Statut
    is_limited = models.BooleanField(default=False, verbose_name="Limité")
    limit_reached_at = models.DateTimeField(null=True, blank=True, verbose_name="Limite atteinte à")
    
    class Meta:
        verbose_name = "Utilisation de limite de taux"
        verbose_name_plural = "Utilisations de limites de taux"
        unique_together = ['rate_limit', 'user', 'ip_address', 'endpoint', 'api_key', 'window_start']
        ordering = ['-window_start']
    
    def __str__(self):
        return f"{self.rate_limit.name} - {self.requests_count} requêtes"
    
    @property
    def is_over_limit(self):
        """Vérifie si la limite est dépassée"""
        return self.requests_count > self.rate_limit.requests_per_minute

