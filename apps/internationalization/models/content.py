"""
Modèles pour la gestion du contenu multilingue
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import TimestampedModel

User = get_user_model()


class Content(TimestampedModel):
    """Contenu multilingue générique"""
    
    CONTENT_TYPE_CHOICES = [
        ('page', 'Page'),
        ('article', 'Article'),
        ('product', 'Produit'),
        ('category', 'Catégorie'),
        ('menu', 'Menu'),
        ('widget', 'Widget'),
        ('form', 'Formulaire'),
        ('email_template', 'Template Email'),
        ('notification_template', 'Template Notification'),
        ('api_message', 'Message API'),
        ('seo_meta', 'Méta SEO'),
    ]
    
    # Informations de base
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES)
    identifier = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Langue source
    source_language = models.ForeignKey(
        'Language', 
        on_delete=models.CASCADE, 
        related_name='source_content'
    )
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Propriétaire
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_content'
    )
    
    # Relation générique (optionnelle)
    content_object_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    content_object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_object_type', 'content_object_id')
    
    class Meta:
        verbose_name = "Contenu"
        verbose_name_plural = "Contenus"
        unique_together = ['content_type', 'identifier', 'source_language']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'identifier']),
            models.Index(fields=['source_language', 'is_active']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.content_type})"
    
    def get_translations(self):
        """Retourne toutes les traductions du contenu"""
        return self.translations.filter(is_active=True)
    
    def get_translation(self, language):
        """Retourne la traduction pour une langue spécifique"""
        try:
            return self.translations.get(language=language, is_active=True)
        except ContentTranslation.DoesNotExist:
            return None
    
    def get_available_languages(self):
        """Retourne toutes les langues disponibles pour ce contenu"""
        languages = [self.source_language]
        languages.extend([
            t.language for t in self.get_translations()
        ])
        return languages


class ContentTranslation(TimestampedModel):
    """Traduction d'un contenu"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending_review', 'En Attente de Révision'),
        ('approved', 'Approuvé'),
        ('published', 'Publié'),
        ('rejected', 'Rejeté'),
    ]
    
    # Relations
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='content_translations')
    
    # Contenu traduit
    translated_title = models.CharField(max_length=255)
    translated_description = models.TextField(blank=True)
    translated_content = models.TextField(blank=True)
    
    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Traducteur
    translated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='content_translations_made'
    )
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='content_translations_reviewed'
    )
    
    # Dates
    translated_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées de traduction
    translation_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Bon'),
            ('fair', 'Correct'),
            ('poor', 'Médiocre'),
        ],
        blank=True
    )
    notes = models.TextField(blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Traduction de Contenu"
        verbose_name_plural = "Traductions de Contenu"
        unique_together = ['content', 'language']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content', 'language']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['language', 'status']),
        ]
    
    def __str__(self):
        return f"{self.content.title} -> {self.language.code}"
    
    @property
    def is_published(self):
        """Vérifie si la traduction est publiée"""
        return self.status == 'published'
    
    @property
    def is_approved(self):
        """Vérifie si la traduction est approuvée"""
        return self.status in ['approved', 'published']
    
    def save(self, *args, **kwargs):
        # Générer le slug si non fourni
        if not self.slug and self.translated_title:
            from django.utils.text import slugify
            self.slug = slugify(self.translated_title)
        super().save(*args, **kwargs)

