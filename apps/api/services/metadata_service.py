"""
Service pour la gestion des métadonnées de l'API
"""
from django.utils import timezone
from django.core.cache import cache
from apps.api.models import APIMetadata, APIDocumentation, APISDK


class MetadataService:
    """Service pour la gestion des métadonnées de l'API"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_metadata(self, api_version, metadata_type=None):
        """Récupère les métadonnées pour une version d'API"""
        cache_key = f'api_metadata_{api_version.version}_{metadata_type or "all"}'
        metadata = cache.get(cache_key)
        
        if metadata is None:
            queryset = APIMetadata.objects.filter(
                api_version=api_version,
                is_public=True
            )
            
            if metadata_type:
                queryset = queryset.filter(metadata_type=metadata_type)
            
            metadata = queryset.order_by('display_order')
            cache.set(cache_key, list(metadata), self.cache_timeout)
        
        return metadata
    
    def get_metadata_dict(self, api_version):
        """Récupère les métadonnées sous forme de dictionnaire"""
        metadata = self.get_metadata(api_version)
        
        result = {}
        for item in metadata:
            if item.metadata_type not in result:
                result[item.metadata_type] = {}
            result[item.metadata_type][item.key] = item.value
        
        return result
    
    def set_metadata(self, api_version, metadata_type, key, value, is_public=True, is_required=False):
        """Définit une métadonnée"""
        metadata, created = APIMetadata.objects.get_or_create(
            api_version=api_version,
            metadata_type=metadata_type,
            key=key,
            defaults={
                'value': value,
                'is_public': is_public,
                'is_required': is_required,
            }
        )
        
        if not created:
            metadata.value = value
            metadata.is_public = is_public
            metadata.is_required = is_required
            metadata.save()
        
        # Invalide le cache
        self._invalidate_metadata_cache(api_version.version, metadata_type)
        
        return metadata
    
    def get_documentation(self, api_version, doc_type=None):
        """Récupère la documentation pour une version d'API"""
        cache_key = f'api_documentation_{api_version.version}_{doc_type or "all"}'
        documentation = cache.get(cache_key)
        
        if documentation is None:
            queryset = APIDocumentation.objects.filter(
                api_version=api_version,
                is_public=True
            )
            
            if doc_type:
                queryset = queryset.filter(doc_type=doc_type)
            
            documentation = queryset.order_by('display_order')
            cache.set(cache_key, list(documentation), self.cache_timeout)
        
        return documentation
    
    def get_featured_documentation(self, api_version):
        """Récupère la documentation mise en avant"""
        return APIDocumentation.objects.filter(
            api_version=api_version,
            is_public=True,
            is_featured=True
        ).order_by('display_order')
    
    def get_sdks(self, api_version, language=None):
        """Récupère les SDKs pour une version d'API"""
        cache_key = f'api_sdks_{api_version.version}_{language or "all"}'
        sdks = cache.get(cache_key)
        
        if sdks is None:
            queryset = APISDK.objects.filter(
                api_version=api_version,
                is_active=True
            )
            
            if language:
                queryset = queryset.filter(language=language)
            
            sdks = queryset.order_by('language', 'version')
            cache.set(cache_key, list(sdks), self.cache_timeout)
        
        return sdks
    
    def get_sdk_by_language(self, api_version, language):
        """Récupère le SDK pour un langage spécifique"""
        try:
            return APISDK.objects.get(
                api_version=api_version,
                language=language,
                is_active=True
            )
        except APISDK.DoesNotExist:
            return None
    
    def get_api_info(self, api_version):
        """Récupère les informations complètes de l'API"""
        return {
            'version': api_version.version,
            'name': api_version.name,
            'description': api_version.description,
            'status': api_version.status,
            'release_date': api_version.release_date.isoformat() if api_version.release_date else None,
            'deprecation_date': api_version.deprecation_date.isoformat() if api_version.deprecation_date else None,
            'retirement_date': api_version.retirement_date.isoformat() if api_version.retirement_date else None,
            'is_default': api_version.is_default,
            'is_public': api_version.is_public,
            'changelog': api_version.changelog,
            'metadata': self.get_metadata_dict(api_version),
            'documentation': [
                {
                    'type': doc.doc_type,
                    'title': doc.title,
                    'summary': doc.summary,
                    'is_featured': doc.is_featured,
                }
                for doc in self.get_documentation(api_version)
            ],
            'sdks': [
                {
                    'language': sdk.language,
                    'name': sdk.name,
                    'version': sdk.version,
                    'download_url': sdk.download_url,
                    'repository_url': sdk.repository_url,
                    'documentation_url': sdk.documentation_url,
                }
                for sdk in self.get_sdks(api_version)
            ],
            'tags': api_version.tags,
        }
    
    def _invalidate_metadata_cache(self, version, metadata_type=None):
        """Invalide le cache des métadonnées"""
        cache_keys = [
            f'api_metadata_{version}_all',
            f'api_metadata_{version}_{metadata_type}',
        ]
        
        for key in cache_keys:
            cache.delete(key)
    
    def get_metadata_statistics(self):
        """Récupère les statistiques des métadonnées"""
        from django.db.models import Count
        
        stats = {
            'total_metadata': APIMetadata.objects.count(),
            'public_metadata': APIMetadata.objects.filter(is_public=True).count(),
            'required_metadata': APIMetadata.objects.filter(is_required=True).count(),
            'metadata_by_type': list(
                APIMetadata.objects.values('metadata_type')
                .annotate(count=Count('id'))
                .order_by('metadata_type')
            ),
            'total_documentation': APIDocumentation.objects.count(),
            'public_documentation': APIDocumentation.objects.filter(is_public=True).count(),
            'featured_documentation': APIDocumentation.objects.filter(is_featured=True).count(),
            'documentation_by_type': list(
                APIDocumentation.objects.values('doc_type')
                .annotate(count=Count('id'))
                .order_by('doc_type')
            ),
            'total_sdks': APISDK.objects.count(),
            'active_sdks': APISDK.objects.filter(is_active=True).count(),
            'sdks_by_language': list(
                APISDK.objects.filter(is_active=True)
                .values('language')
                .annotate(count=Count('id'))
                .order_by('language')
            ),
        }
        
        return stats

