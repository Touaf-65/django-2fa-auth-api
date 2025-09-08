"""
Utilitaires d'aide pour les permissions
"""
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import models
from ..models import Permission


def get_permission_codename(app_label, model, action, field_name=None):
    """
    Génère un code de permission standardisé
    
    Args:
        app_label: Label de l'application
        model: Nom du modèle
        action: Action (view, add, change, delete)
        field_name: Nom du champ (optionnel)
    
    Returns:
        str: Code de permission
    """
    if field_name:
        return f"{app_label}.{model}.{field_name}.{action}"
    else:
        return f"{app_label}.{model}.{action}"


def create_permission_from_string(permission_string, name=None, description=None, created_by=None):
    """
    Crée une permission à partir d'une chaîne
    
    Args:
        permission_string: Chaîne de permission (ex: "users.userprofile.salary.change")
        name: Nom de la permission (optionnel)
        description: Description (optionnel)
        created_by: Utilisateur créateur (optionnel)
    
    Returns:
        Permission: Instance créée
    """
    parts = permission_string.split('.')
    
    if len(parts) < 3:
        raise ValueError("Format de permission invalide. Attendu: app.model.action ou app.model.field.action")
    
    if len(parts) == 3:
        app_label, model, action = parts
        field_name = None
    elif len(parts) == 4:
        app_label, model, field_name, action = parts
    else:
        raise ValueError("Format de permission invalide. Trop de parties.")
    
    # Générer le nom si non fourni
    if not name:
        if field_name:
            name = f"Can {action} {field_name} on {model}"
        else:
            name = f"Can {action} {model}"
    
    # Générer la description si non fournie
    if not description:
        if field_name:
            description = f"Permission to {action} the {field_name} field on {model} objects"
        else:
            description = f"Permission to {action} {model} objects"
    
    return Permission.create_permission(
        name=name,
        codename=permission_string,
        description=description,
        app_label=app_label,
        model=model,
        action=action,
        field_name=field_name,
        created_by=created_by
    )


def get_model_permissions(model_class, include_field_permissions=False):
    """
    Génère les permissions standard pour un modèle
    
    Args:
        model_class: Classe du modèle
        include_field_permissions: Inclure les permissions par champ
    
    Returns:
        list: Liste des codes de permissions
    """
    app_label = model_class._meta.app_label
    model_name = model_class._meta.model_name
    
    # Permissions de base
    base_permissions = [
        get_permission_codename(app_label, model_name, 'view'),
        get_permission_codename(app_label, model_name, 'add'),
        get_permission_codename(app_label, model_name, 'change'),
        get_permission_codename(app_label, model_name, 'delete'),
    ]
    
    if not include_field_permissions:
        return base_permissions
    
    # Permissions par champ
    field_permissions = []
    for field in model_class._meta.fields:
        if field.name in ['id', 'created_at', 'updated_at']:
            continue
        
        # Permissions de lecture et modification pour chaque champ
        field_permissions.extend([
            get_permission_codename(app_label, model_name, 'view', field.name),
            get_permission_codename(app_label, model_name, 'change', field.name),
        ])
    
    return base_permissions + field_permissions


def create_model_permissions(model_class, include_field_permissions=False, created_by=None):
    """
    Crée les permissions standard pour un modèle
    
    Args:
        model_class: Classe du modèle
        include_field_permissions: Inclure les permissions par champ
        created_by: Utilisateur créateur (optionnel)
    
    Returns:
        list: Liste des permissions créées
    """
    permission_codenames = get_model_permissions(model_class, include_field_permissions)
    created_permissions = []
    
    for codename in permission_codenames:
        # Vérifier si la permission existe déjà
        if not Permission.objects.filter(codename=codename).exists():
            permission = create_permission_from_string(
                codename,
                created_by=created_by
            )
            created_permissions.append(permission)
    
    return created_permissions


def get_app_permissions(app_label, include_field_permissions=False):
    """
    Récupère toutes les permissions d'une application
    
    Args:
        app_label: Label de l'application
        include_field_permissions: Inclure les permissions par champ
    
    Returns:
        QuerySet: Permissions de l'application
    """
    queryset = Permission.objects.filter(app_label=app_label, is_active=True)
    
    if not include_field_permissions:
        queryset = queryset.filter(field_name='')
    
    return queryset


def get_user_permissions_by_app(user, app_label, include_delegated=True):
    """
    Récupère les permissions d'un utilisateur pour une application
    
    Args:
        user: Utilisateur
        app_label: Label de l'application
        include_delegated: Inclure les permissions déléguées
    
    Returns:
        QuerySet: Permissions de l'utilisateur pour l'application
    """
    from .permission_checker import get_user_permissions
    
    all_permissions = get_user_permissions(user, include_delegated)
    return all_permissions.filter(app_label=app_label)


def get_permission_hierarchy(app_label, model_name):
    """
    Génère une hiérarchie de permissions pour un modèle
    
    Args:
        app_label: Label de l'application
        model_name: Nom du modèle
    
    Returns:
        dict: Hiérarchie des permissions
    """
    return {
        'app': app_label,
        'model': model_name,
        'permissions': {
            'view': {
                'codename': get_permission_codename(app_label, model_name, 'view'),
                'description': f'Can view {model_name} objects',
                'level': 1
            },
            'add': {
                'codename': get_permission_codename(app_label, model_name, 'add'),
                'description': f'Can add {model_name} objects',
                'level': 2,
                'requires': [get_permission_codename(app_label, model_name, 'view')]
            },
            'change': {
                'codename': get_permission_codename(app_label, model_name, 'change'),
                'description': f'Can change {model_name} objects',
                'level': 3,
                'requires': [get_permission_codename(app_label, model_name, 'view')]
            },
            'delete': {
                'codename': get_permission_codename(app_label, model_name, 'delete'),
                'description': f'Can delete {model_name} objects',
                'level': 4,
                'requires': [get_permission_codename(app_label, model_name, 'view')]
            }
        }
    }


def validate_permission_string(permission_string):
    """
    Valide le format d'une chaîne de permission
    
    Args:
        permission_string: Chaîne de permission à valider
    
    Returns:
        dict: Résultat de la validation
    """
    result = {
        'valid': False,
        'error': '',
        'parts': {}
    }
    
    parts = permission_string.split('.')
    
    if len(parts) < 3:
        result['error'] = 'Format invalide. Attendu: app.model.action ou app.model.field.action'
        return result
    
    if len(parts) == 3:
        app_label, model, action = parts
        field_name = None
    elif len(parts) == 4:
        app_label, model, field_name, action = parts
    else:
        result['error'] = 'Format invalide. Trop de parties.'
        return result
    
    # Valider les parties
    if not app_label or not app_label.replace('_', '').isalnum():
        result['error'] = 'App label invalide'
        return result
    
    if not model or not model.replace('_', '').isalnum():
        result['error'] = 'Model name invalide'
        return result
    
    if field_name and (not field_name or not field_name.replace('_', '').isalnum()):
        result['error'] = 'Field name invalide'
        return result
    
    valid_actions = ['view', 'add', 'change', 'delete', 'list', 'export', 'import']
    if action not in valid_actions:
        result['error'] = f'Action invalide. Actions valides: {", ".join(valid_actions)}'
        return result
    
    result['valid'] = True
    result['parts'] = {
        'app_label': app_label,
        'model': model,
        'field_name': field_name,
        'action': action
    }
    
    return result


def get_permission_statistics():
    """
    Récupère les statistiques des permissions
    
    Returns:
        dict: Statistiques des permissions
    """
    from django.contrib.auth import get_user_model
    from ..models import Role, Group, UserRole, GroupMembership
    
    User = get_user_model()
    
    return {
        'permissions': {
            'total': Permission.objects.filter(is_active=True).count(),
            'custom': Permission.objects.filter(is_active=True, is_custom=True).count(),
            'by_app': dict(Permission.objects.filter(is_active=True).values_list('app_label').annotate(
                count=models.Count('id')
            ))
        },
        'roles': {
            'total': Role.objects.filter(is_active=True).count(),
            'system': Role.objects.filter(is_active=True, is_system=True).count(),
            'custom': Role.objects.filter(is_active=True, is_system=False).count()
        },
        'groups': {
            'total': Group.objects.filter(is_active=True).count(),
            'with_members': Group.objects.filter(is_active=True).annotate(
                member_count=models.Count('users', filter=models.Q(groupmembership__is_active=True))
            ).filter(member_count__gt=0).count()
        },
        'users': {
            'total': User.objects.filter(is_active=True).count(),
            'with_roles': User.objects.filter(is_active=True).annotate(
                role_count=models.Count('user_roles', filter=models.Q(user_roles__is_active=True))
            ).filter(role_count__gt=0).count(),
            'in_groups': User.objects.filter(is_active=True).annotate(
                group_count=models.Count('permission_groups', filter=models.Q(groupmembership__is_active=True))
            ).filter(group_count__gt=0).count()
        }
    }
