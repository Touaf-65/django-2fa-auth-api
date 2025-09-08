"""
Managers personnalisés pour l'application Core
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseManager(models.Manager):
    """Manager de base avec fonctionnalités communes"""
    
    def get_or_none(self, **kwargs):
        """Récupère un objet ou None s'il n'existe pas"""
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
    
    def bulk_create_with_validation(self, objs, **kwargs):
        """Création en lot avec validation"""
        for obj in objs:
            obj.full_clean()
        return self.bulk_create(objs, **kwargs)


class TimestampedManager(BaseManager):
    """Manager pour les modèles avec timestamps"""
    
    def recent(self, days=7):
        """Récupère les objets récents"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def created_between(self, start_date, end_date):
        """Récupère les objets créés entre deux dates"""
        return self.filter(created_at__range=[start_date, end_date])


class SoftDeleteManager(BaseManager):
    """Manager pour les modèles avec suppression douce"""
    
    def get_queryset(self):
        """Récupère uniquement les objets non supprimés"""
        return super().get_queryset().filter(is_deleted=False)
    
    def deleted(self):
        """Récupère les objets supprimés"""
        return super().get_queryset().filter(is_deleted=True)
    
    def with_deleted(self):
        """Récupère tous les objets (supprimés et non supprimés)"""
        return super().get_queryset()


class StatusManager(BaseManager):
    """Manager pour les modèles avec statut"""
    
    def active(self):
        """Récupère les objets actifs"""
        return self.filter(status='active')
    
    def draft(self):
        """Récupère les objets en brouillon"""
        return self.filter(status='draft')
    
    def inactive(self):
        """Récupère les objets inactifs"""
        return self.filter(status='inactive')
    
    def archived(self):
        """Récupère les objets archivés"""
        return self.filter(status='archived')


class OrderingManager(BaseManager):
    """Manager pour les modèles avec ordre"""
    
    def ordered(self):
        """Récupère les objets triés par ordre"""
        return self.order_by('order', '-created_at')
    
    def reorder(self, new_order):
        """Réordonne les objets"""
        for index, obj_id in enumerate(new_order):
            self.filter(id=obj_id).update(order=index)


class CacheManager(BaseManager):
    """Manager pour les modèles avec cache"""
    
    def get_from_cache(self, cache_key):
        """Récupère un objet depuis le cache"""
        try:
            return self.get(cache_key=cache_key)
        except self.model.DoesNotExist:
            return None
    
    def invalidate_cache(self, cache_key):
        """Invalide le cache d'un objet"""
        obj = self.get_from_cache(cache_key)
        if obj:
            obj.invalidate_cache()


class CreatedByManager(BaseManager):
    """Manager pour les modèles avec créateur"""
    
    def created_by_user(self, user):
        """Récupère les objets créés par un utilisateur"""
        return self.filter(created_by=user)
    
    def created_by_users(self, users):
        """Récupère les objets créés par plusieurs utilisateurs"""
        return self.filter(created_by__in=users)


class UpdatedByManager(BaseManager):
    """Manager pour les modèles avec modificateur"""
    
    def updated_by_user(self, user):
        """Récupère les objets modifiés par un utilisateur"""
        return self.filter(updated_by=user)
    
    def updated_by_users(self, users):
        """Récupère les objets modifiés par plusieurs utilisateurs"""
        return self.filter(updated_by__in=users)

