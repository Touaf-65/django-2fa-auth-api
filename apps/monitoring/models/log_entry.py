"""
Modèle pour les entrées de log structurées
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class LogEntry(TimestampedModel):
    """Entrée de log structurée"""
    
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    SOURCE_CHOICES = [
        ('api', 'API'),
        ('auth', 'Authentication'),
        ('user', 'User'),
        ('admin', 'Admin'),
        ('security', 'Security'),
        ('system', 'System'),
        ('database', 'Database'),
        ('external', 'External Service'),
        ('monitoring', 'Monitoring'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, db_index=True)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='monitoring_logs')
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Métadonnées structurées
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Contexte de l'application
    app_name = models.CharField(max_length=50, blank=True, db_index=True)
    module_name = models.CharField(max_length=100, blank=True)
    function_name = models.CharField(max_length=100, blank=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Contexte de la requête
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=500, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    
    # Exception/Erreur
    exception_type = models.CharField(max_length=100, blank=True)
    exception_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    class Meta:
        db_table = 'monitoring_log_entry'
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['app_name', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.level}] {self.source}: {self.message[:100]}"
    
    @property
    def is_error(self):
        """Vérifie si c'est une erreur"""
        return self.level in ['ERROR', 'CRITICAL']
    
    @property
    def is_warning(self):
        """Vérifie si c'est un avertissement"""
        return self.level == 'WARNING'
    
    def get_metadata_value(self, key, default=None):
        """Récupère une valeur des métadonnées"""
        return self.metadata.get(key, default)
    
    def add_tag(self, tag):
        """Ajoute un tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """Supprime un tag"""
        if tag in self.tags:
            self.tags.remove(tag)

