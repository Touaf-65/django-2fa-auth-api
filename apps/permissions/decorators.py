"""
Décorateurs pour les permissions
"""
from functools import wraps
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import has_permission, has_any_permission, has_all_permissions
from .middleware.permission_middleware import (
    require_permission, require_permissions, require_any_permission, require_all_permissions
)


def permission_required(permission_codename, resource_getter=None, context_getter=None):
    """
    Décorateur pour vérifier une permission sur une vue
    
    Args:
        permission_codename: Code de la permission requise
        resource_getter: Fonction pour récupérer la ressource (optionnel)
        context_getter: Fonction pour récupérer le contexte (optionnel)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Récupérer la ressource si nécessaire
            resource = None
            if resource_getter:
                resource = resource_getter(request, *args, **kwargs)
            
            # Récupérer le contexte si nécessaire
            context = None
            if context_getter:
                context = context_getter(request, *args, **kwargs)
            
            # Vérifier la permission
            if not has_permission(request.user, permission_codename, resource, request, context):
                return JsonResponse({
                    'error': 'Permission refusée',
                    'message': f'Vous n\'avez pas la permission "{permission_codename}"',
                    'permission_required': permission_codename,
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        # Marquer la vue comme nécessitant une permission
        wrapper.required_permission = permission_codename
        return wrapper
    return decorator


def any_permission_required(permission_codenames, resource_getter=None, context_getter=None):
    """
    Décorateur pour vérifier au moins une permission sur une vue
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Récupérer la ressource si nécessaire
            resource = None
            if resource_getter:
                resource = resource_getter(request, *args, **kwargs)
            
            # Récupérer le contexte si nécessaire
            context = None
            if context_getter:
                context = context_getter(request, *args, **kwargs)
            
            # Vérifier les permissions
            if not has_any_permission(request.user, permission_codenames, resource, request, context):
                return JsonResponse({
                    'error': 'Permission refusée',
                    'message': f'Vous n\'avez aucune des permissions requises: {permission_codenames}',
                    'permissions_required': permission_codenames,
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        # Marquer la vue comme nécessitant des permissions
        wrapper.required_any_permission = permission_codenames
        return wrapper
    return decorator


def all_permissions_required(permission_codenames, resource_getter=None, context_getter=None):
    """
    Décorateur pour vérifier toutes les permissions sur une vue
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Récupérer la ressource si nécessaire
            resource = None
            if resource_getter:
                resource = resource_getter(request, *args, **kwargs)
            
            # Récupérer le contexte si nécessaire
            context = None
            if context_getter:
                context = context_getter(request, *args, **kwargs)
            
            # Vérifier les permissions
            if not has_all_permissions(request.user, permission_codenames, resource, request, context):
                return JsonResponse({
                    'error': 'Permission refusée',
                    'message': f'Vous n\'avez pas toutes les permissions requises: {permission_codenames}',
                    'permissions_required': permission_codenames,
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        # Marquer la vue comme nécessitant des permissions
        wrapper.required_all_permissions = permission_codenames
        return wrapper
    return decorator


def method_permissions(permissions_dict, resource_getter=None, context_getter=None):
    """
    Décorateur pour vérifier des permissions par méthode HTTP
    
    Args:
        permissions_dict: Dict {method: permission_codename} ou {method: [permissions]}
        resource_getter: Fonction pour récupérer la ressource (optionnel)
        context_getter: Fonction pour récupérer le contexte (optionnel)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            method = request.method
            required_permissions = permissions_dict.get(method)
            
            if not required_permissions:
                return JsonResponse({
                    'error': 'Méthode non autorisée',
                    'message': f'La méthode {method} n\'est pas autorisée sur cette ressource',
                    'code': 'METHOD_NOT_ALLOWED'
                }, status=405)
            
            # Récupérer la ressource si nécessaire
            resource = None
            if resource_getter:
                resource = resource_getter(request, *args, **kwargs)
            
            # Récupérer le contexte si nécessaire
            context = None
            if context_getter:
                context = context_getter(request, *args, **kwargs)
            
            # Vérifier les permissions selon le type
            if isinstance(required_permissions, str):
                # Permission unique
                if not has_permission(request.user, required_permissions, resource, request, context):
                    return JsonResponse({
                        'error': 'Permission refusée',
                        'message': f'Vous n\'avez pas la permission "{required_permissions}"',
                        'permission_required': required_permissions,
                        'code': 'PERMISSION_DENIED'
                    }, status=403)
            elif isinstance(required_permissions, list):
                # Permissions multiples (au moins une)
                if not has_any_permission(request.user, required_permissions, resource, request, context):
                    return JsonResponse({
                        'error': 'Permission refusée',
                        'message': f'Vous n\'avez aucune des permissions requises: {required_permissions}',
                        'permissions_required': required_permissions,
                        'code': 'PERMISSION_DENIED'
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        # Marquer la vue comme nécessitant des permissions par méthode
        wrapper.required_permissions = permissions_dict
        return wrapper
    return decorator


def class_permission_required(permission_codename):
    """
    Décorateur de classe pour les vues basées sur les classes
    """
    def decorator(cls):
        # Appliquer le décorateur à toutes les méthodes HTTP
        for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
            if hasattr(cls, method):
                setattr(cls, method, permission_required(permission_codename)(getattr(cls, method)))
        
        return cls
    return decorator


def class_method_permissions(permissions_dict):
    """
    Décorateur de classe pour les permissions par méthode
    """
    def decorator(cls):
        for method, permission in permissions_dict.items():
            if hasattr(cls, method):
                if isinstance(permission, str):
                    setattr(cls, method, permission_required(permission)(getattr(cls, method)))
                elif isinstance(permission, list):
                    setattr(cls, method, any_permission_required(permission)(getattr(cls, method)))
        
        return cls
    return decorator


# Décorateurs pour l'audit
def audit_required(view_func):
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


# Décorateurs pour les délégations
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


# Utilitaires pour les getters
def get_resource_from_kwargs(field_name='id', model_class=None):
    """
    Factory pour créer un getter de ressource basé sur les kwargs
    """
    def resource_getter(request, *args, **kwargs):
        if field_name in kwargs:
            resource_id = kwargs[field_name]
            if model_class:
                try:
                    return model_class.objects.get(id=resource_id)
                except model_class.DoesNotExist:
                    return None
            return resource_id
        return None
    
    return resource_getter


def get_context_from_request(fields=None):
    """
    Factory pour créer un getter de contexte basé sur la requête
    """
    def context_getter(request, *args, **kwargs):
        context = {}
        
        if fields:
            for field in fields:
                if hasattr(request, field):
                    context[field] = getattr(request, field)
                elif field in request.GET:
                    context[field] = request.GET[field]
                elif hasattr(request, 'POST') and field in request.POST:
                    context[field] = request.POST[field]
        
        return context
    
    return context_getter



