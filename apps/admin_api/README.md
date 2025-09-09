# ⚙️ Admin API App

## Vue d'ensemble

L'app **Admin API** fournit des APIs d'administration complètes pour la gestion du système, incluant la gestion des utilisateurs, des rôles, des permissions, des statistiques et des actions en lot.

## 🚀 Fonctionnalités

### ✅ Gestion des utilisateurs
- Création, modification, suppression d'utilisateurs
- Gestion des rôles et permissions
- Activation/désactivation des comptes
- Import/export d'utilisateurs

### ✅ Gestion des rôles et permissions
- Création et modification de rôles
- Attribution de permissions
- Gestion des groupes d'utilisateurs
- Audit des changements

### ✅ Statistiques d'administration
- Tableaux de bord d'administration
- Métriques système
- Rapports d'activité
- Analytics d'utilisation

### ✅ Actions en lot
- Opérations sur plusieurs utilisateurs
- Import/export de données
- Nettoyage de données
- Maintenance système

## 📁 Structure

```
apps/admin_api/
├── models/
│   ├── admin_action.py        # Actions d'administration
│   ├── system_config.py       # Configuration système
│   ├── admin_stats.py         # Statistiques admin
│   └── bulk_operation.py      # Opérations en lot
├── serializers/
│   ├── user_serializers.py    # Sérialiseurs utilisateurs
│   ├── role_serializers.py    # Sérialiseurs rôles
│   ├── stats_serializers.py   # Sérialiseurs statistiques
│   └── bulk_serializers.py    # Sérialiseurs opérations en lot
├── views/
│   ├── user_management_views.py # Vues gestion utilisateurs
│   ├── role_management_views.py # Vues gestion rôles
│   ├── stats_views.py         # Vues statistiques
│   └── bulk_operation_views.py # Vues opérations en lot
├── services/
│   ├── user_management_service.py # Service gestion utilisateurs
│   ├── role_management_service.py # Service gestion rôles
│   ├── stats_service.py       # Service statistiques
│   └── bulk_operation_service.py # Service opérations en lot
└── utils/
    ├── admin_utils.py         # Utilitaires admin
    └── bulk_utils.py          # Utilitaires opérations en lot
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration de l'admin API
ADMIN_API_ENABLED=true
ADMIN_API_RATE_LIMIT=1000  # requêtes par heure
ADMIN_API_AUDIT_ENABLED=true

# Configuration des opérations en lot
BULK_OPERATION_MAX_SIZE=10000
BULK_OPERATION_TIMEOUT=300  # 5 minutes
BULK_OPERATION_CHUNK_SIZE=100

# Configuration des statistiques
ADMIN_STATS_CACHE_TTL=300  # 5 minutes
ADMIN_STATS_RETENTION_DAYS=365

# Configuration des exports
EXPORT_MAX_SIZE=50000
EXPORT_FORMATS=csv,excel,json
EXPORT_STORAGE_PATH=/tmp/exports
```

### Permissions requises

```python
# Permissions nécessaires pour accéder à l'admin API
ADMIN_API_PERMISSIONS = [
    'admin_api.view_user',
    'admin_api.create_user',
    'admin_api.edit_user',
    'admin_api.delete_user',
    'admin_api.view_role',
    'admin_api.create_role',
    'admin_api.edit_role',
    'admin_api.delete_role',
    'admin_api.view_stats',
    'admin_api.bulk_operations'
]
```

## 📡 APIs disponibles

### 👥 Gestion des utilisateurs

#### Lister les utilisateurs
```http
GET /api/admin/users/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 123,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "date_joined": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T10:00:00Z",
      "roles": [
        {
          "id": 1,
          "name": "user",
          "description": "Utilisateur standard"
        }
      ],
      "profile": {
        "phone": "+1234567890",
        "location": "Paris, France"
      }
    }
  ]
}
```

#### Créer un utilisateur
```http
POST /api/admin/users/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "is_staff": false,
  "roles": [1, 2],
  "profile": {
    "phone": "+1234567890",
    "location": "New York, USA"
  }
}
```

#### Modifier un utilisateur
```http
PUT /api/admin/users/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "roles": [1, 2, 3]
}
```

#### Supprimer un utilisateur
```http
DELETE /api/admin/users/{id}/
Authorization: Bearer <access_token>
```

#### Activer/Désactiver un utilisateur
```http
PATCH /api/admin/users/{id}/toggle-status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_active": false,
  "reason": "Violation des conditions d'utilisation"
}
```

### 🔑 Gestion des rôles

#### Lister les rôles
```http
GET /api/admin/roles/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "admin",
      "description": "Administrateur système",
      "permissions": [
        {
          "id": 1,
          "name": "users.view_user",
          "codename": "view_user"
        },
        {
          "id": 2,
          "name": "users.create_user",
          "codename": "create_user"
        }
      ],
      "user_count": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer un rôle
```http
POST /api/admin/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "moderator",
  "description": "Modérateur du système",
  "permissions": [1, 2, 3, 4]
}
```

#### Modifier un rôle
```http
PUT /api/admin/roles/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "senior_moderator",
  "description": "Modérateur senior",
  "permissions": [1, 2, 3, 4, 5, 6]
}
```

#### Supprimer un rôle
```http
DELETE /api/admin/roles/{id}/
Authorization: Bearer <access_token>
```

### 📊 Statistiques d'administration

#### Récupérer les statistiques générales
```http
GET /api/admin/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "users": {
    "total": 1000,
    "active": 950,
    "inactive": 50,
    "new_today": 15,
    "new_this_week": 100,
    "new_this_month": 400
  },
  "roles": {
    "total": 10,
    "most_used": "user",
    "least_used": "guest"
  },
  "activity": {
    "logins_today": 500,
    "logins_this_week": 3500,
    "logins_this_month": 15000,
    "failed_logins_today": 25
  },
  "system": {
    "uptime": "30 days",
    "memory_usage": "75%",
    "disk_usage": "60%",
    "cpu_usage": "45%"
  },
  "security": {
    "blocked_ips": 25,
    "security_events_today": 10,
    "alerts_active": 3
  }
}
```

#### Récupérer les statistiques des utilisateurs
```http
GET /api/admin/stats/users/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "registration_trend": [
    {"date": "2024-01-01", "count": 15},
    {"date": "2024-01-02", "count": 20},
    {"date": "2024-01-03", "count": 18}
  ],
  "user_distribution": {
    "by_country": {
      "France": 400,
      "USA": 300,
      "Germany": 200,
      "UK": 100
    },
    "by_role": {
      "user": 800,
      "moderator": 150,
      "admin": 50
    }
  },
  "activity_metrics": {
    "average_session_duration": "25 minutes",
    "most_active_hour": 14,
    "most_active_day": "Tuesday"
  }
}
```

#### Récupérer les statistiques de sécurité
```http
GET /api/admin/stats/security/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "security_events": {
    "total": 1000,
    "by_type": {
      "failed_login": 500,
      "suspicious_activity": 300,
      "intrusion_attempt": 100,
      "data_breach": 100
    },
    "by_severity": {
      "low": 300,
      "medium": 400,
      "high": 250,
      "critical": 50
    }
  },
  "blocked_ips": {
    "total": 150,
    "active": 50,
    "auto_blocked": 100,
    "manually_blocked": 50
  },
  "alerts": {
    "total": 200,
    "active": 25,
    "resolved": 175
  }
}
```

### 🔄 Opérations en lot

#### Créer une opération en lot
```http
POST /api/admin/bulk-operations/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "operation_type": "update_users",
  "description": "Mise à jour des rôles utilisateur",
  "parameters": {
    "user_ids": [1, 2, 3, 4, 5],
    "action": "add_role",
    "role_id": 2
  }
}
```

#### Lister les opérations en lot
```http
GET /api/admin/bulk-operations/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "operation_type": "update_users",
      "description": "Mise à jour des rôles utilisateur",
      "status": "completed",
      "progress": 100,
      "total_items": 100,
      "processed_items": 100,
      "failed_items": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "started_at": "2024-01-01T00:01:00Z",
      "completed_at": "2024-01-01T00:05:00Z",
      "created_by": {
        "id": 1,
        "email": "admin@example.com"
      }
    }
  ]
}
```

#### Récupérer le statut d'une opération
```http
GET /api/admin/bulk-operations/{id}/
Authorization: Bearer <access_token>
```

#### Annuler une opération
```http
POST /api/admin/bulk-operations/{id}/cancel/
Authorization: Bearer <access_token>
```

### 📤 Import/Export

#### Exporter des utilisateurs
```http
POST /api/admin/export/users/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "format": "excel",
  "filters": {
    "is_active": true,
    "date_joined__gte": "2024-01-01"
  },
  "fields": ["id", "email", "first_name", "last_name", "date_joined"]
}
```

#### Importer des utilisateurs
```http
POST /api/admin/import/users/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: [fichier CSV/Excel]
```

**Réponse:**
```json
{
  "import_id": 1,
  "status": "processing",
  "total_rows": 100,
  "processed_rows": 0,
  "successful_rows": 0,
  "failed_rows": 0,
  "errors": []
}
```

## 🛠️ Utilisation dans le code

### Service de gestion des utilisateurs

```python
from apps.admin_api.services import UserManagementService

user_service = UserManagementService()

# Créer un utilisateur
user = user_service.create_user(
    email="newuser@example.com",
    password="securepassword123",
    first_name="Jane",
    last_name="Smith",
    roles=[1, 2]
)

# Modifier un utilisateur
updated_user = user_service.update_user(
    user_id=123,
    data={
        "first_name": "Jane",
        "last_name": "Smith",
        "is_active": True
    }
)

# Supprimer un utilisateur
user_service.delete_user(user_id=123)

# Activer/Désactiver un utilisateur
user_service.toggle_user_status(
    user_id=123,
    is_active=False,
    reason="Violation des conditions"
)
```

### Service de gestion des rôles

```python
from apps.admin_api.services import RoleManagementService

role_service = RoleManagementService()

# Créer un rôle
role = role_service.create_role(
    name="moderator",
    description="Modérateur du système",
    permissions=[1, 2, 3, 4]
)

# Modifier un rôle
updated_role = role_service.update_role(
    role_id=1,
    data={
        "name": "senior_moderator",
        "description": "Modérateur senior",
        "permissions": [1, 2, 3, 4, 5, 6]
    }
)

# Supprimer un rôle
role_service.delete_role(role_id=1)
```

### Service de statistiques

```python
from apps.admin_api.services import StatsService

stats_service = StatsService()

# Récupérer les statistiques générales
general_stats = stats_service.get_general_stats()

# Récupérer les statistiques des utilisateurs
user_stats = stats_service.get_user_stats()

# Récupérer les statistiques de sécurité
security_stats = stats_service.get_security_stats()

# Récupérer les tendances
trends = stats_service.get_trends(period="30d")
```

### Service d'opérations en lot

```python
from apps.admin_api.services import BulkOperationService

bulk_service = BulkOperationService()

# Créer une opération en lot
operation = bulk_service.create_operation(
    operation_type="update_users",
    description="Mise à jour des rôles",
    parameters={
        "user_ids": [1, 2, 3, 4, 5],
        "action": "add_role",
        "role_id": 2
    }
)

# Exécuter une opération
result = bulk_service.execute_operation(operation_id=1)

# Récupérer le statut
status = bulk_service.get_operation_status(operation_id=1)
```

### Décorateurs d'administration

```python
from apps.admin_api.decorators import admin_required, superuser_required

@admin_required
def admin_view(request):
    """Vue nécessitant des droits d'administration"""
    pass

@superuser_required
def superuser_view(request):
    """Vue nécessitant des droits de superutilisateur"""
    pass
```

## 🔧 Configuration avancée

### Configuration des opérations en lot

```python
# settings.py
BULK_OPERATIONS = {
    'update_users': {
        'max_items': 10000,
        'timeout': 300,
        'chunk_size': 100
    },
    'delete_users': {
        'max_items': 1000,
        'timeout': 600,
        'chunk_size': 50
    },
    'import_users': {
        'max_items': 50000,
        'timeout': 1800,
        'chunk_size': 200
    }
}
```

### Configuration des exports

```python
# Configuration des exports
EXPORT_CONFIG = {
    'users': {
        'max_size': 50000,
        'formats': ['csv', 'excel', 'json'],
        'fields': ['id', 'email', 'first_name', 'last_name', 'date_joined']
    },
    'roles': {
        'max_size': 1000,
        'formats': ['csv', 'excel', 'json'],
        'fields': ['id', 'name', 'description', 'permissions']
    }
}
```

### Configuration des statistiques

```python
# Configuration des statistiques
ADMIN_STATS_CONFIG = {
    'cache_ttl': 300,  # 5 minutes
    'retention_days': 365,
    'aggregation_intervals': ['hourly', 'daily', 'weekly', 'monthly'],
    'metrics': [
        'user_registrations',
        'user_logins',
        'failed_logins',
        'security_events',
        'system_performance'
    ]
}
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.admin_api

# Tests avec couverture
coverage run --source='apps.admin_api' manage.py test apps.admin_api
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.admin_api.services import UserManagementService, RoleManagementService

User = get_user_model()

class AdminAPIServiceTestCase(TestCase):
    def setUp(self):
        self.user_service = UserManagementService()
        self.role_service = RoleManagementService()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )
    
    def test_create_user(self):
        user = self.user_service.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
    
    def test_create_role(self):
        role = self.role_service.create_role(
            name='test_role',
            description='Test role',
            permissions=[1, 2, 3]
        )
        
        self.assertEqual(role.name, 'test_role')
        self.assertEqual(role.description, 'Test role')
        self.assertEqual(role.permissions.count(), 3)
    
    def test_bulk_operation(self):
        from apps.admin_api.services import BulkOperationService
        
        bulk_service = BulkOperationService()
        
        operation = bulk_service.create_operation(
            operation_type='update_users',
            description='Test operation',
            parameters={'user_ids': [1, 2, 3]}
        )
        
        self.assertEqual(operation.operation_type, 'update_users')
        self.assertEqual(operation.status, 'pending')
```

## 📊 Intégration avec d'autres apps

### Intégration avec l'app Permissions

```python
# Vérification des permissions pour les actions d'administration
from apps.permissions.decorators import permission_required

@permission_required('admin_api.create_user')
def create_user_admin(request):
    """Création d'utilisateur avec vérification des permissions"""
    pass
```

### Intégration avec l'app Security

```python
# Audit des actions d'administration
from apps.security.services import AuditService

audit_service = AuditService()

def admin_action_with_audit(request, action, resource_id):
    # Enregistrer l'action d'administration
    audit_service.log_action(
        action=action,
        user=request.user,
        resource="admin_api",
        resource_id=resource_id,
        metadata={"admin_action": True}
    )
```

## 🐛 Dépannage

### Problèmes courants

1. **Permission refusée** : Vérifiez les permissions de l'utilisateur
2. **Opération en lot échouée** : Vérifiez la taille et la configuration
3. **Export échoué** : Vérifiez la taille des données et les limites
4. **Performance lente** : Optimisez les requêtes et activez le cache

### Configuration de debug

```python
# settings.py
DEBUG_ADMIN_API = True
ADMIN_API_LOG_LEVEL = 'DEBUG'
BULK_OPERATION_DEBUG = True
```

## 📚 Ressources

- [Django Admin](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions)
- [Django Bulk Operations](https://docs.djangoproject.com/en/stable/topics/db/queries/#bulk-operations)

---

*Dernière mise à jour: Septembre 2024*
