"""
Mixins pour les modèles Django
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class CreatedByMixin(models.Model):
    """
    Mixin pour ajouter un champ created_by
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_set',
        verbose_name="Créé par"
    )
    
    class Meta:
        abstract = True


class UpdatedByMixin(models.Model):
    """
    Mixin pour ajouter un champ updated_by
    """
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_set',
        verbose_name="Modifié par"
    )
    
    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """
    Mixin pour ajouter un champ slug
    """
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug"
    )
    
    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """
    Mixin pour ajouter un champ status
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('archived', 'Archivé'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Statut"
    )
    
    class Meta:
        abstract = True
    
    @property
    def is_active(self):
        """Vérifie si l'objet est actif"""
        return self.status == 'active'
    
    @property
    def is_draft(self):
        """Vérifie si l'objet est en brouillon"""
        return self.status == 'draft'


class OrderingMixin(models.Model):
    """
    Mixin pour ajouter un champ order
    """
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre"
    )
    
    class Meta:
        abstract = True
        ordering = ['order', '-created_at']


class CacheMixin(models.Model):
    """
    Mixin pour ajouter la gestion du cache
    """
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Clé de cache"
    )
    cache_data = models.JSONField(
        default=dict,
        verbose_name="Données de cache"
    )
    cache_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expiration du cache"
    )
    
    class Meta:
        abstract = True
    
    def is_cache_valid(self):
        """Vérifie si le cache est valide"""
        if not self.cache_expires_at:
            return True
        return timezone.now() < self.cache_expires_at
    
    def invalidate_cache(self):
        """Invalide le cache"""
        self.cache_data = {}
        self.cache_expires_at = None
        self.save()
    
    def set_cache(self, data, expires_in=None):
        """Définit les données de cache"""
        self.cache_data = data
        if expires_in:
            self.cache_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
        self.save()
    
    def get_cache(self):
        """Récupère les données de cache si valides"""
        if self.is_cache_valid():
            return self.cache_data
        return None


class SoftDeleteMixin(models.Model):
    """
    Mixin pour la suppression douce
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Supprimé"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de suppression"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_%(class)s_set',
        verbose_name="Supprimé par"
    )
    
    class Meta:
        abstract = True
    
    def delete(self, user=None, *args, **kwargs):
        """Suppression douce"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        """Suppression définitive"""
        super().delete(*args, **kwargs)
    
    def restore(self):
        """Restauration de l'objet supprimé"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()


class TimestampMixin(models.Model):
    """
    Mixin pour ajouter les timestamps
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """
    Mixin pour ajouter un ID UUID
    """
    import uuid
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )
    
    class Meta:
        abstract = True


class NameMixin(models.Model):
    """
    Mixin pour ajouter des champs nom et description
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Nom"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class CodeMixin(models.Model):
    """
    Mixin pour ajouter un champ code
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code"
    )
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.code


class VersionMixin(models.Model):
    """
    Mixin pour la gestion des versions
    """
    version = models.PositiveIntegerField(
        default=1,
        verbose_name="Version"
    )
    version_notes = models.TextField(
        blank=True,
        verbose_name="Notes de version"
    )
    
    class Meta:
        abstract = True
    
    def increment_version(self, notes=""):
        """Incrémente la version"""
        self.version += 1
        if notes:
            self.version_notes = notes
        self.save()



