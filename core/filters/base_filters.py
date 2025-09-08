"""
Filtres de base pour l'application Core
"""
import django_filters
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseFilterSet(django_filters.FilterSet):
    """Filtre de base avec fonctionnalités communes"""
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajoute des filtres communs si nécessaire
        self.add_common_filters()
    
    def add_common_filters(self):
        """Ajoute des filtres communs"""
        pass


class TimestampedFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec timestamps"""
    created_at = django_filters.DateTimeFromToRangeFilter()
    updated_at = django_filters.DateTimeFromToRangeFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        abstract = True


class SoftDeleteFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec suppression douce"""
    is_deleted = django_filters.BooleanFilter()
    deleted_after = django_filters.DateTimeFilter(field_name='deleted_at', lookup_expr='gte')
    deleted_before = django_filters.DateTimeFilter(field_name='deleted_at', lookup_expr='lte')
    deleted_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    
    class Meta:
        abstract = True


class StatusFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec statut"""
    status = django_filters.ChoiceFilter(choices=[
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('archived', 'Archivé'),
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('suspended', 'Suspendu'),
        ('deleted', 'Supprimé'),
    ])
    status_in = django_filters.BaseInFilter(field_name='status', lookup_expr='in')
    status_not = django_filters.ChoiceFilter(field_name='status', exclude=True)
    
    class Meta:
        abstract = True


class OrderingFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec ordre"""
    order = django_filters.NumberFilter()
    order_gte = django_filters.NumberFilter(field_name='order', lookup_expr='gte')
    order_lte = django_filters.NumberFilter(field_name='order', lookup_expr='lte')
    order_range = django_filters.RangeFilter(field_name='order')
    
    class Meta:
        abstract = True


class CreatedByFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec créateur"""
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    created_by_in = django_filters.BaseInFilter(field_name='created_by', lookup_expr='in')
    created_by_not = django_filters.ModelChoiceFilter(field_name='created_by', exclude=True, queryset=User.objects.all())
    
    class Meta:
        abstract = True


class UpdatedByFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec modificateur"""
    updated_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    updated_by_in = django_filters.BaseInFilter(field_name='updated_by', lookup_expr='in')
    updated_by_not = django_filters.ModelChoiceFilter(field_name='updated_by', exclude=True, queryset=User.objects.all())
    
    class Meta:
        abstract = True


class SlugFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec slug"""
    slug = django_filters.CharFilter(lookup_expr='icontains')
    slug_exact = django_filters.CharFilter(field_name='slug', lookup_expr='exact')
    slug_in = django_filters.BaseInFilter(field_name='slug', lookup_expr='in')
    slug_startswith = django_filters.CharFilter(field_name='slug', lookup_expr='startswith')
    slug_endswith = django_filters.CharFilter(field_name='slug', lookup_expr='endswith')
    
    class Meta:
        abstract = True


class CacheFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec cache"""
    cache_key = django_filters.CharFilter(lookup_expr='icontains')
    cache_expires_after = django_filters.DateTimeFilter(field_name='cache_expires_at', lookup_expr='gte')
    cache_expires_before = django_filters.DateTimeFilter(field_name='cache_expires_at', lookup_expr='lte')
    cache_expired = django_filters.BooleanFilter(method='filter_cache_expired')
    
    class Meta:
        abstract = True
    
    def filter_cache_expired(self, queryset, name, value):
        """Filtre les objets avec cache expiré"""
        from django.utils import timezone
        if value:
            return queryset.filter(cache_expires_at__lt=timezone.now())
        else:
            return queryset.filter(
                models.Q(cache_expires_at__gte=timezone.now()) | 
                models.Q(cache_expires_at__isnull=True)
            )


class NameFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec nom"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    name_exact = django_filters.CharFilter(field_name='name', lookup_expr='exact')
    name_in = django_filters.BaseInFilter(field_name='name', lookup_expr='in')
    name_startswith = django_filters.CharFilter(field_name='name', lookup_expr='startswith')
    name_endswith = django_filters.CharFilter(field_name='name', lookup_expr='endswith')
    
    class Meta:
        abstract = True


class DescriptionFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec description"""
    description = django_filters.CharFilter(lookup_expr='icontains')
    description_exact = django_filters.CharFilter(field_name='description', lookup_expr='exact')
    description_startswith = django_filters.CharFilter(field_name='description', lookup_expr='startswith')
    description_endswith = django_filters.CharFilter(field_name='description', lookup_expr='endswith')
    
    class Meta:
        abstract = True


class CodeFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec code"""
    code = django_filters.CharFilter(lookup_expr='icontains')
    code_exact = django_filters.CharFilter(field_name='code', lookup_expr='exact')
    code_in = django_filters.BaseInFilter(field_name='code', lookup_expr='in')
    code_startswith = django_filters.CharFilter(field_name='code', lookup_expr='startswith')
    code_endswith = django_filters.CharFilter(field_name='code', lookup_expr='endswith')
    
    class Meta:
        abstract = True


class VersionFilterSet(BaseFilterSet):
    """Filtre pour les modèles avec version"""
    version = django_filters.NumberFilter()
    version_gte = django_filters.NumberFilter(field_name='version', lookup_expr='gte')
    version_lte = django_filters.NumberFilter(field_name='version', lookup_expr='lte')
    version_range = django_filters.RangeFilter(field_name='version')
    
    class Meta:
        abstract = True
