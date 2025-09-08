"""
Modèles pour le système de rapports automatiques
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class ReportTemplate(TimestampedModel):
    """Templates de rapports"""
    
    REPORT_TYPES = [
        ('users', 'Utilisateurs'),
        ('activity', 'Activité'),
        ('security', 'Sécurité'),
        ('performance', 'Performance'),
        ('system', 'Système'),
        ('errors', 'Erreurs'),
        ('api_usage', 'Utilisation API'),
        ('custom', 'Personnalisé'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    description = models.TextField(blank=True, verbose_name="Description")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Type de rapport")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='json', verbose_name="Format")
    
    # Configuration
    query_config = models.JSONField(verbose_name="Configuration de requête")
    template_config = models.JSONField(default=dict, verbose_name="Configuration du template")
    filters = models.JSONField(default=dict, verbose_name="Filtres")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_templates', verbose_name="Créé par")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    class Meta:
        verbose_name = "Template de rapport"
        verbose_name_plural = "Templates de rapport"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class ScheduledReport(TimestampedModel):
    """Rapports programmés"""
    
    FREQUENCY_CHOICES = [
        ('hourly', 'Horaire'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
        ('custom', 'Personnalisé'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('paused', 'En pause'),
        ('error', 'Erreur'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom du rapport programmé")
    description = models.TextField(blank=True, verbose_name="Description")
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='scheduled_reports', verbose_name="Template")
    
    # Programmation
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Fréquence")
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name="Expression CRON")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Prochaine exécution")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Dernière exécution")
    
    # Configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    recipients = models.JSONField(default=list, verbose_name="Destinataires")
    notification_channels = models.JSONField(default=list, verbose_name="Canaux de notification")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_scheduled_reports', verbose_name="Créé par")
    retention_days = models.IntegerField(default=30, verbose_name="Rétention (jours)")
    
    class Meta:
        verbose_name = "Rapport programmé"
        verbose_name_plural = "Rapports programmés"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def calculate_next_run(self):
        """Calcule la prochaine exécution"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.frequency == 'hourly':
            return now + timedelta(hours=1)
        elif self.frequency == 'daily':
            return now + timedelta(days=1)
        elif self.frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            return now + timedelta(days=30)
        elif self.frequency == 'quarterly':
            return now + timedelta(days=90)
        elif self.frequency == 'yearly':
            return now + timedelta(days=365)
        
        return now


class ReportExecution(TimestampedModel):
    """Exécutions de rapports"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    # Informations de base
    scheduled_report = models.ForeignKey(ScheduledReport, on_delete=models.CASCADE, related_name='executions', verbose_name="Rapport programmé")
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='executions', verbose_name="Template")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Exécution
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Début")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin")
    duration = models.DurationField(null=True, blank=True, verbose_name="Durée")
    
    # Résultats
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Chemin du fichier")
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="Taille du fichier")
    record_count = models.IntegerField(null=True, blank=True, verbose_name="Nombre d'enregistrements")
    
    # Métadonnées
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    execution_log = models.JSONField(default=list, verbose_name="Log d'exécution")
    parameters = models.JSONField(default=dict, verbose_name="Paramètres")
    
    class Meta:
        verbose_name = "Exécution de rapport"
        verbose_name_plural = "Exécutions de rapport"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.scheduled_report.name} - {self.get_status_display()}"
    
    def start(self):
        """Démarre l'exécution"""
        from django.utils import timezone
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def complete(self, file_path=None, record_count=None):
        """Termine l'exécution avec succès"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.file_path = file_path or ''
        self.record_count = record_count
        
        if self.started_at:
            self.duration = self.completed_at - self.started_at
        
        self.save()
    
    def fail(self, error_message):
        """Marque l'exécution comme échouée"""
        from django.utils import timezone
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        
        if self.started_at:
            self.duration = self.completed_at - self.started_at
        
        self.save()

