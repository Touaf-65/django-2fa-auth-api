# 🔑 Permissions App

## Vue d'ensemble

L'app **Permissions** fournit un système de permissions avancé avec support RBAC (Role-Based Access Control) et ABAC (Attribute-Based Access Control), incluant la délégation de permissions et l'audit complet.

## 🚀 Fonctionnalités

### ✅ RBAC (Role-Based Access Control)
- Rôles hiérarchiques avec permissions
- Attribution de rôles aux utilisateurs
- Gestion des groupes d'utilisateurs
- Permissions granulaires

### ✅ ABAC (Attribute-Based Access Control)
- Permissions basées sur les attributs
- Conditions dynamiques
- Contexte d'accès avancé
- Évaluation en temps réel

### ✅ Délégation de permissions
- Délégation temporaire de permissions
- Délégation avec expiration
- Audit des délégations
- Révocation des délégations

### ✅ Audit et monitoring
- Logs complets des accès
- Traçabilité des actions
- Rapports de sécurité
- Alertes de permissions

## 📁 Structure

```
apps/permissions/
├── models/
│   ├── permission.py          # Permissions
│   ├── role.py               # Rôles
│   ├── group.py              # Groupes
│   ├── user_role.py          # Rôles utilisateur
│   ├── permission_delegation.py # Délégation
│   └── permission_audit.py   # Audit
├── serializers/
│   ├── permission_serializers.py # Sérialiseurs permissions
│   ├── role_serializers.py      # Sérialiseurs rôles
│   ├── group_serializers.py     # Sérialiseurs groupes
│   └── delegation_serializers.py # Sérialiseurs délégation
├── views/
│   ├── permission_views.py      # Vues permissions
│   ├── role_views.py           # Vues rôles
│   ├── group_views.py          # Vues groupes
│   ├── user_role_views.py      # Vues rôles utilisateur
│   ├── delegation_views.py     # Vues délégation
│   └── permission_manager_views.py # Vues gestionnaire
├── services/
│   ├── permission_service.py   # Service permissions
│   ├── role_service.py        # Service rôles
│   └── delegation_service.py  # Service délégation
├── utils/
│   ├── permission_checker.py  # Vérificateur permissions
│   └── permission_utils.py    # Utilitaires
├── middleware/
│   ├── permission_middleware.py # Middleware permissions
│   └── audit_middleware.py    # Middleware audit
└── decorators/
    ├── permission_decorators.py # Décorateurs permissions
    └── audit_decorators.py     # Décorateurs audit
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration des permissions
PERMISSIONS_ENABLED=true
PERMISSION_CACHE_TTL=300  # 5 minutes
AUDIT_ENABLED=true
DELEGATION_ENABLED=true

# Configuration de l'audit
AUDIT_RETENTION_DAYS=365
AUDIT_LOG_LEVEL=INFO
AUDIT_SENSITIVE_ACTIONS=true
```

### Middleware requis

```python
# settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.permissions.middleware.permission_middleware.PermissionMiddleware',
    'apps.permissions.middleware.audit_middleware.AuditMiddleware',
]
```

## 📡 APIs disponibles

### 🔑 Gestion des permissions

#### Lister les permissions
```http
GET /api/permissions/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "name": "users.view_user",
      "codename": "view_user",
      "content_type": "user",
      "description": "Peut voir les utilisateurs",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "users.create_user",
      "codename": "create_user",
      "content_type": "user",
      "description": "Peut créer des utilisateurs",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer une permission
```http
POST /api/permissions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "users.edit_user",
  "codename": "edit_user",
  "content_type": "user",
  "description": "Peut modifier les utilisateurs"
}
```

### 👥 Gestion des rôles

#### Lister les rôles
```http
GET /api/permissions/roles/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 5,
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
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer un rôle
```http
POST /api/permissions/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "moderator",
  "description": "Modérateur du système",
  "permissions": [1, 2, 3]
}
```

#### Assigner un rôle à un utilisateur
```http
POST /api/permissions/user-roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user": 123,
  "role": 2,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

### 👥 Gestion des groupes

#### Lister les groupes
```http
GET /api/permissions/groups/
Authorization: Bearer <access_token>
```

#### Créer un groupe
```http
POST /api/permissions/groups/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "developers",
  "description": "Équipe de développement",
  "users": [123, 124, 125],
  "roles": [2, 3]
}
```

### 🔄 Délégation de permissions

#### Déléguer une permission
```http
POST /api/permissions/delegate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user": 123,
  "permission": "users.create_user",
  "expires_at": "2024-12-31T23:59:59Z",
  "reason": "Formation temporaire"
}
```

#### Révoker une délégation
```http
DELETE /api/permissions/delegate/{id}/
Authorization: Bearer <access_token>
```

### 📊 Audit et statistiques

#### Récupérer l'audit des permissions
```http
GET /api/permissions/audit/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 123,
        "email": "user@example.com"
      },
      "action": "permission_granted",
      "permission": "users.create_user",
      "resource": "user",
      "timestamp": "2024-01-01T10:00:00Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "success": true
    }
  ]
}
```

#### Statistiques des permissions
```http
GET /api/permissions/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "total_permissions": 25,
  "total_roles": 5,
  "total_groups": 3,
  "active_delegations": 12,
  "permissions_by_type": {
    "users": 8,
    "content": 10,
    "admin": 7
  },
  "recent_activities": [
    {
      "action": "role_assigned",
      "count": 5,
      "date": "2024-01-01"
    }
  ]
}
```

## 🛠️ Utilisation dans le code

### Décorateurs de permissions

```python
from apps.permissions.decorators import permission_required, audit_required

@permission_required('users.view_user')
def view_user(request, user_id):
    """Vue protégée par permission"""
    user = get_object_or_404(User, id=user_id)
    return Response(UserSerializer(user).data)

@permission_required('users.create_user', audit=True)
def create_user(request):
    """Vue avec audit automatique"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)
    return Response(serializer.errors, status=400)

@audit_required('users.delete_user')
def delete_user(request, user_id):
    """Vue avec audit obligatoire"""
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response(status=204)
```

### Vérification de permissions dans les vues

```python
from apps.permissions.utils import check_permission

def custom_view(request):
    # Vérifier une permission
    if not check_permission(request.user, 'users.view_user'):
        return Response(
            {'error': 'Permission refusée'},
            status=403
        )
    
    # Vérifier une permission avec contexte
    if not check_permission(
        request.user, 
        'users.edit_user',
        context={'user_id': request.data.get('user_id')}
    ):
        return Response(
            {'error': 'Permission refusée pour cet utilisateur'},
            status=403
        )
    
    return Response({'message': 'Accès autorisé'})
```

### Service de permissions

```python
from apps.permissions.services import PermissionService

permission_service = PermissionService()

# Vérifier une permission
has_permission = permission_service.user_has_permission(
    user=request.user,
    permission='users.create_user'
)

# Obtenir les permissions d'un utilisateur
permissions = permission_service.get_user_permissions(user)

# Obtenir les rôles d'un utilisateur
roles = permission_service.get_user_roles(user)

# Déléguer une permission
delegation = permission_service.delegate_permission(
    user=target_user,
    permission='users.create_user',
    delegated_by=request.user,
    expires_at=datetime.now() + timedelta(days=7)
)
```

### Service de rôles

```python
from apps.permissions.services import RoleService

role_service = RoleService()

# Créer un rôle
role = role_service.create_role(
    name='moderator',
    description='Modérateur',
    permissions=['users.view_user', 'users.edit_user']
)

# Assigner un rôle
role_service.assign_role(user, role)

# Révoker un rôle
role_service.revoke_role(user, role)
```

### Middleware de permissions

```python
# Le middleware vérifie automatiquement les permissions
# selon les décorateurs appliqués aux vues

# Dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.permissions.middleware.permission_middleware.PermissionMiddleware',
    'apps.permissions.middleware.audit_middleware.AuditMiddleware',
]
```

## 🔒 Sécurité et bonnes pratiques

### Hiérarchie des rôles recommandée

```python
# Structure de rôles typique
ROLES_HIERARCHY = {
    'super_admin': {
        'permissions': ['*'],  # Toutes les permissions
        'description': 'Super administrateur'
    },
    'admin': {
        'permissions': [
            'users.*',
            'content.*',
            'settings.view_settings'
        ],
        'description': 'Administrateur'
    },
    'moderator': {
        'permissions': [
            'users.view_user',
            'users.edit_user',
            'content.view_content',
            'content.edit_content'
        ],
        'description': 'Modérateur'
    },
    'user': {
        'permissions': [
            'users.view_own_profile',
            'users.edit_own_profile'
        ],
        'description': 'Utilisateur standard'
    }
}
```

### Permissions granulaires

```python
# Exemples de permissions granulaires
PERMISSIONS = [
    # Utilisateurs
    'users.view_user',
    'users.create_user',
    'users.edit_user',
    'users.delete_user',
    'users.view_own_profile',
    'users.edit_own_profile',
    
    # Contenu
    'content.view_content',
    'content.create_content',
    'content.edit_content',
    'content.delete_content',
    'content.publish_content',
    
    # Administration
    'admin.view_dashboard',
    'admin.manage_users',
    'admin.manage_settings',
    'admin.view_logs',
]
```

### Audit des actions sensibles

```python
from apps.permissions.decorators import audit_sensitive

@audit_sensitive('user_deletion')
def delete_user(request, user_id):
    """Suppression d'utilisateur avec audit sensible"""
    user = get_object_or_404(User, id=user_id)
    
    # Log automatique de l'action sensible
    user.delete()
    
    return Response(status=204)
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.permissions

# Tests avec couverture
coverage run --source='apps.permissions' manage.py test apps.permissions
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.permissions.models import Role, Permission
from apps.permissions.services import PermissionService

User = get_user_model()

class PermissionServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.permission = Permission.objects.create(
            name='users.view_user',
            codename='view_user',
            content_type='user'
        )
        self.role = Role.objects.create(
            name='viewer',
            description='Peut voir les utilisateurs'
        )
        self.role.permissions.add(self.permission)
        self.service = PermissionService()
    
    def test_user_has_permission(self):
        # Sans rôle
        self.assertFalse(
            self.service.user_has_permission(
                self.user, 'users.view_user'
            )
        )
        
        # Avec rôle
        self.user.roles.add(self.role)
        self.assertTrue(
            self.service.user_has_permission(
                self.user, 'users.view_user'
            )
        )
    
    def test_delegate_permission(self):
        delegation = self.service.delegate_permission(
            user=self.user,
            permission='users.create_user',
            delegated_by=self.user
        )
        
        self.assertEqual(delegation.user, self.user)
        self.assertEqual(delegation.permission, 'users.create_user')
        self.assertTrue(delegation.is_active)
```

## 📊 Monitoring et analytics

### Métriques disponibles

```python
from apps.permissions.models import PermissionAudit

# Statistiques des permissions
stats = {
    'total_permissions': Permission.objects.count(),
    'total_roles': Role.objects.count(),
    'active_delegations': PermissionDelegation.objects.filter(is_active=True).count(),
    'failed_permission_checks': PermissionAudit.objects.filter(success=False).count(),
    'permissions_by_type': Permission.objects.values('content_type').annotate(count=Count('id')),
}
```

### Logs d'audit

```python
import logging

# Activer les logs d'audit
logging.getLogger('apps.permissions.audit').setLevel(logging.INFO)

# Les logs incluent:
# - Tentatives d'accès
# - Délégations de permissions
# - Modifications de rôles
# - Échecs d'authentification
```

## 🐛 Dépannage

### Problèmes courants

1. **Permission refusée** : Vérifiez les rôles de l'utilisateur
2. **Délégation expirée** : Vérifiez les dates d'expiration
3. **Audit non fonctionnel** : Vérifiez la configuration du middleware
4. **Performance lente** : Activez le cache des permissions

### Configuration de debug

```python
# settings.py
DEBUG_PERMISSIONS = True
PERMISSION_CACHE_DEBUG = True
AUDIT_DEBUG = True
```

## 📚 Ressources

- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions)
- [RBAC vs ABAC](https://en.wikipedia.org/wiki/Role-based_access_control)
- [OWASP Access Control](https://owasp.org/www-community/controls/Access_Control)

---

*Dernière mise à jour: Septembre 2024*