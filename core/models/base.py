"""
Modèles de base pour toutes les applications
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class BaseModel(models.Model):
    """
    Modèle de base avec ID UUID et métadonnées communes
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class TimestampedModel(BaseModel):
    """
    Modèle avec timestamps de création et modification
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
    
    @property
    def age(self):
        """Âge de l'objet en secondes"""
        return (timezone.now() - self.created_at).total_seconds()
    
    @property
    def is_recent(self):
        """Vérifie si l'objet a été créé récemment (moins de 24h)"""
        return self.age < 86400  # 24 heures


class SoftDeleteModel(TimestampedModel):
    """
    Modèle avec suppression douce (soft delete)
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
    
    @classmethod
    def active_objects(cls):
        """Manager pour les objets non supprimés"""
        return cls.objects.filter(is_deleted=False)
    
    @classmethod
    def deleted_objects(cls):
        """Manager pour les objets supprimés"""
        return cls.objects.filter(is_deleted=True)


class CreatedByModel(TimestampedModel):
    """
    Modèle avec information sur le créateur
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
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec attribution automatique du créateur"""
        if not self.pk and not self.created_by:
            # Si c'est une création et qu'aucun créateur n'est défini
            # On essaie de récupérer l'utilisateur depuis le contexte
            from django.contrib.auth import get_user
            try:
                user = get_user()
                if user and user.is_authenticated:
                    self.created_by = user
            except:
                pass
        super().save(*args, **kwargs)


class UpdatedByModel(CreatedByModel):
    """
    Modèle avec information sur le créateur et le dernier modificateur
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
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec attribution automatique du modificateur"""
        if self.pk:  # Si c'est une modification
            from django.contrib.auth import get_user
            try:
                user = get_user()
                if user and user.is_authenticated:
                    self.updated_by = user
            except:
                pass
        super().save(*args, **kwargs)


class StatusModel(TimestampedModel):
    """
    Modèle avec statut et gestion des états
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
    
    def activate(self):
        """Active l'objet"""
        self.status = 'active'
        self.save()
    
    def deactivate(self):
        """Désactive l'objet"""
        self.status = 'inactive'
        self.save()
    
    def archive(self):
        """Archive l'objet"""
        self.status = 'archived'
        self.save()


class OrderingModel(TimestampedModel):
    """
    Modèle avec ordre personnalisable
    """
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre"
    )
    
    class Meta:
        abstract = True
        ordering = ['order', '-created_at']
    
    def move_up(self):
        """Déplace l'objet vers le haut"""
        if self.order > 0:
            self.order -= 1
            self.save()
    
    def move_down(self):
        """Déplace l'objet vers le bas"""
        self.order += 1
        self.save()
    
    def move_to_top(self):
        """Déplace l'objet en première position"""
        self.order = 0
        self.save()
    
    def move_to_bottom(self):
        """Déplace l'objet en dernière position"""
        max_order = self.__class__.objects.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        self.order = max_order + 1
        self.save()


class SlugModel(TimestampedModel):
    """
    Modèle avec slug automatique
    """
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug"
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Génération automatique du slug"""
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)
    
    def generate_slug(self):
        """Génère un slug unique basé sur le nom/titre"""
        from django.utils.text import slugify
        from django.utils import timezone
        
        # Utilise le nom, titre ou ID comme base
        base = getattr(self, 'name', None) or getattr(self, 'title', None) or str(self.id)
        slug = slugify(base)
        
        # Ajoute un timestamp si le slug existe déjà
        if self.__class__.objects.filter(slug=slug).exists():
            slug = f"{slug}-{int(timezone.now().timestamp())}"
        
        return slug


class CacheModel(TimestampedModel):
    """
    Modèle avec gestion du cache
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

