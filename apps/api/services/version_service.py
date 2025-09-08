"""
Service pour la gestion des versions d'API
"""
from django.utils import timezone
from django.core.cache import cache
from apps.api.models import APIVersion, APIEndpoint


class VersionService:
    """Service pour la gestion des versions d'API"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_current_version(self):
        """Récupère la version actuelle de l'API"""
        cache_key = 'api_current_version'
        version = cache.get(cache_key)
        
        if version is None:
            try:
                version = APIVersion.objects.filter(is_default=True, is_active=True).first()
                if version:
                    cache.set(cache_key, version, self.cache_timeout)
            except APIVersion.DoesNotExist:
                version = None
        
        return version
    
    def get_version(self, version_string):
        """Récupère une version spécifique"""
        cache_key = f'api_version_{version_string}'
        version = cache.get(cache_key)
        
        if version is None:
            try:
                version = APIVersion.objects.get(version=version_string, is_active=True)
                cache.set(cache_key, version, self.cache_timeout)
            except APIVersion.DoesNotExist:
                version = None
        
        return version
    
    def get_available_versions(self):
        """Récupère toutes les versions disponibles"""
        cache_key = 'api_available_versions'
        versions = cache.get(cache_key)
        
        if versions is None:
            versions = APIVersion.objects.filter(is_active=True).order_by('-version')
            cache.set(cache_key, list(versions), self.cache_timeout)
        
        return versions
    
    def get_version_info(self, version_string=None):
        """Récupère les informations complètes d'une version"""
        if version_string:
            version = self.get_version(version_string)
        else:
            version = self.get_current_version()
        
        if not version:
            return None
        
        # Récupère les endpoints de cette version
        endpoints = APIEndpoint.objects.filter(
            api_version=version,
            status='active'
        ).order_by('path', 'method')
        
        # Récupère les métadonnées
        metadata = version.metadata.filter(is_public=True).order_by('display_order')
        
        return {
            'version': version.version,
            'name': version.name,
            'description': version.description,
            'status': version.status,
            'release_date': version.release_date.isoformat() if version.release_date else None,
            'deprecation_date': version.deprecation_date.isoformat() if version.deprecation_date else None,
            'retirement_date': version.retirement_date.isoformat() if version.retirement_date else None,
            'is_default': version.is_default,
            'is_public': version.is_public,
            'changelog': version.changelog,
            'endpoints_count': endpoints.count(),
            'endpoints': [
                {
                    'path': endpoint.path,
                    'method': endpoint.method,
                    'name': endpoint.name,
                    'description': endpoint.description,
                    'requires_auth': endpoint.requires_auth,
                    'rate_limit': endpoint.rate_limit,
                }
                for endpoint in endpoints
            ],
            'metadata': {
                item.key: item.value
                for item in metadata
            },
            'tags': version.tags,
        }
    
    def get_version_comparison(self, version1, version2):
        """Compare deux versions de l'API"""
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not v1 or not v2:
            return None
        
        # Récupère les endpoints de chaque version
        endpoints1 = set(
            (endpoint.path, endpoint.method)
            for endpoint in APIEndpoint.objects.filter(api_version=v1, status='active')
        )
        endpoints2 = set(
            (endpoint.path, endpoint.method)
            for endpoint in APIEndpoint.objects.filter(api_version=v2, status='active')
        )
        
        # Calcule les différences
        added_endpoints = endpoints2 - endpoints1
        removed_endpoints = endpoints1 - endpoints2
        common_endpoints = endpoints1 & endpoints2
        
        return {
            'version1': {
                'version': v1.version,
                'name': v1.name,
                'endpoints_count': len(endpoints1),
            },
            'version2': {
                'version': v2.version,
                'name': v2.name,
                'endpoints_count': len(endpoints2),
            },
            'comparison': {
                'added_endpoints': list(added_endpoints),
                'removed_endpoints': list(removed_endpoints),
                'common_endpoints': list(common_endpoints),
                'added_count': len(added_endpoints),
                'removed_count': len(removed_endpoints),
                'common_count': len(common_endpoints),
            }
        }
    
    def deprecate_version(self, version_string, deprecation_date=None):
        """Déprécie une version de l'API"""
        version = self.get_version(version_string)
        if not version:
            return False
        
        version.status = 'deprecated'
        if deprecation_date:
            version.deprecation_date = deprecation_date
        else:
            version.deprecation_date = timezone.now()
        
        version.save()
        
        # Invalide le cache
        self._invalidate_version_cache(version_string)
        
        return True
    
    def retire_version(self, version_string, retirement_date=None):
        """Retire une version de l'API"""
        version = self.get_version(version_string)
        if not version:
            return False
        
        version.status = 'retired'
        if retirement_date:
            version.retirement_date = retirement_date
        else:
            version.retirement_date = timezone.now()
        
        version.save()
        
        # Invalide le cache
        self._invalidate_version_cache(version_string)
        
        return True
    
    def _invalidate_version_cache(self, version_string):
        """Invalide le cache pour une version"""
        cache_keys = [
            'api_current_version',
            'api_available_versions',
            f'api_version_{version_string}',
        ]
        
        for key in cache_keys:
            cache.delete(key)
    
    def get_version_statistics(self):
        """Récupère les statistiques des versions"""
        from django.db.models import Count
        
        stats = {
            'total_versions': APIVersion.objects.count(),
            'active_versions': APIVersion.objects.filter(is_active=True).count(),
            'deprecated_versions': APIVersion.objects.filter(status='deprecated').count(),
            'retired_versions': APIVersion.objects.filter(status='retired').count(),
            'versions_by_status': list(
                APIVersion.objects.values('status')
                .annotate(count=Count('id'))
                .order_by('status')
            ),
            'versions_with_endpoints': list(
                APIVersion.objects.annotate(
                    endpoints_count=Count('endpoints')
                ).values('version', 'endpoints_count')
                .order_by('-endpoints_count')
            ),
        }
        
        return stats



