"""
Middleware pour la limitation de taux
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware pour limiter le taux de requêtes
    """
    
    def process_request(self, request):
        """
        Vérifie le taux de requêtes
        """
        # Récupérer l'IP du client
        ip_address = getattr(request, 'client_ip', self._get_client_ip(request))
        
        # Vérifier le rate limiting
        if self._is_rate_limited(ip_address, request):
            logger.warning(f"Rate limit dépassé pour IP: {ip_address}")
            return JsonResponse({
                'error': 'Trop de requêtes',
                'message': 'Vous avez dépassé la limite de requêtes. Veuillez patienter avant de réessayer.',
                'retry_after': 60
            }, status=429)
        
        return None
    
    def _get_client_ip(self, request):
        """
        Récupère l'IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_rate_limited(self, ip_address, request):
        """
        Vérifie si l'IP est rate limitée
        """
        # Configuration du rate limiting
        rate_limit_config = getattr(settings, 'RATE_LIMIT_CONFIG', {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
        })
        
        # Vérifier les limites par minute
        minute_key = f"rate_limit:minute:{ip_address}:{int(time.time() // 60)}"
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= rate_limit_config['requests_per_minute']:
            return True
        
        # Vérifier les limites par heure
        hour_key = f"rate_limit:hour:{ip_address}:{int(time.time() // 3600)}"
        hour_count = cache.get(hour_key, 0)
        
        if hour_count >= rate_limit_config['requests_per_hour']:
            return True
        
        # Vérifier les limites par jour
        day_key = f"rate_limit:day:{ip_address}:{int(time.time() // 86400)}"
        day_count = cache.get(day_key, 0)
        
        if day_count >= rate_limit_config['requests_per_day']:
            return True
        
        # Incrémenter les compteurs
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        cache.set(day_key, day_count + 1, 86400)
        
        return False
    
    def _get_rate_limit_headers(self, ip_address):
        """
        Retourne les headers de rate limiting
        """
        headers = {}
        
        # Compteurs actuels
        current_minute = int(time.time() // 60)
        current_hour = int(time.time() // 3600)
        current_day = int(time.time() // 86400)
        
        minute_key = f"rate_limit:minute:{ip_address}:{current_minute}"
        hour_key = f"rate_limit:hour:{ip_address}:{current_hour}"
        day_key = f"rate_limit:day:{ip_address}:{current_day}"
        
        minute_count = cache.get(minute_key, 0)
        hour_count = cache.get(hour_key, 0)
        day_count = cache.get(day_key, 0)
        
        rate_limit_config = getattr(settings, 'RATE_LIMIT_CONFIG', {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
        })
        
        headers['X-RateLimit-Limit-Minute'] = rate_limit_config['requests_per_minute']
        headers['X-RateLimit-Remaining-Minute'] = max(0, rate_limit_config['requests_per_minute'] - minute_count)
        headers['X-RateLimit-Reset-Minute'] = (current_minute + 1) * 60
        
        headers['X-RateLimit-Limit-Hour'] = rate_limit_config['requests_per_hour']
        headers['X-RateLimit-Remaining-Hour'] = max(0, rate_limit_config['requests_per_hour'] - hour_count)
        headers['X-RateLimit-Reset-Hour'] = (current_hour + 1) * 3600
        
        headers['X-RateLimit-Limit-Day'] = rate_limit_config['requests_per_day']
        headers['X-RateLimit-Remaining-Day'] = max(0, rate_limit_config['requests_per_day'] - day_count)
        headers['X-RateLimit-Reset-Day'] = (current_day + 1) * 86400
        
        return headers
    
    def process_response(self, request, response):
        """
        Ajoute les headers de rate limiting à la réponse
        """
        if hasattr(request, 'client_ip'):
            headers = self._get_rate_limit_headers(request.client_ip)
            for key, value in headers.items():
                response[key] = str(value)
        
        return response
