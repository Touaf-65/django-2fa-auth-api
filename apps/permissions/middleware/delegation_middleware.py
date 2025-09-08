"""
Middleware pour la gestion des délégations de permissions
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
from ..models import PermissionDelegation, RoleDelegation
from ..utils import has_delegated_permission

logger = logging.getLogger(__name__)


class DelegationMiddleware(MiddlewareMixin):
    """
    Middleware pour gérer les délégations de permissions
    """
    
    def process_request(self, request):
        """
        Traite chaque requête pour vérifier les délégations
        """
        # Ignorer les requêtes non authentifiées
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Ignorer les superutilisateurs
        if request.user.is_superuser:
            return None
        
        # Vérifier si une délégation est utilisée
        delegation_header = request.META.get('HTTP_X_USE_DELEGATION')
        if delegation_header:
            return self._handle_delegation_request(request, delegation_header)
        
        return None
    
    def process_response(self, request, response):
        """
        Traite la réponse pour ajouter des informations de délégation
        """
        if hasattr(request, 'delegation_used'):
            response['X-Delegation-Used'] = 'true'
            response['X-Delegation-Source'] = request.delegation_source
            response['X-Delegation-Remaining-Uses'] = str(request.delegation_remaining_uses)
            response['X-Delegation-Expires'] = request.delegation_expires.isoformat()
        
        return response
    
    def _handle_delegation_request(self, request, delegation_header):
        """
        Gère une requête utilisant une délégation
        """
        try:
            # Parser le header de délégation
            # Format: "permission:codename" ou "role:rolename"
            delegation_type, delegation_target = delegation_header.split(':', 1)
            
            if delegation_type == 'permission':
                return self._handle_permission_delegation(request, delegation_target)
            elif delegation_type == 'role':
                return self._handle_role_delegation(request, delegation_target)
            else:
                return JsonResponse({
                    'error': 'Type de délégation invalide',
                    'message': 'Le type de délégation doit être "permission" ou "role"',
                    'code': 'INVALID_DELEGATION_TYPE'
                }, status=400)
        
        except ValueError:
            return JsonResponse({
                'error': 'Format de délégation invalide',
                'message': 'Format attendu: "permission:codename" ou "role:rolename"',
                'code': 'INVALID_DELEGATION_FORMAT'
            }, status=400)
    
    def _handle_permission_delegation(self, request, permission_codename):
        """
        Gère une délégation de permission
        """
        # Vérifier si l'utilisateur a une délégation active pour cette permission
        delegations = PermissionDelegation.get_active_delegations(
            request.user, 
            permission_codename
        )
        
        if not delegations:
            return JsonResponse({
                'error': 'Délégation non trouvée',
                'message': f'Aucune délégation active trouvée pour la permission "{permission_codename}"',
                'code': 'DELEGATION_NOT_FOUND'
            }, status=403)
        
        # Trouver une délégation utilisable
        usable_delegation = None
        for delegation in delegations:
            if delegation.can_use(request):
                usable_delegation = delegation
                break
        
        if not usable_delegation:
            return JsonResponse({
                'error': 'Délégation non utilisable',
                'message': 'Aucune délégation utilisable trouvée (expirée, épuisée, ou restrictions)',
                'code': 'DELEGATION_NOT_USABLE'
            }, status=403)
        
        # Utiliser la délégation
        usable_delegation.use()
        
        # Marquer la requête comme utilisant une délégation
        request.delegation_used = True
        request.delegation_source = f"{usable_delegation.delegator.email} -> {usable_delegation.delegatee.email}"
        request.delegation_remaining_uses = usable_delegation.get_remaining_uses()
        request.delegation_expires = usable_delegation.end_date
        
        # Ajouter les informations de délégation à la requête
        request.delegation_info = {
            'type': 'permission',
            'permission': permission_codename,
            'delegator': usable_delegation.delegator.email,
            'delegation_id': usable_delegation.id,
            'remaining_uses': usable_delegation.get_remaining_uses(),
            'expires_at': usable_delegation.end_date
        }
        
        logger.info(
            f"Délégation de permission utilisée: {usable_delegation.delegator.email} -> "
            f"{usable_delegation.delegatee.email} - {permission_codename}"
        )
        
        return None
    
    def _handle_role_delegation(self, request, role_name):
        """
        Gère une délégation de rôle
        """
        # Vérifier si l'utilisateur a une délégation active pour ce rôle
        delegations = RoleDelegation.get_active_delegations(
            request.user,
            role_name
        )
        
        if not delegations:
            return JsonResponse({
                'error': 'Délégation de rôle non trouvée',
                'message': f'Aucune délégation active trouvée pour le rôle "{role_name}"',
                'code': 'ROLE_DELEGATION_NOT_FOUND'
            }, status=403)
        
        # Trouver une délégation utilisable
        usable_delegation = None
        for delegation in delegations:
            if delegation.can_use(request):
                usable_delegation = delegation
                break
        
        if not usable_delegation:
            return JsonResponse({
                'error': 'Délégation de rôle non utilisable',
                'message': 'Aucune délégation de rôle utilisable trouvée',
                'code': 'ROLE_DELEGATION_NOT_USABLE'
            }, status=403)
        
        # Utiliser la délégation
        usable_delegation.use()
        
        # Marquer la requête comme utilisant une délégation
        request.delegation_used = True
        request.delegation_source = f"{usable_delegation.delegator.email} -> {usable_delegation.delegatee.email}"
        request.delegation_remaining_uses = usable_delegation.get_remaining_uses()
        request.delegation_expires = usable_delegation.end_date
        
        # Ajouter les informations de délégation à la requête
        request.delegation_info = {
            'type': 'role',
            'role': role_name,
            'delegator': usable_delegation.delegator.email,
            'delegation_id': usable_delegation.id,
            'remaining_uses': usable_delegation.get_remaining_uses(),
            'expires_at': usable_delegation.end_date,
            'effective_permissions': list(usable_delegation.get_effective_permissions().values_list('codename', flat=True))
        }
        
        logger.info(
            f"Délégation de rôle utilisée: {usable_delegation.delegator.email} -> "
            f"{usable_delegation.delegatee.email} - {role_name}"
        )
        
        return None


def use_delegation(permission_codename=None, role_name=None):
    """
    Décorateur pour forcer l'utilisation d'une délégation
    """
    def decorator(view_func):
        if permission_codename:
            view_func.required_delegation = {'type': 'permission', 'target': permission_codename}
        elif role_name:
            view_func.required_delegation = {'type': 'role', 'target': role_name}
        return view_func
    return decorator
