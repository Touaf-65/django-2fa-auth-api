"""
Signals pour l'API App
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import APIVersion, APIEndpoint, APIUsage


@receiver(post_save, sender=APIVersion)
def invalidate_version_cache(sender, instance, **kwargs):
    """Invalide le cache des versions d'API"""
    cache_keys = [
        'api_current_version',
        'api_available_versions',
        f'api_version_{instance.version}',
    ]
    
    for key in cache_keys:
        cache.delete(key)


@receiver(post_save, sender=APIEndpoint)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    """Invalide le cache des endpoints d'API"""
    cache_keys = [
        f'api_endpoints_{instance.api_version.version}',
        f'api_endpoint_{instance.id}',
    ]
    
    for key in cache_keys:
        cache.delete(key)


@receiver(post_save, sender=APIUsage)
def invalidate_usage_cache(sender, instance, **kwargs):
    """Invalide le cache des statistiques d'utilisation"""
    # Invalide les caches des statistiques d'utilisation
    cache_patterns = [
        'api_usage_stats_*',
        'api_usage_trends_*',
        'api_user_usage_*',
        'api_endpoint_usage_*',
    ]
    
    # Note: Dans un environnement de production, vous pourriez utiliser
    # un système de cache plus sophistiqué comme Redis avec des patterns
    for pattern in cache_patterns:
        # Ici vous pouvez implémenter une logique pour invalider
        # les caches correspondant au pattern
        pass



