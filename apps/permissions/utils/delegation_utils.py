"""
Utilitaires pour la délégation de permissions
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
# PermissionError est une exception Python standard, pas Django
from ..models import PermissionDelegation, RoleDelegation, Permission, Role

User = get_user_model()


def has_delegated_permission(user, permission_codename, request=None):
    """
    Vérifie si un utilisateur a reçu une permission par délégation
    
    Args:
        user: Utilisateur à vérifier
        permission_codename: Code de la permission
        request: Requête HTTP (optionnel)
    
    Returns:
        bool: True si l'utilisateur a la permission déléguée
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        return False
    
    delegations = PermissionDelegation.get_active_delegations(user, permission)
    
    for delegation in delegations:
        if delegation.can_use(request):
            delegation.use()
            return True
    
    return False


def can_delegate_permission(delegator, delegatee, permission_codename):
    """
    Vérifie si un utilisateur peut déléguer une permission
    
    Args:
        delegator: Utilisateur qui délègue
        delegatee: Utilisateur qui reçoit
        permission_codename: Code de la permission
    
    Returns:
        dict: Résultat de la vérification
    """
    result = {
        'can_delegate': False,
        'reason': '',
        'constraints': {}
    }
    
    if not delegator or not delegatee:
        result['reason'] = 'Utilisateur manquant'
        return result
    
    if not delegator.is_authenticated:
        result['reason'] = 'Délégateur non authentifié'
        return result
    
    if not delegatee.is_authenticated:
        result['reason'] = 'Délégué non authentifié'
        return result
    
    # Vérifier si le délégateur a la permission
    from .permission_checker import has_permission
    if not has_permission(delegator, permission_codename):
        result['reason'] = 'Le délégateur n\'a pas cette permission'
        return result
    
    # Vérifier si le délégué n'est pas un superutilisateur
    if delegatee.is_superuser:
        result['reason'] = 'Impossible de déléguer à un superutilisateur'
        return result
    
    # Vérifier les droits de délégation du délégateur
    try:
        from ..models import PermissionManager
        manager = PermissionManager.objects.get(user=delegator, is_active=True)
        
        if not manager.can_delegate_permissions:
            result['reason'] = 'Pas de droits de délégation'
            return result
        
        # Récupérer les contraintes
        constraints = manager.get_delegation_constraints()
        result['constraints'] = constraints
        
        # Vérifier les restrictions d'étendue
        try:
            permission = Permission.objects.get(codename=permission_codename, is_active=True)
            
            if constraints.get('allowed_apps') and permission.app_label not in constraints['allowed_apps']:
                result['reason'] = f'App {permission.app_label} non autorisée'
                return result
            
            if constraints.get('allowed_models') and permission.model not in constraints['allowed_models']:
                result['reason'] = f'Modèle {permission.model} non autorisé'
                return result
        
        except Permission.DoesNotExist:
            result['reason'] = 'Permission inexistante'
            return result
    
    except PermissionManager.DoesNotExist:
        # Si pas de gestionnaire, vérifier si c'est un superutilisateur
        if not delegator.is_superuser:
            result['reason'] = 'Pas de droits de délégation'
            return result
    
    result['can_delegate'] = True
    result['reason'] = 'Délégation autorisée'
    return result


def create_delegation(delegator, delegatee, permission_codename, constraints=None):
    """
    Crée une délégation de permission
    
    Args:
        delegator: Utilisateur qui délègue
        delegatee: Utilisateur qui reçoit
        permission_codename: Code de la permission
        constraints: Contraintes de la délégation
    
    Returns:
        PermissionDelegation: Instance créée
    
    Raises:
        PermissionError: Si la délégation n'est pas autorisée
    """
    # Vérifier si la délégation est autorisée
    check_result = can_delegate_permission(delegator, delegatee, permission_codename)
    if not check_result['can_delegate']:
        raise PermissionError(check_result['reason'])
    
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        raise PermissionError('Permission inexistante')
    
    # Appliquer les contraintes par défaut
    constraints = constraints or {}
    default_constraints = check_result.get('constraints', {})
    
    # Durée maximale
    max_duration_days = default_constraints.get('max_duration_days')
    if max_duration_days and 'end_date' in constraints:
        end_date = constraints['end_date']
        if isinstance(end_date, str):
            from datetime import datetime
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        max_end_date = timezone.now() + timezone.timedelta(days=max_duration_days)
        if end_date > max_end_date:
            constraints['end_date'] = max_end_date
    
    # Nombre maximum d'utilisations
    max_uses = default_constraints.get('max_uses')
    if max_uses and 'max_uses' in constraints:
        if constraints['max_uses'] > max_uses:
            constraints['max_uses'] = max_uses
    
    return PermissionDelegation.create_delegation(
        delegator=delegator,
        delegatee=delegatee,
        permission=permission,
        constraints=constraints
    )


def revoke_delegation(delegator, delegatee, permission_codename):
    """
    Révoque une délégation de permission
    
    Args:
        delegator: Utilisateur qui a délégué
        delegatee: Utilisateur qui a reçu
        permission_codename: Code de la permission
    
    Returns:
        bool: True si la révocation a réussi
    """
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        return False
    
    delegations = PermissionDelegation.objects.filter(
        delegator=delegator,
        delegatee=delegatee,
        permission=permission,
        is_active=True
    )
    
    count = 0
    for delegation in delegations:
        delegation.is_active = False
        delegation.save(update_fields=['is_active'])
        count += 1
    
    return count > 0


def can_delegate_role(delegator, delegatee, role_name):
    """
    Vérifie si un utilisateur peut déléguer un rôle
    
    Args:
        delegator: Utilisateur qui délègue
        delegatee: Utilisateur qui reçoit
        role_name: Nom du rôle
    
    Returns:
        dict: Résultat de la vérification
    """
    result = {
        'can_delegate': False,
        'reason': '',
        'constraints': {}
    }
    
    if not delegator or not delegatee:
        result['reason'] = 'Utilisateur manquant'
        return result
    
    if not delegator.is_authenticated:
        result['reason'] = 'Délégateur non authentifié'
        return result
    
    if not delegatee.is_authenticated:
        result['reason'] = 'Délégué non authentifié'
        return result
    
    # Vérifier si le délégateur a le rôle
    from .permission_checker import get_user_roles
    delegator_roles = get_user_roles(delegator)
    if not delegator_roles.filter(name=role_name).exists():
        result['reason'] = 'Le délégateur n\'a pas ce rôle'
        return result
    
    # Vérifier si le délégué n'est pas un superutilisateur
    if delegatee.is_superuser:
        result['reason'] = 'Impossible de déléguer à un superutilisateur'
        return result
    
    # Vérifier les droits de délégation du délégateur
    try:
        from ..models import PermissionManager
        manager = PermissionManager.objects.get(user=delegator, is_active=True)
        
        if not manager.can_delegate_roles:
            result['reason'] = 'Pas de droits de délégation de rôles'
            return result
        
        # Récupérer les contraintes
        constraints = manager.get_delegation_constraints()
        result['constraints'] = constraints
    
    except PermissionManager.DoesNotExist:
        # Si pas de gestionnaire, vérifier si c'est un superutilisateur
        if not delegator.is_superuser:
            result['reason'] = 'Pas de droits de délégation'
            return result
    
    result['can_delegate'] = True
    result['reason'] = 'Délégation autorisée'
    return result


def create_role_delegation(delegator, delegatee, role_name, constraints=None):
    """
    Crée une délégation de rôle
    
    Args:
        delegator: Utilisateur qui délègue
        delegatee: Utilisateur qui reçoit
        role_name: Nom du rôle
        constraints: Contraintes de la délégation
    
    Returns:
        RoleDelegation: Instance créée
    
    Raises:
        PermissionError: Si la délégation n'est pas autorisée
    """
    # Vérifier si la délégation est autorisée
    check_result = can_delegate_role(delegator, delegatee, role_name)
    if not check_result['can_delegate']:
        raise PermissionError(check_result['reason'])
    
    try:
        role = Role.objects.get(name=role_name, is_active=True)
    except Role.DoesNotExist:
        raise PermissionError('Rôle inexistant')
    
    # Appliquer les contraintes par défaut
    constraints = constraints or {}
    default_constraints = check_result.get('constraints', {})
    
    # Durée maximale
    max_duration_days = default_constraints.get('max_duration_days')
    if max_duration_days and 'end_date' in constraints:
        end_date = constraints['end_date']
        if isinstance(end_date, str):
            from datetime import datetime
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        max_end_date = timezone.now() + timezone.timedelta(days=max_duration_days)
        if end_date > max_end_date:
            constraints['end_date'] = max_end_date
    
    # Nombre maximum d'utilisations
    max_uses = default_constraints.get('max_uses')
    if max_uses and 'max_uses' in constraints:
        if constraints['max_uses'] > max_uses:
            constraints['max_uses'] = max_uses
    
    return RoleDelegation.create_delegation(
        delegator=delegator,
        delegatee=delegatee,
        role=role,
        constraints=constraints
    )


def revoke_role_delegation(delegator, delegatee, role_name):
    """
    Révoque une délégation de rôle
    
    Args:
        delegator: Utilisateur qui a délégué
        delegatee: Utilisateur qui a reçu
        role_name: Nom du rôle
    
    Returns:
        bool: True si la révocation a réussi
    """
    try:
        role = Role.objects.get(name=role_name, is_active=True)
    except Role.DoesNotExist:
        return False
    
    delegations = RoleDelegation.objects.filter(
        delegator=delegator,
        delegatee=delegatee,
        role=role,
        is_active=True
    )
    
    count = 0
    for delegation in delegations:
        delegation.is_active = False
        delegation.save(update_fields=['is_active'])
        count += 1
    
    return count > 0


def get_user_delegations(user, as_delegator=False, as_delegatee=False):
    """
    Récupère les délégations d'un utilisateur
    
    Args:
        user: Utilisateur
        as_delegator: Inclure les délégations où l'utilisateur est délégateur
        as_delegatee: Inclure les délégations où l'utilisateur est délégué
    
    Returns:
        dict: Délégations de l'utilisateur
    """
    result = {
        'as_delegator': [],
        'as_delegatee': []
    }
    
    if as_delegator:
        permission_delegations = PermissionDelegation.objects.filter(
            delegator=user,
            is_active=True
        ).select_related('delegatee', 'permission')
        
        role_delegations = RoleDelegation.objects.filter(
            delegator=user,
            is_active=True
        ).select_related('delegatee', 'role')
        
        result['as_delegator'] = {
            'permissions': list(permission_delegations),
            'roles': list(role_delegations)
        }
    
    if as_delegatee:
        permission_delegations = PermissionDelegation.objects.filter(
            delegatee=user,
            is_active=True
        ).select_related('delegator', 'permission')
        
        role_delegations = RoleDelegation.objects.filter(
            delegatee=user,
            is_active=True
        ).select_related('delegator', 'role')
        
        result['as_delegatee'] = {
            'permissions': list(permission_delegations),
            'roles': list(role_delegations)
        }
    
    return result
