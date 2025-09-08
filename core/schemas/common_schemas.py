"""
Schémas OpenAPI communs pour l'API
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status


# Schémas d'erreur communs
error_400_schema = {
    'description': 'Données invalides',
    'content': {
        'application/json': {
            'example': {
                'field_name': ['Message d\'erreur spécifique au champ.'],
                'non_field_errors': ['Erreur générale de validation.']
            }
        }
    }
}

error_401_schema = {
    'description': 'Authentification requise',
    'content': {
        'application/json': {
            'example': {
                'detail': 'Authentication credentials were not provided.'
            }
        }
    }
}

error_403_schema = {
    'description': 'Permissions insuffisantes',
    'content': {
        'application/json': {
            'example': {
                'detail': 'You do not have permission to perform this action.'
            }
        }
    }
}

error_404_schema = {
    'description': 'Ressource non trouvée',
    'content': {
        'application/json': {
            'example': {
                'detail': 'Not found.'
            }
        }
    }
}

error_500_schema = {
    'description': 'Erreur serveur interne',
    'content': {
        'application/json': {
            'example': {
                'detail': 'A server error occurred.'
            }
        }
    }
}

# Schémas de pagination
pagination_schema = {
    'type': 'object',
    'properties': {
        'count': {
            'type': 'integer',
            'description': 'Nombre total d\'éléments',
            'example': 100
        },
        'page': {
            'type': 'integer',
            'description': 'Numéro de page actuelle',
            'example': 1
        },
        'page_size': {
            'type': 'integer',
            'description': 'Taille de page',
            'example': 20
        },
        'total_pages': {
            'type': 'integer',
            'description': 'Nombre total de pages',
            'example': 5
        },
        'next': {
            'type': 'string',
            'nullable': True,
            'description': 'URL de la page suivante',
            'example': 'http://localhost:8000/api/permissions/permissions/?page=2'
        },
        'previous': {
            'type': 'string',
            'nullable': True,
            'description': 'URL de la page précédente',
            'example': None
        }
    }
}

# Schémas de filtrage communs
filtering_schema = extend_schema(
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Recherche textuelle',
            examples=[
                OpenApiExample('Search term', value='user'),
                OpenApiExample('Multiple words', value='john doe'),
            ]
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Tri des résultats (préfixez avec - pour tri décroissant)',
            examples=[
                OpenApiExample('Ascending', value='name'),
                OpenApiExample('Descending', value='-created_at'),
                OpenApiExample('Multiple fields', value='app_label,model,action'),
            ]
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Numéro de page',
            examples=[
                OpenApiExample('First page', value=1),
                OpenApiExample('Second page', value=2),
            ]
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Taille de page (max 100)',
            examples=[
                OpenApiExample('Default size', value=20),
                OpenApiExample('Large page', value=50),
            ]
        ),
    ]
)

# Schémas d'authentification
auth_header_schema = {
    'type': 'object',
    'properties': {
        'Authorization': {
            'type': 'string',
            'description': 'Token JWT d\'authentification',
            'example': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        }
    },
    'required': ['Authorization']
}

# Schémas de délégation
delegation_header_schema = {
    'type': 'object',
    'properties': {
        'X-Use-Delegation': {
            'type': 'string',
            'description': 'Utiliser une délégation pour cette requête',
            'example': 'permission:users.userprofile.change_salary'
        }
    }
}

# Schémas de réponse de succès générique
success_response_schema = {
    'type': 'object',
    'properties': {
        'message': {
            'type': 'string',
            'description': 'Message de succès',
            'example': 'Opération effectuée avec succès'
        },
        'data': {
            'type': 'object',
            'description': 'Données retournées (optionnel)'
        }
    }
}

# Schémas de validation
validation_error_schema = {
    'type': 'object',
    'properties': {
        'field_name': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'Erreurs de validation pour un champ spécifique',
            'example': ['Ce champ est requis.', 'Ce champ doit être unique.']
        },
        'non_field_errors': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'Erreurs de validation générales',
            'example': ['Les données fournies sont invalides.']
        }
    }
}

# Schémas de métadonnées
metadata_schema = {
    'type': 'object',
    'properties': {
        'created_at': {
            'type': 'string',
            'format': 'date-time',
            'description': 'Date de création',
            'example': '2025-09-08T10:00:00Z'
        },
        'updated_at': {
            'type': 'string',
            'format': 'date-time',
            'description': 'Date de dernière modification',
            'example': '2025-09-08T10:00:00Z'
        },
        'created_by': {
            'type': 'integer',
            'description': 'ID de l\'utilisateur créateur',
            'example': 1
        },
        'created_by_username': {
            'type': 'string',
            'description': 'Nom d\'utilisateur du créateur',
            'example': 'admin@example.com'
        }
    }
}

# Schémas de statut
status_schema = {
    'type': 'object',
    'properties': {
        'is_active': {
            'type': 'boolean',
            'description': 'Statut actif/inactif',
            'example': True
        },
        'status_display': {
            'type': 'string',
            'description': 'Affichage du statut',
            'example': 'Actif'
        }
    }
}

# Schémas de relations
user_relation_schema = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'description': 'ID de l\'utilisateur',
            'example': 1
        },
        'email': {
            'type': 'string',
            'format': 'email',
            'description': 'Email de l\'utilisateur',
            'example': 'user@example.com'
        },
        'first_name': {
            'type': 'string',
            'description': 'Prénom',
            'example': 'John'
        },
        'last_name': {
            'type': 'string',
            'description': 'Nom',
            'example': 'Doe'
        },
        'full_name': {
            'type': 'string',
            'description': 'Nom complet',
            'example': 'John Doe'
        }
    }
}

# Schémas de permissions
permission_relation_schema = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'description': 'ID de la permission',
            'example': 1
        },
        'name': {
            'type': 'string',
            'description': 'Nom de la permission',
            'example': 'Can view user profile'
        },
        'codename': {
            'type': 'string',
            'description': 'Code de la permission',
            'example': 'users.userprofile.view'
        },
        'description': {
            'type': 'string',
            'description': 'Description de la permission',
            'example': 'Permission to view user profiles'
        }
    }
}

# Schémas de rôles
role_relation_schema = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'description': 'ID du rôle',
            'example': 1
        },
        'name': {
            'type': 'string',
            'description': 'Nom du rôle',
            'example': 'HR Manager'
        },
        'description': {
            'type': 'string',
            'description': 'Description du rôle',
            'example': 'Human Resources Manager role'
        },
        'is_system': {
            'type': 'boolean',
            'description': 'Rôle système',
            'example': False
        },
        'is_active': {
            'type': 'boolean',
            'description': 'Rôle actif',
            'example': True
        }
    }
}

