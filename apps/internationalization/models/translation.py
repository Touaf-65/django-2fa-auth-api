"""
Modèles pour la gestion des traductions
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class TranslationKey(TimestampedModel):
    """Clé de traduction (texte source)"""
    
    CONTEXT_CHOICES = [
        ('ui', 'Interface Utilisateur'),
        ('email', 'Email'),
        ('notification', 'Notification'),
        ('error', 'Message d\'Erreur'),
        ('success', 'Message de Succès'),
        ('warning', 'Avertissement'),
        ('help', 'Aide'),
        ('documentation', 'Documentation'),
        ('api', 'API'),
        ('admin', 'Administration'),
        ('content', 'Contenu'),
        ('seo', 'SEO'),
    ]
    
    key = models.CharField(max_length=255, unique=True, db_index=True)
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default='ui')
    source_text = models.TextField()
    source_language = models.ForeignKey(
        'Language', 
        on_delete=models.CASCADE, 
        related_name='source_keys'
    )
    
    # Métadonnées
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.CharField(
        max_length=10,
        choices=[
            ('high', 'Haute'),
            ('medium', 'Moyenne'),
            ('low', 'Faible'),
        ],
        default='medium'
    )
    
    # Statistiques
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Clé de Traduction"
        verbose_name_plural = "Clés de Traduction"
        ordering = ['key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['context', 'is_active']),
            models.Index(fields=['source_language']),
        ]
    
    def __str__(self):
        return f"{self.key} ({self.context})"


class Translation(TimestampedModel):
    """Traduction d'une clé dans une langue spécifique"""
    
    STATUS_CHOICES = [
        ('pending', 'En Attente'),
        ('auto_translated', 'Traduit Automatiquement'),
        ('human_translated', 'Traduit par un Humain'),
        ('reviewed', 'Révisé'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    translation_key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='translations')
    translated_text = models.TextField()
    
    # Métadonnées de traduction
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confidence_score = models.FloatField(null=True, blank=True)  # Score de confiance (0-1)
    translation_service = models.CharField(max_length=50, blank=True)  # Service utilisé
    
    # Traducteur
    translated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='translations_made'
    )
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='translations_reviewed'
    )
    
    # Dates
    translated_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Traduction"
        verbose_name_plural = "Traductions"
        unique_together = ['translation_key', 'language']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['translation_key', 'language']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['language', 'status']),
        ]
    
    def __str__(self):
        return f"{self.translation_key.key} -> {self.language.code}"
    
    @property
    def is_approved(self):
        """Vérifie si la traduction est approuvée"""
        return self.status == 'approved'
    
    @property
    def is_human_translated(self):
        """Vérifie si la traduction est faite par un humain"""
        return self.status in ['human_translated', 'reviewed', 'approved']


class TranslationRequest(TimestampedModel):
    """Demande de traduction"""
    
    STATUS_CHOICES = [
        ('pending', 'En Attente'),
        ('processing', 'En Cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'Haute'),
        ('medium', 'Moyenne'),
        ('low', 'Faible'),
    ]
    
    # Informations de base
    source_text = models.TextField()
    source_language = models.ForeignKey(
        'Language', 
        on_delete=models.CASCADE, 
        related_name='source_requests'
    )
    target_languages = models.ManyToManyField('Language', related_name='target_requests')
    
    # Métadonnées
    context = models.CharField(max_length=20, choices=TranslationKey.CONTEXT_CHOICES, default='ui')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Demandeur
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='translation_requests'
    )
    
    # Configuration de traduction
    use_auto_translation = models.BooleanField(default=True)
    require_human_review = models.BooleanField(default=False)
    translation_service = models.CharField(max_length=50, blank=True)
    
    # Résultats
    completed_translations = models.ManyToManyField(
        Translation, 
        blank=True, 
        related_name='source_requests'
    )
    error_message = models.TextField(blank=True)
    
    # Dates
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Demande de Traduction"
        verbose_name_plural = "Demandes de Traduction"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['requested_by', 'created_at']),
            models.Index(fields=['source_language']),
        ]
    
    def __str__(self):
        return f"Traduction {self.id} - {self.source_text[:50]}"
    
    @property
    def progress_percentage(self):
        """Pourcentage de progression"""
        if not self.target_languages.exists():
            return 0
        
        completed = self.completed_translations.count()
        total = self.target_languages.count()
        return (completed / total) * 100 if total > 0 else 0
    
    @property
    def is_completed(self):
        """Vérifie si la demande est terminée"""
        return self.status == 'completed'

