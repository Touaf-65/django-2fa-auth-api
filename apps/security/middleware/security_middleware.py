"""
Middleware principal de sécurité
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from ..models import SecurityEvent, IPBlock, UserSecurity
from ..utils.security_utils import get_client_ip, get_geolocation

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware principal pour la sécurité
    """
    
    def process_request(self, request):
        """
        Traite chaque requête entrante
        """
        # Récupérer l'IP du client
        ip_address = get_client_ip(request)
        
        # Vérifier si l'IP est bloquée
        if IPBlock.is_ip_blocked(ip_address):
            logger.warning(f"Requête bloquée - IP: {ip_address}")
            return JsonResponse({
                'error': 'Accès refusé',
                'message': 'Votre adresse IP a été bloquée pour des raisons de sécurité.'
            }, status=403)
        
        # Ajouter l'IP à la requête pour utilisation ultérieure
        request.client_ip = ip_address
        
        # Récupérer les informations de géolocalisation
        geolocation = get_geolocation(ip_address)
        if geolocation:
            request.client_country = geolocation.get('country', '')
            request.client_city = geolocation.get('city', '')
        else:
            request.client_country = ''
            request.client_city = ''
        
        return None
    
    def process_response(self, request, response):
        """
        Traite chaque réponse sortante
        """
        # Enregistrer les événements de sécurité si nécessaire
        if hasattr(request, 'security_event'):
            self._log_security_event(request, response)
        
        return response
    
    def _log_security_event(self, request, response):
        """
        Enregistre un événement de sécurité
        """
        try:
            event_data = request.security_event
            
            SecurityEvent.create_event(
                event_type=event_data.get('event_type'),
                title=event_data.get('title'),
                description=event_data.get('description'),
                ip_address=request.client_ip,
                user=event_data.get('user'),
                severity=event_data.get('severity', 'medium'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                country=request.client_country,
                city=request.client_city,
                metadata=event_data.get('metadata', {})
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'événement de sécurité: {str(e)}")
    
    def _check_suspicious_activity(self, request):
        """
        Détecte les activités suspectes
        """
        suspicious_indicators = []
        
        # Vérifier les headers suspects
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or len(user_agent) < 10:
            suspicious_indicators.append('User-Agent manquant ou suspect')
        
        # Vérifier les tentatives de SQL injection
        query_params = request.GET.dict()
        for key, value in query_params.items():
            if any(keyword in value.lower() for keyword in ['union', 'select', 'drop', 'delete', 'insert']):
                suspicious_indicators.append(f'Possible injection SQL dans le paramètre {key}')
        
        # Vérifier les tentatives de XSS
        for key, value in query_params.items():
            if any(tag in value.lower() for tag in ['<script>', '<iframe>', 'javascript:']):
                suspicious_indicators.append(f'Possible XSS dans le paramètre {key}')
        
        return suspicious_indicators
