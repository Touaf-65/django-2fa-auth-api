"""
Service pour le suivi de l'utilisation de l'API
"""
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Avg, Sum
from datetime import timedelta
from apps.api.models import APIUsage


class UsageService:
    """Service pour le suivi de l'utilisation de l'API"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def log_api_usage(self, api_version, endpoint, user=None, method=None, path=None,
                     query_params=None, request_headers=None, request_body=None,
                     status_code=None, response_headers=None, response_body=None,
                     response_time=None, request_size=None, response_size=None,
                     ip_address=None, user_agent=None, referer=None, error_message=None,
                     api_key=None):
        """Enregistre l'utilisation de l'API"""
        
        # Détermine le statut basé sur le code de statut
        if status_code:
            if 200 <= status_code < 300:
                status = 'success'
            elif status_code == 401:
                status = 'unauthorized'
            elif status_code == 403:
                status = 'forbidden'
            elif status_code == 404:
                status = 'not_found'
            elif status_code == 429:
                status = 'rate_limited'
            elif status_code >= 500:
                status = 'server_error'
            else:
                status = 'error'
        else:
            status = 'error'
        
        # Crée l'enregistrement d'utilisation
        usage = APIUsage.objects.create(
            api_version=api_version,
            endpoint=endpoint,
            user=user,
            method=method or endpoint.method if endpoint else 'GET',
            path=path or endpoint.path if endpoint else '',
            query_params=query_params or {},
            request_headers=request_headers or {},
            request_body=request_body or '',
            status_code=status_code or 200,
            status=status,
            response_headers=response_headers or {},
            response_body=response_body or '',
            response_time=response_time or 0,
            request_size=request_size or 0,
            response_size=response_size or 0,
            ip_address=ip_address or '127.0.0.1',
            user_agent=user_agent or '',
            referer=referer or '',
            error_message=error_message or '',
            api_key=api_key or '',
        )
        
        # Invalide le cache des statistiques
        self._invalidate_usage_cache()
        
        return usage
    
    def get_usage_statistics(self, days=7, api_version=None, endpoint=None, user=None):
        """Récupère les statistiques d'utilisation"""
        cache_key = f'api_usage_stats_{days}_{api_version.id if api_version else "all"}_{endpoint.id if endpoint else "all"}_{user.id if user else "all"}'
        stats = cache.get(cache_key)
        
        if stats is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = APIUsage.objects.filter(created_at__gte=start_date)
            
            if api_version:
                queryset = queryset.filter(api_version=api_version)
            if endpoint:
                queryset = queryset.filter(endpoint=endpoint)
            if user:
                queryset = queryset.filter(user=user)
            
            stats = {
                'total_requests': queryset.count(),
                'successful_requests': queryset.filter(status='success').count(),
                'failed_requests': queryset.exclude(status='success').count(),
                'rate_limited_requests': queryset.filter(status='rate_limited').count(),
                'unauthorized_requests': queryset.filter(status='unauthorized').count(),
                'forbidden_requests': queryset.filter(status='forbidden').count(),
                'not_found_requests': queryset.filter(status='not_found').count(),
                'server_error_requests': queryset.filter(status='server_error').count(),
                'average_response_time': queryset.aggregate(avg_time=Avg('response_time'))['avg_time'] or 0,
                'total_request_size': queryset.aggregate(total_size=Sum('request_size'))['total_size'] or 0,
                'total_response_size': queryset.aggregate(total_size=Sum('response_size'))['total_size'] or 0,
                'requests_by_status': list(
                    queryset.values('status')
                    .annotate(count=Count('id'))
                    .order_by('status')
                ),
                'requests_by_method': list(
                    queryset.values('method')
                    .annotate(count=Count('id'))
                    .order_by('method')
                ),
                'requests_by_hour': list(
                    queryset.extra(
                        select={'hour': 'EXTRACT(hour FROM created_at)'}
                    ).values('hour')
                    .annotate(count=Count('id'))
                    .order_by('hour')
                ),
                'top_endpoints': list(
                    queryset.values('endpoint__path', 'endpoint__method')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'top_users': list(
                    queryset.filter(user__isnull=False)
                    .values('user__email')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'top_ips': list(
                    queryset.values('ip_address')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def get_usage_trends(self, days=30, api_version=None):
        """Récupère les tendances d'utilisation"""
        cache_key = f'api_usage_trends_{days}_{api_version.id if api_version else "all"}'
        trends = cache.get(cache_key)
        
        if trends is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = APIUsage.objects.filter(created_at__gte=start_date)
            
            if api_version:
                queryset = queryset.filter(api_version=api_version)
            
            # Tendance par jour
            daily_trends = list(
                queryset.extra(
                    select={'date': 'DATE(created_at)'}
                ).values('date')
                .annotate(
                    total_requests=Count('id'),
                    successful_requests=Count('id', filter=Q(status='success')),
                    failed_requests=Count('id', filter=~Q(status='success')),
                    average_response_time=Avg('response_time')
                )
                .order_by('date')
            )
            
            # Tendance par heure (dernière semaine)
            weekly_end_date = timezone.now()
            weekly_start_date = weekly_end_date - timedelta(days=7)
            
            weekly_queryset = APIUsage.objects.filter(
                created_at__gte=weekly_start_date,
                created_at__lte=weekly_end_date
            )
            
            if api_version:
                weekly_queryset = weekly_queryset.filter(api_version=api_version)
            
            hourly_trends = list(
                weekly_queryset.extra(
                    select={'hour': 'EXTRACT(hour FROM created_at)'}
                ).values('hour')
                .annotate(
                    total_requests=Count('id'),
                    successful_requests=Count('id', filter=Q(status='success')),
                    failed_requests=Count('id', filter=~Q(status='success')),
                    average_response_time=Avg('response_time')
                )
                .order_by('hour')
            )
            
            trends = {
                'daily_trends': daily_trends,
                'hourly_trends': hourly_trends,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days,
                }
            }
            
            cache.set(cache_key, trends, self.cache_timeout)
        
        return trends
    
    def get_user_usage(self, user, days=30):
        """Récupère l'utilisation d'un utilisateur spécifique"""
        cache_key = f'api_user_usage_{user.id}_{days}'
        usage = cache.get(cache_key)
        
        if usage is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = APIUsage.objects.filter(
                user=user,
                created_at__gte=start_date
            )
            
            usage = {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'total_requests': queryset.count(),
                'successful_requests': queryset.filter(status='success').count(),
                'failed_requests': queryset.exclude(status='success').count(),
                'average_response_time': queryset.aggregate(avg_time=Avg('response_time'))['avg_time'] or 0,
                'total_request_size': queryset.aggregate(total_size=Sum('request_size'))['total_size'] or 0,
                'total_response_size': queryset.aggregate(total_size=Sum('response_size'))['total_size'] or 0,
                'requests_by_status': list(
                    queryset.values('status')
                    .annotate(count=Count('id'))
                    .order_by('status')
                ),
                'requests_by_endpoint': list(
                    queryset.values('endpoint__path', 'endpoint__method')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'requests_by_api_version': list(
                    queryset.values('api_version__version')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                ),
                'recent_requests': list(
                    queryset.order_by('-created_at')[:10]
                    .values(
                        'method', 'path', 'status_code', 'status',
                        'response_time', 'created_at'
                    )
                ),
            }
            
            cache.set(cache_key, usage, self.cache_timeout)
        
        return usage
    
    def get_endpoint_usage(self, endpoint, days=30):
        """Récupère l'utilisation d'un endpoint spécifique"""
        cache_key = f'api_endpoint_usage_{endpoint.id}_{days}'
        usage = cache.get(cache_key)
        
        if usage is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            queryset = APIUsage.objects.filter(
                endpoint=endpoint,
                created_at__gte=start_date
            )
            
            usage = {
                'endpoint': {
                    'id': endpoint.id,
                    'path': endpoint.path,
                    'method': endpoint.method,
                    'name': endpoint.name,
                    'api_version': endpoint.api_version.version,
                },
                'total_requests': queryset.count(),
                'successful_requests': queryset.filter(status='success').count(),
                'failed_requests': queryset.exclude(status='success').count(),
                'average_response_time': queryset.aggregate(avg_time=Avg('response_time'))['avg_time'] or 0,
                'total_request_size': queryset.aggregate(total_size=Sum('request_size'))['total_size'] or 0,
                'total_response_size': queryset.aggregate(total_size=Sum('response_size'))['total_size'] or 0,
                'requests_by_status': list(
                    queryset.values('status')
                    .annotate(count=Count('id'))
                    .order_by('status')
                ),
                'requests_by_user': list(
                    queryset.filter(user__isnull=False)
                    .values('user__email')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'requests_by_ip': list(
                    queryset.values('ip_address')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'recent_requests': list(
                    queryset.order_by('-created_at')[:10]
                    .values(
                        'user__email', 'status_code', 'status',
                        'response_time', 'ip_address', 'created_at'
                    )
                ),
            }
            
            cache.set(cache_key, usage, self.cache_timeout)
        
        return usage
    
    def _invalidate_usage_cache(self):
        """Invalide le cache des statistiques d'utilisation"""
        # Ici vous pouvez implémenter une logique pour invalider les caches spécifiques
        # Par exemple, en utilisant des patterns de clés
        pass

