"""
Modèles pour l'export de données Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class ExportFormat(TimestampedModel):
    """Format d'export supporté"""
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    description = models.TextField(blank=True)
    mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=10)
    
    # Configuration
    template_path = models.CharField(max_length=200, blank=True)
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Format d'Export"
        verbose_name_plural = "Formats d'Export"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DataExport(TimestampedModel):
    """Export de données"""
    
    STATUS_CHOICES = [
        ('pending', 'En Attente'),
        ('processing', 'Traitement'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
        ('expired', 'Expiré'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    export_format = models.ForeignKey(ExportFormat, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Configuration de l'export
    data_source = models.CharField(max_length=100)
    query = models.TextField(blank=True)
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list)
    
    # Paramètres temporels
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)
    
    # Fichier généré
    file_path = models.CharField(max_length=500, blank=True)
    file_name = models.CharField(max_length=200, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    
    # Métadonnées
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_analytics_exports')
    processed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Options d'export
    include_metadata = models.BooleanField(default=True)
    compression_enabled = models.BooleanField(default=False)
    password_protected = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Export de Données"
        verbose_name_plural = "Exports de Données"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['requested_by', 'created_at']),
            models.Index(fields=['export_format']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
