"""
Schémas OpenAPI pour l'authentification
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status


# Schémas pour l'inscription
register_schema = extend_schema(
    operation_id='user_register',
    summary='Inscription d\'un nouvel utilisateur',
    description='''
    Crée un nouveau compte utilisateur avec validation email.
    
    **Validation :**
    - Email doit être unique
    - Mot de passe minimum 8 caractères
    - Prénom et nom requis
    
    **Réponse :**
    - 201 : Utilisateur créé avec succès
    - 400 : Données invalides
    ''',
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Inscription réussie',
            summary='Exemple d\'inscription',
            description='Inscription d\'un nouvel utilisateur',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1234567890'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Réponse de succès',
            summary='Utilisateur créé',
            description='Réponse après création réussie',
            value={
                'id': 1,
                'email': 'user@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1234567890',
                'is_active': True,
                'date_joined': '2025-09-08T10:00:00Z',
                'message': 'Utilisateur créé avec succès. Vérifiez votre email pour activer votre compte.'
            },
            response_only=True,
        )
    ],
    responses={
        201: {
            'description': 'Utilisateur créé avec succès',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'email': 'user@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'phone': '+1234567890',
                        'is_active': True,
                        'date_joined': '2025-09-08T10:00:00Z',
                        'message': 'Utilisateur créé avec succès. Vérifiez votre email pour activer votre compte.'
                    }
                }
            }
        },
        400: {
            'description': 'Données invalides',
            'content': {
                'application/json': {
                    'example': {
                        'email': ['Un utilisateur avec cet email existe déjà.'],
                        'password': ['Ce mot de passe est trop court. Il doit contenir au moins 8 caractères.']
                    }
                }
            }
        }
    }
)

# Schémas pour la connexion
login_schema = extend_schema(
    operation_id='user_login',
    summary='Connexion utilisateur',
    description='''
    Authentifie un utilisateur et retourne les tokens JWT.
    
    **Processus :**
    1. Vérification des identifiants
    2. Génération des tokens JWT
    3. Création d'une session
    4. Envoi d'email de notification
    
    **2FA :**
    Si l'utilisateur a activé la 2FA, un code TOTP sera requis.
    ''',
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Connexion simple',
            summary='Connexion sans 2FA',
            description='Connexion d\'un utilisateur sans 2FA activée',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Connexion avec 2FA',
            summary='Connexion avec 2FA',
            description='Connexion d\'un utilisateur avec 2FA activée',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123',
                'totp_code': '123456'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Réponse de succès',
            summary='Connexion réussie',
            description='Tokens JWT retournés après connexion',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'email': 'user@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'is_2fa_enabled': False
                },
                'session_key': 'abc123def456'
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': 'Connexion réussie',
            'content': {
                'application/json': {
                    'example': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'email': 'user@example.com',
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'is_2fa_enabled': False
                        },
                        'session_key': 'abc123def456'
                    }
                }
            }
        },
        400: {
            'description': 'Identifiants invalides',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Email ou mot de passe incorrect'
                    }
                }
            }
        },
        401: {
            'description': 'Code 2FA requis ou invalide',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Code 2FA requis',
                        'requires_2fa': True
                    }
                }
            }
        }
    }
)

# Schémas pour le refresh token
refresh_token_schema = extend_schema(
    operation_id='token_refresh',
    summary='Rafraîchir le token d\'accès',
    description='''
    Génère un nouveau token d'accès à partir du refresh token.
    
    **Utilisation :**
    - Utilisez le refresh token pour obtenir un nouveau access token
    - Le refresh token expire après 7 jours
    - Les tokens sont automatiquement mis en blacklist après rotation
    ''',
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Refresh token',
            summary='Rafraîchir le token',
            description='Demande de nouveau token d\'accès',
            value={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Nouveau token',
            summary='Nouveau token d\'accès',
            description='Nouveau token d\'accès généré',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': 'Nouveau token généré',
            'content': {
                'application/json': {
                    'example': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            }
        },
        401: {
            'description': 'Refresh token invalide ou expiré',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Token is invalid or expired'
                    }
                }
            }
        }
    }
)

# Schémas pour la configuration 2FA
setup_2fa_schema = extend_schema(
    operation_id='setup_2fa',
    summary='Configurer la 2FA TOTP',
    description='''
    Configure l'authentification à deux facteurs TOTP pour l'utilisateur.
    
    **Processus :**
    1. Génération d'une clé secrète TOTP
    2. Création d'un QR code pour l'application d'authentification
    3. Sauvegarde de la configuration 2FA
    
    **Applications compatibles :**
    - Google Authenticator
    - Authy
    - Microsoft Authenticator
    ''',
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Configuration 2FA',
            summary='Configuration réussie',
            description='Réponse après configuration 2FA',
            value={
                'secret_key': 'JBSWY3DPEHPK3PXP',
                'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',
                'backup_codes': [
                    '12345678',
                    '87654321',
                    '11223344',
                    '44332211'
                ],
                'message': '2FA configurée avec succès. Scannez le QR code avec votre application d\'authentification.'
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': '2FA configurée avec succès',
            'content': {
                'application/json': {
                    'example': {
                        'secret_key': 'JBSWY3DPEHPK3PXP',
                        'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...',
                        'backup_codes': [
                            '12345678',
                            '87654321',
                            '11223344',
                            '44332211'
                        ],
                        'message': '2FA configurée avec succès. Scannez le QR code avec votre application d\'authentification.'
                    }
                }
            }
        },
        400: {
            'description': '2FA déjà configurée',
            'content': {
                'application/json': {
                    'example': {
                        'error': '2FA déjà configurée pour cet utilisateur'
                    }
                }
            }
        }
    }
)

# Schémas pour la vérification 2FA
verify_2fa_schema = extend_schema(
    operation_id='verify_2fa',
    summary='Vérifier le code 2FA',
    description='''
    Vérifie un code TOTP pour activer la 2FA.
    
    **Codes acceptés :**
    - Code TOTP de l'application d'authentification
    - Code de sauvegarde (backup code)
    ''',
    tags=['Authentication'],
    examples=[
        OpenApiExample(
            'Vérification 2FA',
            summary='Code TOTP',
            description='Vérification avec code TOTP',
            value={
                'code': '123456'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Vérification réussie',
            summary='2FA activée',
            description='2FA activée avec succès',
            value={
                'message': '2FA activée avec succès',
                'is_2fa_enabled': True
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'description': '2FA activée avec succès',
            'content': {
                'application/json': {
                    'example': {
                        'message': '2FA activée avec succès',
                        'is_2fa_enabled': True
                    }
                }
            }
        },
        400: {
            'description': 'Code invalide',
            'content': {
                'application/json': {
                    'example': {
                        'error': 'Code 2FA invalide'
                    }
                }
            }
        }
    }
)

