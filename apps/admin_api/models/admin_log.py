"""
Modèle pour les logs d'administration
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AdminLog(TimestampedModel):
    """Logs d'administration pour audit"""
    
    LOG_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('critical', 'Critique'),
    ]
    
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Log d'administration"
        verbose_name_plural = "Logs d'administration"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level.upper()} - {self.action} - {self.admin_user.email}"



