"""
Middleware principal pour la gestion des permissions
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.urls import resolve, Resolver404
from django.utils import timezone
from ..utils import has_permission, check_permission_with_context
from apps.security.models import SecurityEvent

logger = logging.getLogger(__name__)


class PermissionMiddleware(MiddlewareMixin):
    """
    Middleware pour la vérification automatique des permissions
    """
    
    def process_request(self, request):
        """
        Traite chaque requête entrante pour vérifier les permissions
        """
        # Ignorer les requêtes non authentifiées (gérées par Django)
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Ignorer les superutilisateurs
        if request.user.is_superuser:
            return None
        
        # Extraire les informations de la requête
        try:
            resolver_match = resolve(request.path)
            view_func = resolver_match.func
            view_name = resolver_match.view_name
            app_name = resolver_match.app_name
            url_name = resolver_match.url_name
        except Resolver404:
            # URL non trouvée, laisser Django gérer
            return None
        
        # Déterminer la permission requise
        required_permission = self._get_required_permission(request, resolver_match)
        
        if not required_permission:
            # Aucune permission requise pour cette vue
            return None
        
        # Vérifier la permission
        has_perm = has_permission(
            user=request.user,
            permission_codename=required_permission,
            resource=self._get_resource_from_request(request),
            request=request,
            context=self._get_context_from_request(request)
        )
        
        if not has_perm:
            # Enregistrer l'événement de sécurité
            self._log_permission_denied(request, required_permission)
            
            # Retourner une réponse d'erreur
            return JsonResponse({
                'error': 'Permission refusée',
                'message': f'Vous n\'avez pas la permission "{required_permission}" pour accéder à cette ressource.',
                'permission_required': required_permission,
                'code': 'PERMISSION_DENIED'
            }, status=403)
        
        # Ajouter les informations de permission à la requête
        request.permission_checked = True
        request.permission_required = required_permission
        request.permission_granted = True
        
        return None
    
    def process_response(self, request, response):
        """
        Traite la réponse pour ajouter des informations de permission
        """
        if hasattr(request, 'permission_checked') and request.permission_checked:
            # Ajouter des headers informatifs
            response['X-Permission-Required'] = request.permission_required
            response['X-Permission-Granted'] = 'true'
            
            # Ajouter des informations de délégation si applicable
            if hasattr(request, 'delegation_used'):
                response['X-Delegation-Used'] = 'true'
                response['X-Delegation-Source'] = request.delegation_source
        
        return response
    
    def _get_required_permission(self, request, resolver_match):
        """
        Détermine la permission requise pour une vue
        """
        # Récupérer les informations de la vue
        view_func = resolver_match.func
        app_name = resolver_match.app_name
        url_name = resolver_match.url_name
        method = request.method
        
        # Vérifier si la vue a une permission définie
        if hasattr(view_func, 'required_permission'):
            return view_func.required_permission
        
        # Vérifier si la vue a des permissions définies par méthode
        if hasattr(view_func, 'required_permissions'):
            method_permissions = view_func.required_permissions
            if method in method_permissions:
                return method_permissions[method]
        
        # Générer la permission basée sur l'URL et la méthode
        return self._generate_permission_from_url(app_name, url_name, method)
    
    def _generate_permission_from_url(self, app_name, url_name, method):
        """
        Génère une permission basée sur l'URL et la méthode HTTP
        """
        # Mapping des méthodes HTTP vers les actions
        method_to_action = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }
        
        action = method_to_action.get(method, 'view')
        
        # Extraire le modèle de l'URL
        model_name = self._extract_model_from_url_name(url_name)
        
        if not model_name:
            return None
        
        # Générer le code de permission
        return f"{app_name}.{model_name}.{action}"
    
    def _extract_model_from_url_name(self, url_name):
        """
        Extrait le nom du modèle à partir du nom de l'URL
        """
        # Patterns communs pour extraire le modèle
        patterns = [
            r'^(\w+)_list$',           # user_list -> user
            r'^(\w+)_detail$',         # user_detail -> user
            r'^(\w+)_create$',         # user_create -> user
            r'^(\w+)_update$',         # user_update -> user
            r'^(\w+)_delete$',         # user_delete -> user
            r'^(\w+)$',                # user -> user
        ]
        
        import re
        for pattern in patterns:
            match = re.match(pattern, url_name)
            if match:
                return match.group(1)
        
        return None
    
    def _get_resource_from_request(self, request):
        """
        Extrait la ressource concernée de la requête
        """
        # Essayer d'extraire l'ID de la ressource depuis l'URL
        try:
            resolver_match = resolve(request.path)
            kwargs = resolver_match.kwargs
            
            # Chercher un ID dans les paramètres
            for key, value in kwargs.items():
                if key.endswith('_id') or key == 'id':
                    # Ici, on pourrait récupérer l'objet depuis la base de données
                    # Pour l'instant, on retourne None
                    return None
            
        except (Resolver404, AttributeError):
            pass
        
        return None
    
    def _get_context_from_request(self, request):
        """
        Extrait le contexte de la requête
        """
        context = {}
        
        # Ajouter les paramètres de requête
        context.update(request.GET.dict())
        
        # Ajouter les données POST si disponibles
        if hasattr(request, 'POST') and request.POST:
            context.update(request.POST.dict())
        
        # Ajouter les informations de l'utilisateur
        if request.user.is_authenticated:
            context['user_id'] = request.user.id
            context['user_email'] = request.user.email
            
            # Ajouter les informations du profil si disponible
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                if hasattr(profile, 'department'):
                    context['department'] = profile.department
                if hasattr(profile, 'level'):
                    context['level'] = profile.level
        
        # Ajouter les informations de la requête
        context['method'] = request.method
        context['path'] = request.path
        
        return context
    
    def _log_permission_denied(self, request, permission_required):
        """
        Enregistre un événement de sécurité pour un accès refusé
        """
        try:
            # Récupérer l'IP du client
            ip_address = self._get_client_ip(request)
            
            # Créer l'événement de sécurité
            SecurityEvent.create_event(
                event_type=SecurityEvent.SUSPICIOUS_ACTIVITY,
                title='Accès refusé - Permission manquante',
                description=f'Utilisateur {request.user.email} a tenté d\'accéder à {request.path} sans la permission "{permission_required}"',
                ip_address=ip_address,
                user=request.user,
                severity=SecurityEvent.MEDIUM,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={
                    'permission_required': permission_required,
                    'path': request.path,
                    'method': request.method,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            logger.warning(
                f"Permission refusée: {request.user.email} - {permission_required} - {request.path}"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'événement de sécurité: {str(e)}")
    
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


def require_permission(permission_codename):
    """
    Décorateur pour marquer une vue comme nécessitant une permission
    """
    def decorator(view_func):
        view_func.required_permission = permission_codename
        return view_func
    return decorator


def require_permissions(permissions_dict):
    """
    Décorateur pour marquer une vue comme nécessitant des permissions par méthode
    """
    def decorator(view_func):
        view_func.required_permissions = permissions_dict
        return view_func
    return decorator


def require_any_permission(permission_codenames):
    """
    Décorateur pour marquer une vue comme nécessitant au moins une permission
    """
    def decorator(view_func):
        view_func.required_any_permission = permission_codenames
        return view_func
    return decorator


def require_all_permissions(permission_codenames):
    """
    Décorateur pour marquer une vue comme nécessitant toutes les permissions
    """
    def decorator(view_func):
        view_func.required_all_permissions = permission_codenames
        return view_func
    return decorator
