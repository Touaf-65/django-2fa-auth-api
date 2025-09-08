"""
Utilitaires pour la vérification des permissions
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from ..models import (
    Permission, Role, Group, UserRole, GroupMembership, GroupRole,
    PermissionDelegation, RoleDelegation, ConditionalPermission
)

User = get_user_model()


def has_permission(user, permission_codename, resource=None, request=None, context=None):
    """
    Vérifie si un utilisateur a une permission
    
    Args:
        user: Utilisateur à vérifier
        permission_codename: Code de la permission
        resource: Ressource concernée (optionnel)
        request: Requête HTTP (optionnel)
        context: Contexte supplémentaire (optionnel)
    
    Returns:
        bool: True si l'utilisateur a la permission
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superutilisateur a toutes les permissions
    if user.is_superuser:
        return True
    
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        return False
    
    # Vérifier les contraintes de valeur si une ressource est fournie
    if resource and hasattr(resource, permission.field_name) and permission.field_name:
        field_value = getattr(resource, permission.field_name)
        if not permission.check_value_constraints(field_value):
            return False
    
    # Vérifier les conditions contextuelles
    if context and not permission.check_conditions(context):
        return False
    
    # Vérifier les permissions conditionnelles
    if not _check_conditional_permissions(permission, user, resource, request):
        return False
    
    # 1. Vérifier les rôles directs
    if _has_direct_role_permission(user, permission):
        return True
    
    # 2. Vérifier les rôles via les groupes
    if _has_group_role_permission(user, permission):
        return True
    
    # 3. Vérifier les délégations
    if _has_delegated_permission(user, permission, request):
        return True
    
    return False


def has_any_permission(user, permission_codenames, resource=None, request=None, context=None):
    """
    Vérifie si un utilisateur a au moins une des permissions
    
    Args:
        user: Utilisateur à vérifier
        permission_codenames: Liste des codes de permissions
        resource: Ressource concernée (optionnel)
        request: Requête HTTP (optionnel)
        context: Contexte supplémentaire (optionnel)
    
    Returns:
        bool: True si l'utilisateur a au moins une permission
    """
    for codename in permission_codenames:
        if has_permission(user, codename, resource, request, context):
            return True
    return False


def has_all_permissions(user, permission_codenames, resource=None, request=None, context=None):
    """
    Vérifie si un utilisateur a toutes les permissions
    
    Args:
        user: Utilisateur à vérifier
        permission_codenames: Liste des codes de permissions
        resource: Ressource concernée (optionnel)
        request: Requête HTTP (optionnel)
        context: Contexte supplémentaire (optionnel)
    
    Returns:
        bool: True si l'utilisateur a toutes les permissions
    """
    for codename in permission_codenames:
        if not has_permission(user, codename, resource, request, context):
            return False
    return True


def check_permission_with_context(user, permission_codename, resource=None, request=None, **context):
    """
    Vérifie une permission avec un contexte étendu
    
    Args:
        user: Utilisateur à vérifier
        permission_codename: Code de la permission
        resource: Ressource concernée (optionnel)
        request: Requête HTTP (optionnel)
        **context: Contexte supplémentaire
    
    Returns:
        dict: Résultat détaillé de la vérification
    """
    result = {
        'has_permission': False,
        'reason': '',
        'checked_at': timezone.now(),
        'user': user.id if user else None,
        'permission': permission_codename,
        'resource': resource.id if resource else None,
        'details': {}
    }
    
    if not user or not user.is_authenticated:
        result['reason'] = 'Utilisateur non authentifié'
        return result
    
    if user.is_superuser:
        result['has_permission'] = True
        result['reason'] = 'Superutilisateur'
        return result
    
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        result['reason'] = 'Permission inexistante ou inactive'
        return result
    
    # Vérifier les contraintes de valeur
    if resource and hasattr(resource, permission.field_name) and permission.field_name:
        field_value = getattr(resource, permission.field_name)
        if not permission.check_value_constraints(field_value):
            result['reason'] = 'Contrainte de valeur non respectée'
            result['details']['field_value'] = str(field_value)
            result['details']['min_value'] = str(permission.min_value) if permission.min_value else None
            result['details']['max_value'] = str(permission.max_value) if permission.max_value else None
            return result
    
    # Vérifier les conditions contextuelles
    if context and not permission.check_conditions(context):
        result['reason'] = 'Conditions contextuelles non respectées'
        result['details']['conditions'] = permission.conditions
        result['details']['context'] = context
        return result
    
    # Vérifier les permissions conditionnelles
    conditional_result = _check_conditional_permissions_detailed(permission, user, resource, request)
    if not conditional_result['passed']:
        result['reason'] = conditional_result['reason']
        result['details']['conditional_checks'] = conditional_result['details']
        return result
    
    # Vérifier les rôles directs
    direct_role_result = _has_direct_role_permission_detailed(user, permission)
    if direct_role_result['has_permission']:
        result['has_permission'] = True
        result['reason'] = 'Rôle direct'
        result['details']['direct_roles'] = direct_role_result['details']
        return result
    
    # Vérifier les rôles via les groupes
    group_role_result = _has_group_role_permission_detailed(user, permission)
    if group_role_result['has_permission']:
        result['has_permission'] = True
        result['reason'] = 'Rôle via groupe'
        result['details']['group_roles'] = group_role_result['details']
        return result
    
    # Vérifier les délégations
    delegation_result = _has_delegated_permission_detailed(user, permission, request)
    if delegation_result['has_permission']:
        result['has_permission'] = True
        result['reason'] = 'Délégation'
        result['details']['delegations'] = delegation_result['details']
        return result
    
    result['reason'] = 'Aucune permission trouvée'
    return result


def get_user_permissions(user, include_delegated=True):
    """
    Récupère toutes les permissions d'un utilisateur
    
    Args:
        user: Utilisateur
        include_delegated: Inclure les permissions déléguées
    
    Returns:
        QuerySet: Permissions de l'utilisateur
    """
    if not user or not user.is_authenticated:
        return Permission.objects.none()
    
    if user.is_superuser:
        return Permission.objects.filter(is_active=True)
    
    # Permissions via les rôles directs
    direct_permissions = Permission.objects.filter(
        roles__user_roles__user=user,
        roles__user_roles__is_active=True,
        roles__rolepermission__granted=True
    ).filter(
        models.Q(roles__user_roles__expires_at__isnull=True) | 
        models.Q(roles__user_roles__expires_at__gt=timezone.now())
    )
    
    # Permissions via les groupes
    group_permissions = Permission.objects.filter(
        roles__groups__users=user,
        roles__groups__groupmembership__is_active=True,
        roles__rolepermission__granted=True
    )
    
    # Combiner les permissions
    all_permissions = list(direct_permissions) + list(group_permissions)
    
    # Ajouter les permissions déléguées si demandé
    if include_delegated:
        delegated_permissions = Permission.objects.filter(
            permissiondelegation__delegatee=user,
            permissiondelegation__is_active=True,
            permissiondelegation__start_date__lte=timezone.now(),
            permissiondelegation__end_date__gte=timezone.now()
        )
        all_permissions.extend(list(delegated_permissions))
    
    # Retourner un QuerySet unique
    permission_ids = list(set(p.id for p in all_permissions))
    return Permission.objects.filter(id__in=permission_ids)


def get_user_roles(user, include_delegated=True):
    """
    Récupère tous les rôles d'un utilisateur
    
    Args:
        user: Utilisateur
        include_delegated: Inclure les rôles délégués
    
    Returns:
        QuerySet: Rôles de l'utilisateur
    """
    if not user or not user.is_authenticated:
        return Role.objects.none()
    
    if user.is_superuser:
        return Role.objects.filter(is_active=True)
    
    # Rôles directs
    direct_roles = Role.objects.filter(
        user_roles__user=user,
        user_roles__is_active=True
    ).filter(
        models.Q(user_roles__expires_at__isnull=True) | 
        models.Q(user_roles__expires_at__gt=timezone.now())
    )
    
    # Rôles via les groupes
    group_roles = Role.objects.filter(
        groups__users=user,
        groups__groupmembership__is_active=True
    )
    
    # Combiner les rôles
    all_roles = list(direct_roles) + list(group_roles)
    
    # Ajouter les rôles délégués si demandé
    if include_delegated:
        delegated_roles = Role.objects.filter(
            roledelegation__delegatee=user,
            roledelegation__is_active=True,
            roledelegation__start_date__lte=timezone.now(),
            roledelegation__end_date__gte=timezone.now()
        )
        all_roles.extend(list(delegated_roles))
    
    # Retourner un QuerySet unique
    role_ids = list(set(r.id for r in all_roles))
    return Role.objects.filter(id__in=role_ids)


def get_user_groups(user):
    """
    Récupère tous les groupes d'un utilisateur
    
    Args:
        user: Utilisateur
    
    Returns:
        QuerySet: Groupes de l'utilisateur
    """
    if not user or not user.is_authenticated:
        return Group.objects.none()
    
    return Group.objects.filter(
        users=user,
        groupmembership__is_active=True,
        is_active=True
    )


def _check_conditional_permissions(permission, user, resource, request):
    """
    Vérifie les permissions conditionnelles
    """
    conditional_permissions = ConditionalPermission.objects.filter(
        permission=permission,
        is_active=True
    )
    
    for conditional in conditional_permissions:
        if not conditional.evaluate_condition(user, resource, request):
            return False
    
    return True


def _check_conditional_permissions_detailed(permission, user, resource, request):
    """
    Vérifie les permissions conditionnelles avec détails
    """
    result = {
        'passed': True,
        'reason': '',
        'details': []
    }
    
    conditional_permissions = ConditionalPermission.objects.filter(
        permission=permission,
        is_active=True
    )
    
    for conditional in conditional_permissions:
        if not conditional.evaluate_condition(user, resource, request):
            result['passed'] = False
            result['reason'] = f'Condition {conditional.get_condition_type_display()} non respectée'
            result['details'].append({
                'type': conditional.condition_type,
                'data': conditional.condition_data
            })
    
    return result


def _has_direct_role_permission(user, permission):
    """
    Vérifie si l'utilisateur a la permission via un rôle direct
    """
    # Récupérer les rôles actifs de l'utilisateur
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
    ).select_related('role')
    
    # Vérifier si l'un des rôles a la permission
    for user_role in user_roles:
        if user_role.role.is_active and user_role.role.has_permission(permission):
            return True
    
    return False


def _has_direct_role_permission_detailed(user, permission):
    """
    Vérifie si l'utilisateur a la permission via un rôle direct avec détails
    """
    result = {
        'has_permission': False,
        'details': []
    }
    
    user_roles = UserRole.objects.filter(
        user=user,
        role__permissions=permission,
        is_active=True,
        role__is_active=True
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
    ).select_related('role')
    
    for user_role in user_roles:
        if user_role.role.has_permission(permission):
            result['has_permission'] = True
            result['details'].append({
                'role': user_role.role.name,
                'assigned_at': user_role.assigned_at,
                'expires_at': user_role.expires_at
            })
    
    return result


def _has_group_role_permission(user, permission):
    """
    Vérifie si l'utilisateur a la permission via un groupe
    """
    # Récupérer les groupes actifs de l'utilisateur
    memberships = GroupMembership.objects.filter(
        user=user,
        is_active=True,
        group__is_active=True
    ).select_related('group')
    
    # Vérifier si l'un des groupes a la permission via ses rôles
    for membership in memberships:
        group_roles = membership.group.get_roles().filter(is_active=True)
        for role in group_roles:
            if role.has_permission(permission):
                return True
    
    return False


def _has_group_role_permission_detailed(user, permission):
    """
    Vérifie si l'utilisateur a la permission via un groupe avec détails
    """
    result = {
        'has_permission': False,
        'details': []
    }
    
    memberships = GroupMembership.objects.filter(
        user=user,
        is_active=True,
        group__is_active=True
    ).select_related('group')
    
    for membership in memberships:
        group_roles = membership.group.get_roles().filter(
            permissions=permission,
            is_active=True
        )
        
        for role in group_roles:
            if role.has_permission(permission):
                result['has_permission'] = True
                result['details'].append({
                    'group': membership.group.name,
                    'role': role.name,
                    'joined_at': membership.joined_at
                })
    
    return result


def _has_delegated_permission(user, permission, request):
    """
    Vérifie si l'utilisateur a la permission via une délégation
    """
    delegations = PermissionDelegation.get_active_delegations(user, permission)
    
    for delegation in delegations:
        if delegation.can_use(request):
            delegation.use()
            return True
    
    return False


def _has_delegated_permission_detailed(user, permission, request):
    """
    Vérifie si l'utilisateur a la permission via une délégation avec détails
    """
    result = {
        'has_permission': False,
        'details': []
    }
    
    delegations = PermissionDelegation.get_active_delegations(user, permission)
    
    for delegation in delegations:
        if delegation.can_use(request):
            result['has_permission'] = True
            result['details'].append({
                'delegator': delegation.delegator.username,
                'start_date': delegation.start_date,
                'end_date': delegation.end_date,
                'remaining_uses': delegation.get_remaining_uses(),
                'remaining_time': delegation.get_remaining_time()
            })
            delegation.use()
            break
    
    return result
