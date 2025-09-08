"""
Modèle pour la gestion des versions d'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIVersion(TimestampedModel):
    """Versions de l'API"""
    
    STATUS_CHOICES = [
        ('development', 'Développement'),
        ('beta', 'Bêta'),
        ('stable', 'Stable'),
        ('deprecated', 'Déprécié'),
        ('retired', 'Retiré'),
    ]
    
    # Informations de base
    version = models.CharField(max_length=20, unique=True, verbose_name="Version")
    name = models.CharField(max_length=100, verbose_name="Nom de la version")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development', verbose_name="Statut")
    
    # Dates importantes
    release_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de sortie")
    deprecation_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de dépréciation")
    retirement_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de retrait")
    
    # Configuration
    is_default = models.BooleanField(default=False, verbose_name="Version par défaut")
    is_public = models.BooleanField(default=True, verbose_name="Publique")
    changelog = models.JSONField(default=list, verbose_name="Changelog")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_versions', verbose_name="Créé par")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    class Meta:
        verbose_name = "Version d'API"
        verbose_name_plural = "Versions d'API"
        ordering = ['-version']
    
    def __str__(self):
        return f"API v{self.version} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule version est par défaut
        if self.is_default:
            APIVersion.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Vérifie si la version est active"""
        return self.status in ['stable', 'beta']
    
    @property
    def is_deprecated(self):
        """Vérifie si la version est dépréciée"""
        return self.status == 'deprecated'
    
    @property
    def is_retired(self):
        """Vérifie si la version est retirée"""
        return self.status == 'retired'



