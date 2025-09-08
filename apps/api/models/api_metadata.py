"""
Modèle pour les métadonnées de l'API
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class APIMetadata(TimestampedModel):
    """Métadonnées de l'API"""
    
    METADATA_TYPES = [
        ('info', 'Informations générales'),
        ('contact', 'Contact'),
        ('license', 'Licence'),
        ('terms', 'Conditions d\'utilisation'),
        ('privacy', 'Politique de confidentialité'),
        ('changelog', 'Changelog'),
        ('deprecation', 'Avertissement de dépréciation'),
        ('maintenance', 'Maintenance'),
        ('custom', 'Personnalisé'),
    ]
    
    # Informations de base
    api_version = models.ForeignKey('api.APIVersion', on_delete=models.CASCADE, related_name='metadata', verbose_name="Version d'API")
    metadata_type = models.CharField(max_length=20, choices=METADATA_TYPES, verbose_name="Type de métadonnée")
    key = models.CharField(max_length=100, verbose_name="Clé")
    value = models.JSONField(verbose_name="Valeur")
    
    # Configuration
    is_public = models.BooleanField(default=True, verbose_name="Public")
    is_required = models.BooleanField(default=False, verbose_name="Requis")
    display_order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Métadonnées
    description = models.TextField(blank=True, verbose_name="Description")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_metadata', verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Métadonnée d'API"
        verbose_name_plural = "Métadonnées d'API"
        unique_together = ['api_version', 'metadata_type', 'key']
        ordering = ['api_version', 'display_order', 'key']
    
    def __str__(self):
        return f"{self.api_version.version} - {self.get_metadata_type_display()} - {self.key}"


class APIDocumentation(TimestampedModel):
    """Documentation de l'API"""
    
    DOCUMENTATION_TYPES = [
        ('overview', 'Vue d\'ensemble'),
        ('getting_started', 'Premiers pas'),
        ('authentication', 'Authentification'),
        ('endpoints', 'Endpoints'),
        ('examples', 'Exemples'),
        ('sdk', 'SDK'),
        ('troubleshooting', 'Dépannage'),
        ('faq', 'FAQ'),
        ('changelog', 'Changelog'),
        ('migration', 'Guide de migration'),
    ]
    
    # Informations de base
    api_version = models.ForeignKey('api.APIVersion', on_delete=models.CASCADE, related_name='documentation', verbose_name="Version d'API")
    doc_type = models.CharField(max_length=20, choices=DOCUMENTATION_TYPES, verbose_name="Type de documentation")
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    
    # Configuration
    is_public = models.BooleanField(default=True, verbose_name="Public")
    is_featured = models.BooleanField(default=False, verbose_name="Mis en avant")
    display_order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Métadonnées
    summary = models.TextField(blank=True, verbose_name="Résumé")
    tags = models.JSONField(default=list, verbose_name="Tags")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_documentation', verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Documentation d'API"
        verbose_name_plural = "Documentations d'API"
        ordering = ['api_version', 'display_order', 'title']
    
    def __str__(self):
        return f"{self.api_version.version} - {self.get_doc_type_display()} - {self.title}"


class APISDK(TimestampedModel):
    """SDK pour l'API"""
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('php', 'PHP'),
        ('ruby', 'Ruby'),
        ('go', 'Go'),
        ('csharp', 'C#'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('dart', 'Dart'),
    ]
    
    # Informations de base
    api_version = models.ForeignKey('api.APIVersion', on_delete=models.CASCADE, related_name='sdks', verbose_name="Version d'API")
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, verbose_name="Langage")
    name = models.CharField(max_length=100, verbose_name="Nom du SDK")
    version = models.CharField(max_length=20, verbose_name="Version du SDK")
    
    # Configuration
    download_url = models.URLField(verbose_name="URL de téléchargement")
    repository_url = models.URLField(blank=True, verbose_name="URL du repository")
    documentation_url = models.URLField(blank=True, verbose_name="URL de la documentation")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Métadonnées
    description = models.TextField(blank=True, verbose_name="Description")
    installation_instructions = models.TextField(blank=True, verbose_name="Instructions d'installation")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_api_sdks', verbose_name="Créé par")
    
    class Meta:
        verbose_name = "SDK d'API"
        verbose_name_plural = "SDKs d'API"
        unique_together = ['api_version', 'language', 'version']
        ordering = ['api_version', 'language', 'version']
    
    def __str__(self):
        return f"{self.api_version.version} - {self.get_language_display()} SDK v{self.version}"



