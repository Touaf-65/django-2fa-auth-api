# 🔐 Authentication App

## Vue d'ensemble

L'app **Authentication** fournit un système d'authentification complet avec support 2FA (Two-Factor Authentication) pour sécuriser l'accès aux APIs.

## 🚀 Fonctionnalités

### ✅ Authentification de base
- Inscription avec email et mot de passe
- Connexion avec validation des credentials
- Déconnexion sécurisée
- Réinitialisation de mot de passe

### ✅ 2FA (Two-Factor Authentication)
- **TOTP** (Time-based One-Time Password) avec Google Authenticator/Authy
- **Email OTP** (One-Time Password par email)
- Configuration flexible des méthodes 2FA
- Codes de récupération d'urgence

### ✅ JWT Tokens
- Access tokens (courte durée)
- Refresh tokens (longue durée)
- Rotation automatique des tokens
- Révocation des tokens

### ✅ Sécurité avancée
- Hachage sécurisé des mots de passe (bcrypt)
- Protection contre les attaques par force brute
- Validation des emails
- Gestion des sessions

## 📁 Structure

```
apps/authentication/
├── models/
│   ├── user.py                 # Modèle utilisateur étendu
│   ├── two_factor_auth.py      # Configuration 2FA
│   ├── email_otp.py           # Codes OTP par email
│   ├── password_reset.py      # Tokens de réinitialisation
│   └── email_verification.py  # Vérification d'email
├── serializers/
│   ├── auth_serializers.py    # Sérialiseurs d'authentification
│   └── user_serializers.py    # Sérialiseurs utilisateur
├── views/
│   └── auth_views.py          # Vues d'authentification
├── services/
│   ├── auth_service.py        # Service d'authentification
│   ├── two_factor_service.py  # Service 2FA
│   └── email_service.py       # Service email
├── utils/
│   ├── jwt_utils.py           # Utilitaires JWT
│   └── password_utils.py      # Utilitaires mot de passe
└── middleware/
    └── auth_middleware.py     # Middleware d'authentification
```

## 🔧 Configuration

### Variables d'environnement requises

```env
# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days
JWT_ALGORITHM=HS256

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_FROM_NAME=Your App Name

# 2FA Configuration
TOTP_ISSUER_NAME=YourApp
OTP_VALIDITY_PERIOD=300  # seconds (5 minutes)
OTP_LENGTH=6
BACKUP_CODES_COUNT=10

# Security
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SPECIAL_CHARS=True
```

### Installation des dépendances

```bash
pip install django-otp qrcode pillow
```

## 📡 APIs disponibles

### 🔐 Authentification de base

#### Inscription
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse:**
```json
{
  "message": "Utilisateur créé avec succès",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "email_verified": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Connexion
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Réponse:**
```json
{
  "message": "Connexion réussie",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "email_verified": true,
    "two_factor_enabled": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### Connexion avec 2FA
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "totp_code": "123456"
}
```

### 🔄 Gestion des tokens

#### Rafraîchir le token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Déconnexion
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 🔐 2FA (Two-Factor Authentication)

#### Configurer 2FA TOTP
```http
POST /api/auth/2fa/setup/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "secret": "JBSWY3DPEHPK3PXP",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344"
  ]
}
```

#### Vérifier 2FA TOTP
```http
POST /api/auth/2fa/verify/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "totp_code": "123456"
}
```

#### Désactiver 2FA
```http
DELETE /api/auth/2fa/disable/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "password": "securepassword123"
}
```

### 📧 Gestion des emails

#### Vérifier l'email
```http
POST /api/auth/email/verify/
Content-Type: application/json

{
  "token": "verification_token_here"
}
```

#### Renvoyer l'email de vérification
```http
POST /api/auth/email/resend-verification/
Authorization: Bearer <access_token>
```

### 🔑 Réinitialisation de mot de passe

#### Demander une réinitialisation
```http
POST /api/auth/password/reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Confirmer la réinitialisation
```http
POST /api/auth/password/reset/confirm/
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "newsecurepassword123"
}
```

## 🛠️ Utilisation dans le code

### Décorateurs d'authentification

```python
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.authentication.decorators import two_factor_required

@permission_classes([IsAuthenticated])
def protected_view(request):
    # Vue protégée par authentification
    return Response({"message": "Accès autorisé"})

@two_factor_required
def sensitive_view(request):
    # Vue nécessitant 2FA
    return Response({"message": "Accès avec 2FA"})
```

### Service d'authentification

```python
from apps.authentication.services import AuthService

auth_service = AuthService()

# Créer un utilisateur
user = auth_service.create_user(
    email="user@example.com",
    password="password123",
    first_name="John",
    last_name="Doe"
)

# Vérifier les credentials
is_valid = auth_service.verify_credentials(
    email="user@example.com",
    password="password123"
)

# Générer des tokens
tokens = auth_service.generate_tokens(user)
```

### Service 2FA

```python
from apps.authentication.services import TwoFactorService

two_factor_service = TwoFactorService()

# Configurer TOTP
setup_data = two_factor_service.setup_totp(user)

# Vérifier un code TOTP
is_valid = two_factor_service.verify_totp(user, "123456")

# Générer un code OTP par email
otp_code = two_factor_service.generate_email_otp(user)
```

## 🔒 Sécurité

### Bonnes pratiques implémentées

1. **Hachage sécurisé** : Utilisation de bcrypt pour les mots de passe
2. **Tokens JWT** : Signature et validation sécurisées
3. **Rate limiting** : Protection contre les attaques par force brute
4. **Validation d'email** : Vérification obligatoire des emails
5. **2FA** : Authentification à deux facteurs
6. **Audit trail** : Logs de toutes les actions d'authentification

### Configuration de sécurité recommandée

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.authentication

# Tests avec couverture
coverage run --source='apps.authentication' manage.py test apps.authentication
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.authentication.models import User
from apps.authentication.services import AuthService

class AuthServiceTestCase(TestCase):
    def setUp(self):
        self.auth_service = AuthService()
    
    def test_create_user(self):
        user = self.auth_service.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.email_verified)
    
    def test_verify_credentials(self):
        user = self.auth_service.create_user(
            email="test@example.com",
            password="password123"
        )
        
        # Credentials valides
        self.assertTrue(
            self.auth_service.verify_credentials(
                "test@example.com",
                "password123"
            )
        )
        
        # Credentials invalides
        self.assertFalse(
            self.auth_service.verify_credentials(
                "test@example.com",
                "wrongpassword"
            )
        )
```

## 📚 Ressources

- [Documentation Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)
- [JWT.io](https://jwt.io/) - Décodeur et documentation JWT
- [Google Authenticator](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)
- [Authy](https://authy.com/) - Alternative à Google Authenticator

## 🐛 Dépannage

### Problèmes courants

1. **Erreur JWT** : Vérifiez `JWT_SECRET_KEY` dans les settings
2. **Email non envoyé** : Vérifiez la configuration SMTP
3. **2FA ne fonctionne pas** : Vérifiez la synchronisation de l'heure
4. **Token expiré** : Utilisez le refresh token pour obtenir un nouveau token

### Logs utiles

```python
import logging

# Activer les logs d'authentification
logging.getLogger('apps.authentication').setLevel(logging.DEBUG)
```

---

*Dernière mise à jour: Septembre 2024*
