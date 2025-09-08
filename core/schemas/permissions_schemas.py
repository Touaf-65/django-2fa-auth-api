"""
Schémas OpenAPI pour le système de permissions
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status


# Schémas pour les permissions
permission_list_schema = extend_schema(
    operation_id='list_permissions',
    summary='Lister les permissions',
    description='''
    Récupère la liste paginée des permissions avec filtrage et recherche.
    
    **Filtres disponibles :**
    - `app_label` : Filtrer par application
    - `model` : Filtrer par modèle
    - `action` : Filtrer par action (view, add, change, delete)
    - `is_custom` : Filtrer par type (true/false)
    - `is_active` : Filtrer par statut (true/false)
    - `search` : Recherche textuelle dans le nom et la description
    
    **Tri :**
    - `ordering` : Tri par champ (ex: `app_label,model,action`)
    ''',
    tags=['Permissions'],
    parameters=[
        OpenApiParameter(
            name='app_label',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrer par application',
            examples=[
                OpenApiExample('Users app', value='users'),
                OpenApiExample('Permissions app', value='permissions'),
            ]
        ),
        OpenApiParameter(
            name='model',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrer par modèle',
            examples=[
                OpenApiExample('User model', value='user'),
                OpenApiExample('Permission model', value='permission'),
            ]
        ),
        OpenApiParameter(
            name='action',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrer par action',
            examples=[
                OpenApiExample('View action', value='view'),
                OpenApiExample('Change action', value='change'),
            ]
        ),
        OpenApiParameter(
            name='is_custom',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrer par type de permission',
            examples=[
                OpenApiExample('Custom permissions', value=True),
                OpenApiExample('System permissions', value=False),
            ]
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Recherche textuelle',
            examples=[
                OpenApiExample('Search user', value='user'),
                OpenApiExample('Search salary', value='salary'),
            ]
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Tri des résultats',
            examples=[
                OpenApiExample('Sort by app', value='app_label'),
                OpenApiExample('Sort by model', value='model'),
                OpenApiExample('Sort by action', value='action'),
            ]
        ),
    ],
    examples=[
        OpenApiExample(
            'Liste des permissions',
            summary='Permissions avec pagination',
            description='Réponse avec liste paginée des permissions',
            value={
                'results': [
                    {
                        'id': 1,
                        'name': 'Can view user profile',
                        'codename': 'users.userprofile.view',
                        'description': 'Permission to view user profiles',
                        'app_label': 'users',
                        'model': 'userprofile',
                        'action': 'view',
                        'field_name': None,
                        'min_value': None,
                        'max_value': None,
                        'conditions': None,
                        'is_custom': False,
                        'is_custom_display': 'Système',
                        'is_active': True,
                        'created_by': 1,
                        'created_by_username': 'admin@example.com',
                        'created_at': '2025-09-08T10:00:00Z',
                        'updated_at': '2025-09-08T10:00:00Z'
                    }
                ],
                'count': 25,
                'page': 1,
                'page_size': 20,
                'total_pages': 2
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': 'Liste des permissions récupérée avec succès',
        },
        401: {
            'description': 'Authentification requise',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Authentication credentials were not provided.'
                    }
                }
            }
        },
        403: {
            'description': 'Permissions insuffisantes',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'You do not have permission to perform this action.'
                    }
                }
            }
        }
    }
)

permission_create_schema = extend_schema(
    operation_id='create_permission',
    summary='Créer une permission',
    description='''
    Crée une nouvelle permission personnalisée avec contraintes granulaires.
    
    **Types de permissions :**
    - **Permission simple** : Accès basique (view, add, change, delete)
    - **Permission de champ** : Accès à un champ spécifique
    - **Permission avec contraintes** : Accès avec limites de valeur
    - **Permission conditionnelle** : Accès basé sur des conditions
    
    **Exemples d'utilisation :**
    - Permission pour modifier le salaire avec limite max
    - Permission pour voir les données sensibles selon le département
    - Permission pour supprimer uniquement ses propres données
    ''',
    tags=['Permissions'],
    examples=[
        OpenApiExample(
            'Permission simple',
            summary='Permission basique',
            description='Création d\'une permission simple',
            value={
                'name': 'Can view user profiles',
                'codename': 'users.userprofile.view',
                'description': 'Permission to view user profiles',
                'app_label': 'users',
                'model': 'userprofile',
                'action': 'view'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Permission de champ',
            summary='Permission sur un champ',
            description='Permission pour modifier un champ spécifique',
            value={
                'name': 'Can modify user salary',
                'codename': 'users.userprofile.change_salary',
                'description': 'Permission to modify user salary field',
                'app_label': 'users',
                'model': 'userprofile',
                'action': 'change',
                'field_name': 'salary'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Permission avec contraintes',
            summary='Permission avec limites',
            description='Permission avec contraintes de valeur',
            value={
                'name': 'Can modify salary with limits',
                'codename': 'users.userprofile.change_salary_limited',
                'description': 'Permission to modify salary with constraints',
                'app_label': 'users',
                'model': 'userprofile',
                'action': 'change',
                'field_name': 'salary',
                'min_value': 0,
                'max_value': 100000,
                'conditions': {
                    'department': 'HR',
                    'level': 'manager'
                }
            },
            request_only=True,
        ),
        OpenApiExample(
            'Permission créée',
            summary='Permission créée avec succès',
            description='Réponse après création réussie',
            value={
                'id': 1,
                'name': 'Can modify user salary',
                'codename': 'users.userprofile.change_salary',
                'description': 'Permission to modify user salary field',
                'app_label': 'users',
                'model': 'userprofile',
                'action': 'change',
                'field_name': 'salary',
                'min_value': 0,
                'max_value': 100000,
                'conditions': {
                    'department': 'HR'
                },
                'is_custom': True,
                'is_custom_display': 'Personnalisée',
                'is_active': True,
                'created_by': 1,
                'created_by_username': 'admin@example.com',
                'created_at': '2025-09-08T10:00:00Z',
                'updated_at': '2025-09-08T10:00:00Z'
            },
            response_only=True,
        )
    ],
    responses={
        201: {
            'description': 'Permission créée avec succès',
        },
        400: {
            'description': 'Données invalides',
            'content': {
                'application/json': {
                    'example': {
                        'codename': ['Une permission avec ce code existe déjà.'],
                        'name': ['Ce champ est requis.']
                    }
                }
            }
        },
        401: {
            'description': 'Authentification requise',
        },
        403: {
            'description': 'Permissions insuffisantes pour créer des permissions',
        }
    }
)

# Schémas pour les rôles
role_create_schema = extend_schema(
    operation_id='create_role',
    summary='Créer un rôle',
    description='''
    Crée un nouveau rôle avec des permissions assignées.
    
    **Types de rôles :**
    - **Rôle système** : Rôles prédéfinis (Admin, User, etc.)
    - **Rôle personnalisé** : Rôles créés par les administrateurs
    
    **Assignation de permissions :**
    - Utilisez `permission_ids` pour assigner des permissions existantes
    - Les permissions sont vérifiées avant assignation
    ''',
    tags=['Permissions'],
    examples=[
        OpenApiExample(
            'Rôle HR Manager',
            summary='Rôle avec permissions',
            description='Création d\'un rôle HR Manager',
            value={
                'name': 'HR Manager',
                'description': 'Human Resources Manager role with salary management permissions',
                'permission_ids': [1, 2, 3, 4],
                'is_system': False
            },
            request_only=True,
        ),
        OpenApiExample(
            'Rôle créé',
            summary='Rôle créé avec succès',
            description='Réponse après création du rôle',
            value={
                'id': 1,
                'name': 'HR Manager',
                'description': 'Human Resources Manager role',
                'permissions': [
                    {
                        'id': 1,
                        'name': 'Can view user profile',
                        'codename': 'users.userprofile.view'
                    },
                    {
                        'id': 2,
                        'name': 'Can modify user salary',
                        'codename': 'users.userprofile.change_salary'
                    }
                ],
                'is_system': False,
                'is_active': True,
                'created_by': 1,
                'created_by_username': 'admin@example.com',
                'created_at': '2025-09-08T10:00:00Z',
                'updated_at': '2025-09-08T10:00:00Z'
            },
            response_only=True,
        )
    ],
    responses={
        201: {
            'description': 'Rôle créé avec succès',
        },
        400: {
            'description': 'Données invalides',
            'content': {
                'application/json': {
                    'example': {
                        'name': ['Un rôle avec ce nom existe déjà.'],
                        'permission_ids': ['Permission ID 999 n\'existe pas.']
                    }
                }
            }
        }
    }
)

# Schémas pour les délégations
delegation_create_schema = extend_schema(
    operation_id='create_permission_delegation',
    summary='Créer une délégation de permission',
    description='''
    Crée une délégation temporaire de permission entre utilisateurs.
    
    **Types de délégations :**
    - **Délégation de permission** : Délégation d'une permission spécifique
    - **Délégation de rôle** : Délégation d'un rôle complet
    
    **Contraintes de sécurité :**
    - Limitation par IP (optionnelle)
    - Limitation par actions HTTP (optionnelle)
    - Limitation par nombre d'utilisations
    - Limitation temporelle (début/fin)
    - Conditions supplémentaires (JSON)
    
    **Cas d'usage :**
    - Délégation temporaire pendant les vacances
    - Accès limité pour des consultants
    - Permissions d'urgence avec restrictions
    ''',
    tags=['Permissions'],
    examples=[
        OpenApiExample(
            'Délégation simple',
            summary='Délégation basique',
            description='Délégation simple d\'une permission',
            value={
                'delegatee': 2,
                'permission': 1,
                'start_date': '2025-09-08T10:00:00Z',
                'end_date': '2025-09-15T18:00:00Z',
                'max_uses': 10
            },
            request_only=True,
        ),
        OpenApiExample(
            'Délégation sécurisée',
            summary='Délégation avec restrictions',
            description='Délégation avec contraintes de sécurité',
            value={
                'delegatee': 2,
                'permission': 1,
                'start_date': '2025-09-08T10:00:00Z',
                'end_date': '2025-09-15T18:00:00Z',
                'max_uses': 5,
                'allowed_ips': ['192.168.1.100', '10.0.0.50'],
                'allowed_actions': ['GET', 'POST'],
                'conditions': {
                    'department': 'HR',
                    'time_range': 'business_hours',
                    'require_2fa': True
                }
            },
            request_only=True,
        ),
        OpenApiExample(
            'Délégation créée',
            summary='Délégation créée avec succès',
            description='Réponse après création de la délégation',
            value={
                'id': 1,
                'delegator': {
                    'id': 1,
                    'email': 'admin@example.com',
                    'first_name': 'Admin',
                    'last_name': 'User'
                },
                'delegatee': {
                    'id': 2,
                    'email': 'temp@example.com',
                    'first_name': 'Temp',
                    'last_name': 'User'
                },
                'permission': {
                    'id': 1,
                    'name': 'Can modify user salary',
                    'codename': 'users.userprofile.change_salary'
                },
                'start_date': '2025-09-08T10:00:00Z',
                'end_date': '2025-09-15T18:00:00Z',
                'max_uses': 10,
                'current_uses': 0,
                'allowed_ips': ['192.168.1.100'],
                'allowed_actions': ['GET', 'POST'],
                'conditions': {
                    'department': 'HR'
                },
                'is_active': True,
                'created_at': '2025-09-08T10:00:00Z',
                'updated_at': '2025-09-08T10:00:00Z'
            },
            response_only=True,
        )
    ],
    responses={
        201: {
            'description': 'Délégation créée avec succès',
        },
        400: {
            'description': 'Données invalides',
            'content': {
                'application/json': {
                    'example': {
                        'delegatee': ['Utilisateur invalide.'],
                        'permission': ['Permission invalide.'],
                        'end_date': ['La date de fin doit être postérieure à la date de début.']
                    }
                }
            }
        },
        403: {
            'description': 'Pas le droit de déléguer cette permission',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Vous n\'avez pas le droit de déléguer cette permission.'
                    }
                }
            }
        }
    }
)

# Schémas pour les statistiques
permission_stats_schema = extend_schema(
    operation_id='permission_stats',
    summary='Statistiques des permissions',
    description='''
    Récupère les statistiques détaillées du système de permissions.
    
    **Métriques incluses :**
    - Nombre total de permissions
    - Répartition par type (système/personnalisé)
    - Répartition par application
    - Répartition par action
    - Permissions les plus utilisées
    - Évolution dans le temps
    ''',
    tags=['Permissions'],
    examples=[
        OpenApiExample(
            'Statistiques complètes',
            summary='Métriques du système',
            description='Statistiques détaillées des permissions',
            value={
                'total_permissions': 25,
                'custom_permissions': 5,
                'system_permissions': 20,
                'active_permissions': 23,
                'inactive_permissions': 2,
                'permissions_by_app': {
                    'users': 10,
                    'permissions': 8,
                    'notifications': 4,
                    'security': 3
                },
                'permissions_by_action': {
                    'view': 8,
                    'add': 6,
                    'change': 7,
                    'delete': 4
                },
                'permissions_by_type': {
                    'field_permissions': 3,
                    'conditional_permissions': 2,
                    'value_constrained_permissions': 4,
                    'simple_permissions': 16
                },
                'most_used_permissions': [
                    {
                        'id': 1,
                        'name': 'Can view user profile',
                        'codename': 'users.userprofile.view',
                        'usage_count': 150
                    },
                    {
                        'id': 2,
                        'name': 'Can modify user profile',
                        'codename': 'users.userprofile.change',
                        'usage_count': 89
                    }
                ],
                'recent_activity': {
                    'permissions_created_last_week': 2,
                    'permissions_modified_last_week': 5,
                    'active_delegations': 3
                }
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': 'Statistiques récupérées avec succès',
        },
        401: {
            'description': 'Authentification requise',
        },
        403: {
            'description': 'Permissions insuffisantes pour voir les statistiques',
        }
    }
)

