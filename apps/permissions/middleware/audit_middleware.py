"""
Middleware pour l'audit des permissions
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
from apps.security.models import SecurityEvent
from ..utils import get_user_permissions, get_user_roles

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware pour l'audit des accès et des permissions
    """
    
    def process_request(self, request):
        """
        Enregistre les informations de la requête pour l'audit
        """
        # Ignorer les requêtes non authentifiées
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Enregistrer les informations de base
        request.audit_info = {
            'timestamp': timezone.now(),
            'user_id': request.user.id,
            'user_email': request.user.email,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
        }
        
        # Ajouter les permissions de l'utilisateur
        try:
            user_permissions = get_user_permissions(request.user)
            request.audit_info['user_permissions'] = list(user_permissions.values_list('codename', flat=True))
            
            user_roles = get_user_roles(request.user)
            request.audit_info['user_roles'] = list(user_roles.values_list('name', flat=True))
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des permissions pour l'audit: {str(e)}")
            request.audit_info['user_permissions'] = []
            request.audit_info['user_roles'] = []
        
        return None
    
    def process_response(self, request, response):
        """
        Enregistre les informations de la réponse pour l'audit
        """
        if not hasattr(request, 'audit_info'):
            return response
        
        # Compléter les informations d'audit
        audit_info = request.audit_info.copy()
        audit_info.update({
            'response_status': response.status_code,
            'response_time': (timezone.now() - audit_info['timestamp']).total_seconds(),
            'content_type': response.get('Content-Type', ''),
        })
        
        # Ajouter les informations de permission si disponibles
        if hasattr(request, 'permission_checked'):
            audit_info['permission_checked'] = True
            audit_info['permission_required'] = getattr(request, 'permission_required', None)
            audit_info['permission_granted'] = getattr(request, 'permission_granted', False)
        
        # Ajouter les informations de délégation si disponibles
        if hasattr(request, 'delegation_used'):
            audit_info['delegation_used'] = True
            audit_info['delegation_info'] = getattr(request, 'delegation_info', {})
        
        # Déterminer le niveau de log
        log_level = self._determine_log_level(audit_info)
        
        # Enregistrer l'audit
        self._log_audit_event(audit_info, log_level)
        
        # Créer un événement de sécurité si nécessaire
        if self._should_create_security_event(audit_info):
            self._create_security_event(audit_info)
        
        return response
    
    def _get_client_ip(self, request):
        """
        Récupère l'IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    def _determine_log_level(self, audit_info):
        """
        Détermine le niveau de log basé sur les informations d'audit
        """
        # Erreurs 4xx et 5xx
        if audit_info['response_status'] >= 400:
            return 'WARNING'
        
        # Accès avec délégation
        if audit_info.get('delegation_used'):
            return 'INFO'
        
        # Accès avec permissions spéciales
        if audit_info.get('permission_checked'):
            return 'INFO'
        
        # Accès normal
        return 'DEBUG'
    
    def _should_create_security_event(self, audit_info):
        """
        Détermine si un événement de sécurité doit être créé
        """
        # Erreurs d'autorisation
        if audit_info['response_status'] == 403:
            return True
        
        # Utilisation de délégation
        if audit_info.get('delegation_used'):
            return True
        
        # Accès à des endpoints sensibles
        sensitive_paths = ['/admin/', '/api/auth/', '/api/security/']
        if any(audit_info['path'].startswith(path) for path in sensitive_paths):
            return True
        
        return False
    
    def _log_audit_event(self, audit_info, log_level):
        """
        Enregistre l'événement d'audit dans les logs
        """
        log_message = self._format_audit_message(audit_info)
        
        if log_level == 'DEBUG':
            logger.debug(log_message)
        elif log_level == 'INFO':
            logger.info(log_message)
        elif log_level == 'WARNING':
            logger.warning(log_message)
        elif log_level == 'ERROR':
            logger.error(log_message)
    
    def _format_audit_message(self, audit_info):
        """
        Formate le message d'audit
        """
        message_parts = [
            f"USER:{audit_info['user_email']}",
            f"IP:{audit_info['ip_address']}",
            f"METHOD:{audit_info['method']}",
            f"PATH:{audit_info['path']}",
            f"STATUS:{audit_info['response_status']}",
            f"TIME:{audit_info['response_time']:.3f}s"
        ]
        
        if audit_info.get('permission_checked'):
            message_parts.append(f"PERM:{audit_info.get('permission_required', 'N/A')}")
            message_parts.append(f"GRANTED:{audit_info.get('permission_granted', False)}")
        
        if audit_info.get('delegation_used'):
            delegation_info = audit_info.get('delegation_info', {})
            message_parts.append(f"DELEGATION:{delegation_info.get('type', 'unknown')}")
            message_parts.append(f"DELEGATOR:{delegation_info.get('delegator', 'unknown')}")
        
        return " | ".join(message_parts)
    
    def _create_security_event(self, audit_info):
        """
        Crée un événement de sécurité
        """
        try:
            # Déterminer le type d'événement
            if audit_info['response_status'] == 403:
                event_type = SecurityEvent.SUSPICIOUS_ACTIVITY
                title = 'Accès refusé'
                description = f'Accès refusé à {audit_info["path"]}'
                severity = SecurityEvent.MEDIUM
            elif audit_info.get('delegation_used'):
                event_type = SecurityEvent.SUSPICIOUS_ACTIVITY
                title = 'Utilisation de délégation'
                description = f'Utilisation d\'une délégation pour accéder à {audit_info["path"]}'
                severity = SecurityEvent.LOW
            else:
                event_type = SecurityEvent.LOGIN_SUCCESS
                title = 'Accès autorisé'
                description = f'Accès autorisé à {audit_info["path"]}'
                severity = SecurityEvent.LOW
            
            # Créer l'événement
            SecurityEvent.create_event(
                event_type=event_type,
                title=title,
                description=description,
                ip_address=audit_info['ip_address'],
                user_id=audit_info['user_id'],
                severity=severity,
                user_agent=audit_info['user_agent'],
                metadata={
                    'audit_info': audit_info,
                    'timestamp': audit_info['timestamp'].isoformat(),
                    'response_time': audit_info['response_time'],
                    'query_params': audit_info['query_params'],
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement de sécurité: {str(e)}")


def audit_access(view_func):
    """
    Décorateur pour marquer une vue comme nécessitant un audit détaillé
    """
    view_func.audit_required = True
    return view_func


def audit_sensitive(view_func):
    """
    Décorateur pour marquer une vue comme sensible nécessitant un audit complet
    """
    view_func.audit_sensitive = True
    return view_func
