"""
Modèles pour les rapports Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class ReportTemplate(TimestampedModel):
    """Template de rapport prédéfini"""
    
    TYPE_CHOICES = [
        ('user_activity', 'Activité Utilisateur'),
        ('security_audit', 'Audit Sécurité'),
        ('performance', 'Performance'),
        ('usage', 'Utilisation'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    template_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_analytics_report_templates')
    
    class Meta:
        verbose_name = "Template de Rapport"
        verbose_name_plural = "Templates de Rapports"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Report(TimestampedModel):
    """Rapport généré"""
    
    STATUS_CHOICES = [
        ('pending', 'En Attente'),
        ('generating', 'Génération'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=ReportTemplate.TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Configuration du rapport
    config = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)
    
    # Résultats
    data = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Métadonnées
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_analytics_reports')
    execution_time = models.FloatField(null=True, blank=True)  # en secondes
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['generated_by', 'created_at']),
            models.Index(fields=['date_range_start', 'date_range_end']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class ReportSchedule(TimestampedModel):
    """Planification de rapports automatiques"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    
    name = models.CharField(max_length=200)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    # Configuration de la planification
    cron_expression = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)
    
    # Destinataires
    recipients = models.JSONField(default=list)  # Liste d'emails
    notification_enabled = models.BooleanField(default=True)
    
    # Dernière exécution
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, choices=Report.STATUS_CHOICES, blank=True)
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_analytics_report_schedules')
    total_runs = models.PositiveIntegerField(default=0)
    successful_runs = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Planification de Rapport"
        verbose_name_plural = "Planifications de Rapports"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
