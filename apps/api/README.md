# 🌐 API App

## Vue d'ensemble

L'app **API** fournit la gestion des APIs et de leur documentation, incluant le versioning, le rate limiting, le monitoring et la gestion des clés API.

## 🚀 Fonctionnalités

### ✅ Gestion des APIs
- Documentation API automatique
- Versioning des APIs
- Gestion des endpoints
- Métadonnées des APIs

### ✅ Gestion des clés API
- Génération de clés API
- Gestion des permissions par clé
- Rotation des clés
- Révocation des clés

### ✅ Rate limiting
- Limitation par clé API
- Limitation par utilisateur
- Limitation par endpoint
- Configuration flexible

### ✅ Monitoring des APIs
- Métriques d'utilisation
- Analytics des APIs
- Logs d'accès
- Performance monitoring

## 📁 Structure

```
apps/api/
├── models/
│   ├── api_key.py            # Clés API
│   ├── api_version.py        # Versions d'API
│   ├── api_usage.py          # Utilisation des APIs
│   ├── api_documentation.py  # Documentation
│   └── api_analytics.py      # Analytics
├── serializers/
│   ├── api_key_serializers.py # Sérialiseurs clés API
│   ├── api_version_serializers.py # Sérialiseurs versions
│   ├── api_usage_serializers.py # Sérialiseurs utilisation
│   └── api_analytics_serializers.py # Sérialiseurs analytics
├── views/
│   ├── api_key_views.py      # Vues clés API
│   ├── api_version_views.py  # Vues versions
│   ├── api_usage_views.py    # Vues utilisation
│   └── api_analytics_views.py # Vues analytics
├── services/
│   ├── api_key_service.py    # Service clés API
│   ├── api_version_service.py # Service versions
│   ├── api_usage_service.py  # Service utilisation
│   └── api_analytics_service.py # Service analytics
├── middleware/
│   └── api_middleware.py     # Middleware API
└── utils/
    ├── api_utils.py          # Utilitaires API
    └── rate_limit_utils.py   # Utilitaires rate limiting
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration de l'API
API_ENABLED=true
API_VERSIONING_ENABLED=true
API_DOCUMENTATION_ENABLED=true

# Configuration des clés API
API_KEY_LENGTH=32
API_KEY_PREFIX=ak_
API_KEY_EXPIRY_DAYS=365
API_KEY_ROTATION_ENABLED=true

# Configuration du rate limiting
API_RATE_LIMIT_ENABLED=true
API_RATE_LIMIT_PER_KEY=1000  # requêtes par heure
API_RATE_LIMIT_PER_USER=5000  # requêtes par heure
API_RATE_LIMIT_BURST=100  # requêtes par minute

# Configuration du monitoring
API_MONITORING_ENABLED=true
API_ANALYTICS_RETENTION_DAYS=90
API_LOGS_RETENTION_DAYS=30
```

### Middleware requis

```python
# settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.api.middleware.api_middleware.APIMiddleware',
]
```

## 📡 APIs disponibles

### 🔑 Gestion des clés API

#### Lister les clés API
```http
GET /api/api/keys/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Mobile App Key",
      "key": "ak_1234567890abcdef1234567890abcdef",
      "description": "Clé API pour l'application mobile",
      "permissions": ["read", "write"],
      "rate_limit": 1000,
      "is_active": true,
      "expires_at": "2024-12-31T23:59:59Z",
      "last_used": "2024-01-01T10:00:00Z",
      "usage_count": 1500,
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": {
        "id": 123,
        "email": "user@example.com"
      }
    }
  ]
}
```

#### Créer une clé API
```http
POST /api/api/keys/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Web App Key",
  "description": "Clé API pour l'application web",
  "permissions": ["read", "write", "admin"],
  "rate_limit": 2000,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Modifier une clé API
```http
PUT /api/api/keys/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Web App Key",
  "description": "Clé API mise à jour",
  "permissions": ["read", "write"],
  "rate_limit": 1500,
  "is_active": true
}
```

#### Supprimer une clé API
```http
DELETE /api/api/keys/{id}/
Authorization: Bearer <access_token>
```

#### Régénérer une clé API
```http
POST /api/api/keys/{id}/regenerate/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "id": 1,
  "name": "Mobile App Key",
  "key": "ak_new1234567890abcdef1234567890abcdef",
  "description": "Clé API régénérée",
  "permissions": ["read", "write"],
  "rate_limit": 1000,
  "is_active": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T00:00:00Z",
  "regenerated_at": "2024-01-01T10:00:00Z"
}
```

### 📚 Gestion des versions d'API

#### Lister les versions d'API
```http
GET /api/api/versions/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "version": "v1",
      "is_current": true,
      "is_deprecated": false,
      "deprecation_date": null,
      "sunset_date": null,
      "description": "Version 1 de l'API",
      "changelog": "Première version de l'API",
      "endpoints": [
        {
          "path": "/api/v1/users/",
          "method": "GET",
          "description": "Lister les utilisateurs"
        },
        {
          "path": "/api/v1/users/",
          "method": "POST",
          "description": "Créer un utilisateur"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer une version d'API
```http
POST /api/api/versions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "version": "v2",
  "description": "Version 2 de l'API avec de nouvelles fonctionnalités",
  "changelog": "Ajout de nouvelles fonctionnalités et améliorations"
}
```

#### Marquer une version comme dépréciée
```http
PATCH /api/api/versions/{id}/deprecate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "deprecation_date": "2024-06-01T00:00:00Z",
  "sunset_date": "2024-12-31T23:59:59Z",
  "deprecation_message": "Cette version sera supprimée le 31 décembre 2024"
}
```

### 📊 Monitoring et analytics

#### Récupérer les statistiques d'utilisation
```http
GET /api/api/usage/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "total_requests": 100000,
  "requests_today": 5000,
  "requests_this_week": 35000,
  "requests_this_month": 150000,
  "unique_api_keys": 50,
  "unique_users": 200,
  "top_endpoints": [
    {
      "endpoint": "/api/v1/users/",
      "method": "GET",
      "request_count": 25000,
      "average_response_time": 150
    },
    {
      "endpoint": "/api/v1/auth/login/",
      "method": "POST",
      "request_count": 15000,
      "average_response_time": 200
    }
  ],
  "requests_by_hour": [
    {"hour": 9, "count": 500},
    {"hour": 10, "count": 800},
    {"hour": 11, "count": 1200}
  ],
  "requests_by_day": [
    {"date": "2024-01-01", "count": 5000},
    {"date": "2024-01-02", "count": 5500},
    {"date": "2024-01-03", "count": 4800}
  ]
}
```

#### Récupérer les analytics d'une clé API
```http
GET /api/api/keys/{id}/analytics/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "api_key": {
    "id": 1,
    "name": "Mobile App Key",
    "key": "ak_1234567890abcdef1234567890abcdef"
  },
  "usage_stats": {
    "total_requests": 15000,
    "requests_today": 500,
    "requests_this_week": 3500,
    "requests_this_month": 15000,
    "last_used": "2024-01-01T10:00:00Z",
    "average_requests_per_day": 500
  },
  "endpoint_usage": [
    {
      "endpoint": "/api/v1/users/",
      "method": "GET",
      "request_count": 8000,
      "average_response_time": 150
    },
    {
      "endpoint": "/api/v1/auth/login/",
      "method": "POST",
      "request_count": 2000,
      "average_response_time": 200
    }
  ],
  "error_stats": {
    "total_errors": 150,
    "error_rate": 1.0,
    "errors_by_type": {
      "400": 50,
      "401": 30,
      "403": 20,
      "500": 50
    }
  }
}
```

#### Récupérer les logs d'accès
```http
GET /api/api/logs/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "api_key": {
        "id": 1,
        "name": "Mobile App Key"
      },
      "endpoint": "/api/v1/users/",
      "method": "GET",
      "status_code": 200,
      "response_time": 150,
      "ip_address": "192.168.1.100",
      "user_agent": "MobileApp/1.0",
      "timestamp": "2024-01-01T10:00:00Z",
      "request_size": 1024,
      "response_size": 2048
    }
  ]
}
```

### 📖 Documentation de l'API

#### Récupérer la documentation
```http
GET /api/api/documentation/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "title": "Django 2FA Auth API",
  "version": "v1",
  "description": "API complète pour l'authentification et la gestion des utilisateurs",
  "base_url": "https://api.example.com",
  "authentication": {
    "type": "Bearer Token",
    "description": "Utilisez votre token d'accès dans l'en-tête Authorization"
  },
  "endpoints": [
    {
      "path": "/api/v1/auth/login/",
      "method": "POST",
      "description": "Connexion utilisateur",
      "parameters": [
        {
          "name": "email",
          "type": "string",
          "required": true,
          "description": "Email de l'utilisateur"
        },
        {
          "name": "password",
          "type": "string",
          "required": true,
          "description": "Mot de passe de l'utilisateur"
        }
      ],
      "responses": {
        "200": {
          "description": "Connexion réussie",
          "schema": {
            "type": "object",
            "properties": {
              "access_token": {"type": "string"},
              "refresh_token": {"type": "string"},
              "user": {"type": "object"}
            }
          }
        },
        "401": {
          "description": "Identifiants invalides"
        }
      }
    }
  ]
}
```

## 🛠️ Utilisation dans le code

### Service de clés API

```python
from apps.api.services import APIKeyService

api_key_service = APIKeyService()

# Créer une clé API
api_key = api_key_service.create_key(
    name="Mobile App Key",
    description="Clé pour l'application mobile",
    permissions=["read", "write"],
    rate_limit=1000,
    expires_at=datetime.now() + timedelta(days=365)
)

# Vérifier une clé API
is_valid = api_key_service.validate_key("ak_1234567890abcdef1234567890abcdef")

# Récupérer les informations d'une clé
key_info = api_key_service.get_key_info("ak_1234567890abcdef1234567890abcdef")

# Régénérer une clé
new_key = api_key_service.regenerate_key(key_id=1)
```

### Service de versioning

```python
from apps.api.services import APIVersionService

version_service = APIVersionService()

# Créer une version
version = version_service.create_version(
    version="v2",
    description="Version 2 avec nouvelles fonctionnalités",
    changelog="Ajout de nouvelles fonctionnalités"
)

# Marquer comme dépréciée
version_service.deprecate_version(
    version_id=1,
    deprecation_date=datetime.now() + timedelta(days=180),
    sunset_date=datetime.now() + timedelta(days=365)
)
```

### Service d'analytics

```python
from apps.api.services import APIAnalyticsService

analytics_service = APIAnalyticsService()

# Enregistrer une requête
analytics_service.record_request(
    api_key="ak_1234567890abcdef1234567890abcdef",
    endpoint="/api/v1/users/",
    method="GET",
    status_code=200,
    response_time=150,
    ip_address="192.168.1.100"
)

# Récupérer les statistiques
stats = analytics_service.get_usage_stats(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Récupérer les analytics d'une clé
key_analytics = analytics_service.get_key_analytics(
    key_id=1,
    period="30d"
)
```

### Middleware API

```python
# Le middleware gère automatiquement:
# - La validation des clés API
# - Le rate limiting
# - L'enregistrement des requêtes
# - La gestion des versions

# Dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.api.middleware.api_middleware.APIMiddleware',
]
```

### Décorateurs API

```python
from apps.api.decorators import api_key_required, rate_limit

@api_key_required(permissions=['read'])
@rate_limit(requests_per_hour=1000)
def api_view(request):
    """Vue API avec authentification par clé et rate limiting"""
    pass
```

## 🔧 Configuration avancée

### Configuration des clés API

```python
# settings.py
API_KEY_CONFIG = {
    'LENGTH': 32,
    'PREFIX': 'ak_',
    'ALPHABET': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    'EXPIRY_DAYS': 365,
    'ROTATION_ENABLED': True,
    'ROTATION_DAYS': 90
}
```

### Configuration du rate limiting

```python
# Configuration du rate limiting par clé API
API_RATE_LIMITS = {
    'default': {
        'requests_per_hour': 1000,
        'requests_per_minute': 100,
        'burst_limit': 10
    },
    'premium': {
        'requests_per_hour': 10000,
        'requests_per_minute': 1000,
        'burst_limit': 100
    },
    'enterprise': {
        'requests_per_hour': 100000,
        'requests_per_minute': 10000,
        'burst_limit': 1000
    }
}
```

### Configuration du monitoring

```python
# Configuration du monitoring des APIs
API_MONITORING_CONFIG = {
    'ENABLED': True,
    'LOG_LEVEL': 'INFO',
    'RETENTION_DAYS': 90,
    'METRICS_INTERVAL': 300,  # 5 minutes
    'ALERT_THRESHOLDS': {
        'error_rate': 5.0,  # 5%
        'response_time': 1000,  # 1 seconde
        'request_volume': 10000  # requêtes par heure
    }
}
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.api

# Tests avec couverture
coverage run --source='apps.api' manage.py test apps.api
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.api.services import APIKeyService, APIAnalyticsService

class APIServiceTestCase(TestCase):
    def setUp(self):
        self.api_key_service = APIKeyService()
        self.analytics_service = APIAnalyticsService()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
    
    def test_create_api_key(self):
        api_key = self.api_key_service.create_key(
            name="Test Key",
            description="Test description",
            permissions=["read", "write"],
            rate_limit=1000,
            created_by=self.user
        )
        
        self.assertEqual(api_key.name, "Test Key")
        self.assertEqual(api_key.permissions, ["read", "write"])
        self.assertEqual(api_key.rate_limit, 1000)
        self.assertTrue(api_key.is_active)
    
    def test_validate_api_key(self):
        api_key = self.api_key_service.create_key(
            name="Test Key",
            description="Test description",
            permissions=["read"],
            rate_limit=1000,
            created_by=self.user
        )
        
        # Test avec une clé valide
        is_valid = self.api_key_service.validate_key(api_key.key)
        self.assertTrue(is_valid)
        
        # Test avec une clé invalide
        is_valid = self.api_key_service.validate_key("invalid_key")
        self.assertFalse(is_valid)
    
    def test_record_request(self):
        api_key = self.api_key_service.create_key(
            name="Test Key",
            description="Test description",
            permissions=["read"],
            rate_limit=1000,
            created_by=self.user
        )
        
        self.analytics_service.record_request(
            api_key=api_key.key,
            endpoint="/api/v1/users/",
            method="GET",
            status_code=200,
            response_time=150,
            ip_address="192.168.1.100"
        )
        
        # Vérifier que la requête a été enregistrée
        usage = self.analytics_service.get_key_usage(api_key.id)
        self.assertEqual(usage['total_requests'], 1)
```

## 📊 Intégration avec d'autres apps

### Intégration avec l'app Authentication

```python
# Authentification par clé API
from apps.api.middleware import APIKeyAuthentication

class APIKeyAuthenticationMiddleware:
    def process_request(self, request):
        api_key = request.META.get('HTTP_AUTHORIZATION', '').replace('ApiKey ', '')
        if api_key:
            # Valider la clé API
            key_info = api_key_service.validate_key(api_key)
            if key_info:
                request.api_key = key_info
                request.user = key_info.user
```

### Intégration avec l'app Monitoring

```python
# Monitoring des APIs
from apps.monitoring.services import MetricsService

metrics_service = MetricsService()

def record_api_metrics(api_key, endpoint, method, status_code, response_time):
    # Enregistrer les métriques
    metrics_service.increment_counter(
        name='api_requests',
        labels={
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code
        }
    )
    
    metrics_service.record_histogram(
        name='api_response_time',
        value=response_time,
        labels={
            'endpoint': endpoint,
            'method': method
        }
    )
```

## 🐛 Dépannage

### Problèmes courants

1. **Clé API invalide** : Vérifiez la format et l'expiration
2. **Rate limit dépassé** : Vérifiez les limites configurées
3. **Version dépréciée** : Vérifiez les dates de dépréciation
4. **Performance lente** : Optimisez les requêtes et activez le cache

### Configuration de debug

```python
# settings.py
DEBUG_API = True
API_LOG_LEVEL = 'DEBUG'
API_RATE_LIMITING_DEBUG = True
```

## 📚 Ressources

- [Django REST Framework](https://www.django-rest-framework.org/)
- [API Versioning](https://en.wikipedia.org/wiki/API_versioning)
- [Rate Limiting](https://en.wikipedia.org/wiki/Rate_limiting)
- [API Documentation](https://swagger.io/specification/)

---

*Dernière mise à jour: Septembre 2024*
