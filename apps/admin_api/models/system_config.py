"""
Modèle pour la configuration système
"""
from django.db import models
from core.models import TimestampedModel


class SystemConfig(TimestampedModel):
    """Configuration système pour l'administration"""
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    is_public = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Configuration système"
        verbose_name_plural = "Configurations système"
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category}.{self.key}"

