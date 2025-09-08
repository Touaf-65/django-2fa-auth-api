"""
Modèle pour le dashboard d'administration
"""
from django.db import models
from core.models import TimestampedModel


class AdminDashboard(TimestampedModel):
    """Configuration du dashboard d'administration"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    widgets = models.JSONField(default=list)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Dashboard d'administration"
        verbose_name_plural = "Dashboards d'administration"
        ordering = ['name']
    
    def __str__(self):
        return self.name

