"""
Modèle pour la gestion des endpoints d'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIEndpoint(TimestampedModel):
    """Endpoints de l'API"""
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('deprecated', 'Déprécié'),
        ('retired', 'Retiré'),
        ('maintenance', 'Maintenance'),
    ]
    
    # Informations de base
    api_version = models.ForeignKey('api.APIVersion', on_delete=models.CASCADE, related_name='endpoints', verbose_name="Version d'API")
    path = models.CharField(max_length=500, verbose_name="Chemin")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="Méthode HTTP")
    name = models.CharField(max_length=200, verbose_name="Nom de l'endpoint")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    is_public = models.BooleanField(default=True, verbose_name="Public")
    requires_auth = models.BooleanField(default=True, verbose_name="Authentification requise")
    rate_limit = models.IntegerField(null=True, blank=True, verbose_name="Limite de taux (req/min)")
    
    # Documentation
    parameters = models.JSONField(default=list, verbose_name="Paramètres")
    request_schema = models.JSONField(default=dict, verbose_name="Schéma de requête")
    response_schema = models.JSONField(default=dict, verbose_name="Schéma de réponse")
    examples = models.JSONField(default=list, verbose_name="Exemples")
    
    # Métadonnées
    tags = models.JSONField(default=list, verbose_name="Tags")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_endpoints', verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Endpoint d'API"
        verbose_name_plural = "Endpoints d'API"
        unique_together = ['api_version', 'path', 'method']
        ordering = ['api_version', 'path', 'method']
    
    def __str__(self):
        return f"{self.method} {self.path} (v{self.api_version.version})"
    
    @property
    def full_path(self):
        """Chemin complet avec version"""
        return f"/api/v{self.api_version.version}{self.path}"
    
    @property
    def is_active(self):
        """Vérifie si l'endpoint est actif"""
        return self.status == 'active'
    
    @property
    def is_deprecated(self):
        """Vérifie si l'endpoint est déprécié"""
        return self.status == 'deprecated'



