"""
Modèle pour les rapports d'administration
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AdminReport(TimestampedModel):
    """Rapports d'administration"""
    
    REPORT_TYPES = [
        ('users', 'Utilisateurs'),
        ('activity', 'Activité'),
        ('security', 'Sécurité'),
        ('performance', 'Performance'),
        ('system', 'Système'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_reports')
    parameters = models.JSONField(default=dict)
    results = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Rapport d'administration"
        verbose_name_plural = "Rapports d'administration"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

