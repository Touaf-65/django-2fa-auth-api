"""
Modèle pour le suivi de l'utilisation de l'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIUsage(TimestampedModel):
    """Suivi de l'utilisation de l'API"""
    
    STATUS_CHOICES = [
        ('success', 'Succès'),
        ('error', 'Erreur'),
        ('rate_limited', 'Limité par le taux'),
        ('unauthorized', 'Non autorisé'),
        ('forbidden', 'Interdit'),
        ('not_found', 'Non trouvé'),
        ('server_error', 'Erreur serveur'),
    ]
    
    # Informations de base
    api_version = models.ForeignKey('api.APIVersion', on_delete=models.CASCADE, related_name='usage_logs', verbose_name="Version d'API")
    endpoint = models.ForeignKey('api.APIEndpoint', on_delete=models.CASCADE, related_name='usage_logs', verbose_name="Endpoint")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_usage', verbose_name="Utilisateur")
    
    # Détails de la requête
    method = models.CharField(max_length=10, verbose_name="Méthode HTTP")
    path = models.CharField(max_length=500, verbose_name="Chemin")
    query_params = models.JSONField(default=dict, verbose_name="Paramètres de requête")
    request_headers = models.JSONField(default=dict, verbose_name="En-têtes de requête")
    request_body = models.TextField(blank=True, verbose_name="Corps de la requête")
    
    # Détails de la réponse
    status_code = models.IntegerField(verbose_name="Code de statut")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Statut")
    response_headers = models.JSONField(default=dict, verbose_name="En-têtes de réponse")
    response_body = models.TextField(blank=True, verbose_name="Corps de la réponse")
    
    # Métriques
    response_time = models.FloatField(verbose_name="Temps de réponse (ms)")
    request_size = models.IntegerField(default=0, verbose_name="Taille de la requête (bytes)")
    response_size = models.IntegerField(default=0, verbose_name="Taille de la réponse (bytes)")
    
    # Informations client
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    referer = models.URLField(blank=True, verbose_name="Référent")
    
    # Métadonnées
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    api_key = models.CharField(max_length=100, blank=True, verbose_name="Clé API")
    
    class Meta:
        verbose_name = "Utilisation d'API"
        verbose_name_plural = "Utilisations d'API"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_version', 'created_at']),
            models.Index(fields=['endpoint', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.response_time}ms)"
    
    @property
    def is_success(self):
        """Vérifie si la requête a réussi"""
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self):
        """Vérifie si la requête a échoué"""
        return self.status_code >= 400
    
    @property
    def is_rate_limited(self):
        """Vérifie si la requête a été limitée par le taux"""
        return self.status == 'rate_limited'



