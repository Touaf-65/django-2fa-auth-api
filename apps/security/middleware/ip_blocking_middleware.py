"""
Middleware pour le blocage d'IP
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from ..models import IPBlock, LoginAttempt

logger = logging.getLogger(__name__)


class IPBlockingMiddleware(MiddlewareMixin):
    """
    Middleware pour gérer le blocage automatique d'IP
    """
    
    def process_request(self, request):
        """
        Vérifie si l'IP est bloquée
        """
        # Récupérer l'IP du client
        ip_address = getattr(request, 'client_ip', self._get_client_ip(request))
        
        # Vérifier si l'IP est bloquée
        if IPBlock.is_ip_blocked(ip_address):
            logger.warning(f"Requête bloquée - IP: {ip_address}")
            return JsonResponse({
                'error': 'Accès refusé',
                'message': 'Votre adresse IP a été bloquée pour des raisons de sécurité.',
                'code': 'IP_BLOCKED'
            }, status=403)
        
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
    
    def _check_auto_block_conditions(self, request):
        """
        Vérifie les conditions pour un blocage automatique
        """
        ip_address = getattr(request, 'client_ip', self._get_client_ip(request))
        
        # Vérifier les tentatives de connexion échouées
        failed_attempts = LoginAttempt.get_failed_attempts_count(ip_address, minutes=15)
        
        if failed_attempts >= 5:  # Configurable
            return {
                'should_block': True,
                'reason': f'Trop de tentatives de connexion échouées ({failed_attempts})',
                'duration_minutes': 60  # Blocage d'1 heure
            }
        
        return {'should_block': False}
    
    def process_response(self, request, response):
        """
        Traite la réponse et vérifie les conditions de blocage automatique
        """
        # Vérifier les conditions de blocage automatique
        if response.status_code == 401 or response.status_code == 403:
            block_conditions = self._check_auto_block_conditions(request)
            
            if block_conditions['should_block']:
                ip_address = getattr(request, 'client_ip', self._get_client_ip(request))
                
                # Bloquer l'IP automatiquement
                IPBlock.block_ip(
                    ip_address=ip_address,
                    reason=block_conditions['reason'],
                    block_type='automatic',
                    duration_minutes=block_conditions.get('duration_minutes', 60)
                )
                
                logger.warning(f"IP {ip_address} bloquée automatiquement: {block_conditions['reason']}")
        
        return response
