"""
Filtres avancés pour l'API
"""
from django_filters import rest_framework as filters
from django_filters import CharFilter, NumberFilter, DateFilter, DateTimeFilter, ChoiceFilter
from django.db.models import Q
from core.filters import BaseFilterSet


class APIVersionFilter(BaseFilterSet):
    """Filtres pour les versions d'API"""
    
    version = CharFilter(field_name='version', lookup_expr='icontains')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    status = ChoiceFilter(field_name='status', choices=[
        ('development', 'Développement'),
        ('beta', 'Bêta'),
        ('stable', 'Stable'),
        ('deprecated', 'Déprécié'),
        ('retired', 'Retiré'),
    ])
    is_default = filters.BooleanFilter(field_name='is_default')
    is_public = filters.BooleanFilter(field_name='is_public')
    release_date_from = DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_to = DateFilter(field_name='release_date', lookup_expr='lte')
    
    class Meta:
        fields = ['version', 'name', 'status', 'is_default', 'is_public', 'release_date_from', 'release_date_to']


class APIEndpointFilter(BaseFilterSet):
    """Filtres pour les endpoints d'API"""
    
    path = CharFilter(field_name='path', lookup_expr='icontains')
    method = ChoiceFilter(field_name='method', choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ])
    name = CharFilter(field_name='name', lookup_expr='icontains')
    status = ChoiceFilter(field_name='status', choices=[
        ('active', 'Actif'),
        ('deprecated', 'Déprécié'),
        ('retired', 'Retiré'),
        ('maintenance', 'Maintenance'),
    ])
    is_public = filters.BooleanFilter(field_name='is_public')
    requires_auth = filters.BooleanFilter(field_name='requires_auth')
    api_version = CharFilter(field_name='api_version__version')
    
    class Meta:
        fields = ['path', 'method', 'name', 'status', 'is_public', 'requires_auth', 'api_version']


class APIUsageFilter(BaseFilterSet):
    """Filtres pour l'utilisation de l'API"""
    
    method = CharFilter(field_name='method')
    path = CharFilter(field_name='path', lookup_expr='icontains')
    status = ChoiceFilter(field_name='status', choices=[
        ('success', 'Succès'),
        ('error', 'Erreur'),
        ('rate_limited', 'Limité par le taux'),
        ('unauthorized', 'Non autorisé'),
        ('forbidden', 'Interdit'),
        ('not_found', 'Non trouvé'),
        ('server_error', 'Erreur serveur'),
    ])
    status_code = NumberFilter(field_name='status_code')
    status_code_min = NumberFilter(field_name='status_code', lookup_expr='gte')
    status_code_max = NumberFilter(field_name='status_code', lookup_expr='lte')
    response_time_min = NumberFilter(field_name='response_time', lookup_expr='gte')
    response_time_max = NumberFilter(field_name='response_time', lookup_expr='lte')
    ip_address = CharFilter(field_name='ip_address')
    api_version = CharFilter(field_name='api_version__version')
    user = NumberFilter(field_name='user__id')
    created_at_from = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        fields = [
            'method', 'path', 'status', 'status_code', 'status_code_min', 'status_code_max',
            'response_time_min', 'response_time_max', 'ip_address', 'api_version', 'user',
            'created_at_from', 'created_at_to'
        ]


class APIRateLimitFilter(BaseFilterSet):
    """Filtres pour les limites de taux d'API"""
    
    name = CharFilter(field_name='name', lookup_expr='icontains')
    scope = ChoiceFilter(field_name='scope', choices=[
        ('global', 'Global'),
        ('user', 'Utilisateur'),
        ('ip', 'Adresse IP'),
        ('endpoint', 'Endpoint'),
        ('api_key', 'Clé API'),
    ])
    is_active = filters.BooleanFilter(field_name='is_active')
    requests_per_minute_min = NumberFilter(field_name='requests_per_minute', lookup_expr='gte')
    requests_per_minute_max = NumberFilter(field_name='requests_per_minute', lookup_expr='lte')
    
    class Meta:
        fields = ['name', 'scope', 'is_active', 'requests_per_minute_min', 'requests_per_minute_max']


class APIMetadataFilter(BaseFilterSet):
    """Filtres pour les métadonnées d'API"""
    
    metadata_type = ChoiceFilter(field_name='metadata_type', choices=[
        ('info', 'Informations générales'),
        ('contact', 'Contact'),
        ('license', 'Licence'),
        ('terms', 'Conditions d\'utilisation'),
        ('privacy', 'Politique de confidentialité'),
        ('changelog', 'Changelog'),
        ('deprecation', 'Avertissement de dépréciation'),
        ('maintenance', 'Maintenance'),
        ('custom', 'Personnalisé'),
    ])
    key = CharFilter(field_name='key', lookup_expr='icontains')
    is_public = filters.BooleanFilter(field_name='is_public')
    is_required = filters.BooleanFilter(field_name='is_required')
    api_version = CharFilter(field_name='api_version__version')
    
    class Meta:
        fields = ['metadata_type', 'key', 'is_public', 'is_required', 'api_version']


class APIHealthCheckFilter(BaseFilterSet):
    """Filtres pour les health checks d'API"""
    
    name = CharFilter(field_name='name', lookup_expr='icontains')
    check_type = ChoiceFilter(field_name='check_type', choices=[
        ('database', 'Base de données'),
        ('cache', 'Cache'),
        ('external_api', 'API externe'),
        ('storage', 'Stockage'),
        ('queue', 'File d\'attente'),
        ('custom', 'Personnalisé'),
    ])
    is_active = filters.BooleanFilter(field_name='is_active')
    expected_status_code = NumberFilter(field_name='expected_status_code')
    
    class Meta:
        fields = ['name', 'check_type', 'is_active', 'expected_status_code']


class APIDocumentationFilter(BaseFilterSet):
    """Filtres pour la documentation d'API"""
    
    doc_type = ChoiceFilter(field_name='doc_type', choices=[
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
    ])
    title = CharFilter(field_name='title', lookup_expr='icontains')
    is_public = filters.BooleanFilter(field_name='is_public')
    is_featured = filters.BooleanFilter(field_name='is_featured')
    api_version = CharFilter(field_name='api_version__version')
    
    class Meta:
        fields = ['doc_type', 'title', 'is_public', 'is_featured', 'api_version']


class APISDKFilter(BaseFilterSet):
    """Filtres pour les SDKs d'API"""
    
    language = ChoiceFilter(field_name='language', choices=[
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
    ])
    name = CharFilter(field_name='name', lookup_expr='icontains')
    version = CharFilter(field_name='version', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    api_version = CharFilter(field_name='api_version__version')
    
    class Meta:
        fields = ['language', 'name', 'version', 'is_active', 'api_version']


class APISearchFilter:
    """Filtre de recherche avancé"""
    
    @staticmethod
    def search_versions(queryset, search_term):
        """Recherche dans les versions d'API"""
        return queryset.filter(
            Q(version__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    @staticmethod
    def search_endpoints(queryset, search_term):
        """Recherche dans les endpoints d'API"""
        return queryset.filter(
            Q(path__icontains=search_term) |
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(method__icontains=search_term)
        )
    
    @staticmethod
    def search_usage(queryset, search_term):
        """Recherche dans l'utilisation de l'API"""
        return queryset.filter(
            Q(path__icontains=search_term) |
            Q(method__icontains=search_term) |
            Q(ip_address__icontains=search_term) |
            Q(user_agent__icontains=search_term) |
            Q(error_message__icontains=search_term)
        )
    
    @staticmethod
    def search_documentation(queryset, search_term):
        """Recherche dans la documentation d'API"""
        return queryset.filter(
            Q(title__icontains=search_term) |
            Q(content__icontains=search_term) |
            Q(summary__icontains=search_term)
        )



