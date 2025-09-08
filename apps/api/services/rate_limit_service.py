"""
Service pour la gestion des limites de taux d'API
"""
import time
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from apps.api.models import APIRateLimit, APIRateLimitUsage


class RateLimitService:
    """Service pour la gestion des limites de taux d'API"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 heure
    
    def check_rate_limit(self, user=None, ip=None, endpoint=None, api_key=None):
        """Vérifie si une requête respecte les limites de taux"""
        # Récupère les limites applicables
        applicable_limits = self._get_applicable_limits(user, ip, endpoint, api_key)
        
        if not applicable_limits:
            return {'allowed': True, 'reason': 'no_limits'}
        
        # Vérifie chaque limite
        for limit in applicable_limits:
            result = self._check_single_limit(limit, user, ip, endpoint, api_key)
            if not result['allowed']:
                return result
        
        return {'allowed': True, 'reason': 'within_limits'}
    
    def _get_applicable_limits(self, user=None, ip=None, endpoint=None, api_key=None):
        """Récupère les limites applicables à la requête"""
        cache_key = f'rate_limits_{user.id if user else "anon"}_{ip}_{endpoint.id if endpoint else "none"}_{api_key}'
        limits = cache.get(cache_key)
        
        if limits is None:
            limits = APIRateLimit.objects.filter(is_active=True).order_by('scope')
            cache.set(cache_key, list(limits), self.cache_timeout)
        
        # Filtre les limites applicables
        applicable_limits = []
        for limit in limits:
            if limit.is_applicable_to(user, ip, endpoint, api_key):
                applicable_limits.append(limit)
        
        return applicable_limits
    
    def _check_single_limit(self, limit, user=None, ip=None, endpoint=None, api_key=None):
        """Vérifie une limite spécifique"""
        now = timezone.now()
        window_start = now.replace(second=0, microsecond=0)
        
        # Récupère ou crée l'utilisation de la limite
        usage, created = APIRateLimitUsage.objects.get_or_create(
            rate_limit=limit,
            user=user,
            ip_address=ip or '127.0.0.1',
            endpoint=endpoint,
            api_key=api_key or '',
            window_start=window_start,
            defaults={
                'requests_count': 0,
                'window_end': window_start + timezone.timedelta(minutes=1),
            }
        )
        
        # Vérifie si la limite est dépassée
        if usage.requests_count >= limit.requests_per_minute:
            if not usage.is_limited:
                usage.is_limited = True
                usage.limit_reached_at = now
                usage.save()
            
            return {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'limit': limit.name,
                'current_requests': usage.requests_count,
                'max_requests': limit.requests_per_minute,
                'reset_time': usage.window_end.isoformat(),
            }
        
        # Incrémente le compteur
        usage.requests_count += 1
        usage.save()
        
        return {
            'allowed': True,
            'reason': 'within_limit',
            'limit': limit.name,
            'current_requests': usage.requests_count,
            'max_requests': limit.requests_per_minute,
            'remaining_requests': limit.requests_per_minute - usage.requests_count,
        }
    
    def get_rate_limit_status(self, user=None, ip=None, endpoint=None, api_key=None):
        """Récupère le statut des limites de taux"""
        applicable_limits = self._get_applicable_limits(user, ip, endpoint, api_key)
        
        status = {
            'limits': [],
            'overall_status': 'ok',
            'total_remaining': float('inf'),
        }
        
        for limit in applicable_limits:
            now = timezone.now()
            window_start = now.replace(second=0, microsecond=0)
            
            try:
                usage = APIRateLimitUsage.objects.get(
                    rate_limit=limit,
                    user=user,
                    ip_address=ip or '127.0.0.1',
                    endpoint=endpoint,
                    api_key=api_key or '',
                    window_start=window_start,
                )
                
                remaining = max(0, limit.requests_per_minute - usage.requests_count)
                limit_status = {
                    'name': limit.name,
                    'scope': limit.scope,
                    'current_requests': usage.requests_count,
                    'max_requests': limit.requests_per_minute,
                    'remaining_requests': remaining,
                    'reset_time': usage.window_end.isoformat(),
                    'is_limited': usage.is_limited,
                }
                
                if remaining < status['total_remaining']:
                    status['total_remaining'] = remaining
                
                if usage.is_limited:
                    status['overall_status'] = 'limited'
                
            except APIRateLimitUsage.DoesNotExist:
                limit_status = {
                    'name': limit.name,
                    'scope': limit.scope,
                    'current_requests': 0,
                    'max_requests': limit.requests_per_minute,
                    'remaining_requests': limit.requests_per_minute,
                    'reset_time': (window_start + timezone.timedelta(minutes=1)).isoformat(),
                    'is_limited': False,
                }
                
                if limit.requests_per_minute < status['total_remaining']:
                    status['total_remaining'] = limit.requests_per_minute
            
            status['limits'].append(limit_status)
        
        if status['total_remaining'] == float('inf'):
            status['total_remaining'] = None
        
        return status
    
    def reset_rate_limit(self, user=None, ip=None, endpoint=None, api_key=None, limit_name=None):
        """Remet à zéro les limites de taux"""
        if limit_name:
            # Remet à zéro une limite spécifique
            try:
                limit = APIRateLimit.objects.get(name=limit_name, is_active=True)
                APIRateLimitUsage.objects.filter(
                    rate_limit=limit,
                    user=user,
                    ip_address=ip or '127.0.0.1',
                    endpoint=endpoint,
                    api_key=api_key or '',
                ).delete()
                return True
            except APIRateLimit.DoesNotExist:
                return False
        else:
            # Remet à zéro toutes les limites applicables
            applicable_limits = self._get_applicable_limits(user, ip, endpoint, api_key)
            
            for limit in applicable_limits:
                APIRateLimitUsage.objects.filter(
                    rate_limit=limit,
                    user=user,
                    ip_address=ip or '127.0.0.1',
                    endpoint=endpoint,
                    api_key=api_key or '',
                ).delete()
            
            return True
    
    def get_rate_limit_statistics(self, days=7):
        """Récupère les statistiques des limites de taux"""
        from django.db.models import Count, Sum
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            'total_limits': APIRateLimit.objects.filter(is_active=True).count(),
            'total_usage_records': APIRateLimitUsage.objects.filter(
                window_start__gte=start_date
            ).count(),
            'limited_requests': APIRateLimitUsage.objects.filter(
                window_start__gte=start_date,
                is_limited=True
            ).count(),
            'limits_by_scope': list(
                APIRateLimit.objects.filter(is_active=True)
                .values('scope')
                .annotate(count=Count('id'))
                .order_by('scope')
            ),
            'usage_by_limit': list(
                APIRateLimitUsage.objects.filter(
                    window_start__gte=start_date
                ).values('rate_limit__name')
                .annotate(
                    total_requests=Sum('requests_count'),
                    limited_count=Count('id', filter=Q(is_limited=True))
                )
                .order_by('-total_requests')
            ),
        }
        
        return stats

