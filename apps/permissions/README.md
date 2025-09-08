# 🛡️ App Permissions - Système de Gestion des Permissions Avancé

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Modèles](#modèles)
- [API Endpoints](#api-endpoints)
- [Middleware](#middleware)
- [Décorateurs](#décorateurs)
- [Utilitaires](#utilitaires)
- [Exemples d'utilisation](#exemples-dutilisation)
- [Configuration](#configuration)
- [Tests](#tests)

## 🎯 Vue d'ensemble

L'app `permissions` fournit un système de gestion des permissions avancé et granulaire pour Django, incluant :

- **Permissions granulaires** avec contraintes de valeur et conditions
- **Rôles dynamiques** avec assignation flexible
- **Groupes d'utilisateurs** avec gestion des membres
- **Délégations temporaires** de permissions et rôles
- **Permissions conditionnelles** basées sur le contexte
- **Gestionnaires de permissions** avec droits spécifiques
- **Audit complet** de tous les accès
- **Middleware automatique** pour la vérification des permissions

## 🏗️ Architecture

```
apps/permissions/
├── models/                 # Modèles de données
│   ├── permission.py       # Permission, ConditionalPermission
│   ├── role.py            # Role, RolePermission
│   ├── group.py           # Group, GroupMembership, GroupRole
│   ├── user_role.py       # UserRole
│   ├── delegation.py      # PermissionDelegation, RoleDelegation
│   └── permission_manager.py # PermissionManager
├── serializers/           # Serializers DRF
│   ├── permission_serializers.py
│   ├── role_serializers.py
│   ├── group_serializers.py
│   ├── user_role_serializers.py
│   ├── delegation_serializers.py
│   └── permission_manager_serializers.py
├── views/                 # Vues API
│   ├── permission_views.py
│   ├── role_views.py
│   ├── group_views.py
│   ├── user_role_views.py
│   ├── delegation_views.py
│   └── permission_manager_views.py
├── middleware/            # Middleware de sécurité
│   ├── permission_middleware.py
│   ├── delegation_middleware.py
│   └── audit_middleware.py
├── utils/                 # Utilitaires
│   ├── permission_checker.py
│   ├── delegation_utils.py
│   └── permission_helpers.py
├── decorators.py          # Décorateurs pour les vues
├── urls.py               # Configuration des URLs
└── README.md             # Cette documentation
```

## 📊 Modèles

### 🔐 Permission
Modèle principal pour les permissions granulaires.

**Champs :**
- `name` - Nom de la permission
- `codename` - Code unique de la permission
- `description` - Description détaillée
- `app_label` - Application concernée
- `model` - Modèle concerné
- `action` - Action (view, add, change, delete)
- `field_name` - Champ spécifique (optionnel)
- `min_value` / `max_value` - Contraintes de valeur
- `conditions` - Conditions JSON
- `is_custom` - Permission personnalisée
- `is_active` - Statut actif

### 👑 Role
Rôles avec permissions assignées.

**Champs :**
- `name` - Nom du rôle
- `description` - Description
- `permissions` - Permissions assignées (ManyToMany)
- `is_system` - Rôle système
- `is_active` - Statut actif

### 👥 Group
Groupes d'utilisateurs avec rôles.

**Champs :**
- `name` - Nom du groupe
- `description` - Description
- `users` - Utilisateurs membres (ManyToMany)
- `roles` - Rôles assignés (ManyToMany)
- `is_active` - Statut actif

### 🔗 UserRole
Assignation de rôles aux utilisateurs.

**Champs :**
- `user` - Utilisateur
- `role` - Rôle assigné
- `is_active` - Statut actif
- `expires_at` - Date d'expiration
- `assigned_by` - Utilisateur qui a assigné

### 🔄 PermissionDelegation
Délégation temporaire de permissions.

**Champs :**
- `delegator` - Utilisateur qui délègue
- `delegatee` - Utilisateur qui reçoit
- `permission` - Permission déléguée
- `start_date` / `end_date` - Période de délégation
- `max_uses` - Nombre maximum d'utilisations
- `current_uses` - Utilisations actuelles
- `allowed_ips` - IPs autorisées
- `allowed_actions` - Actions autorisées
- `conditions` - Conditions supplémentaires

### 🔄 RoleDelegation
Délégation temporaire de rôles.

**Champs :**
- `delegator` - Utilisateur qui délègue
- `delegatee` - Utilisateur qui reçoit
- `role` - Rôle délégué
- `excluded_permissions` - Permissions exclues
- `start_date` / `end_date` - Période de délégation
- `max_uses` - Nombre maximum d'utilisations
- `current_uses` - Utilisations actuelles
- `allowed_ips` - IPs autorisées

### ⚙️ PermissionManager
Gestionnaires avec droits spécifiques.

**Champs :**
- `user` - Utilisateur gestionnaire
- `can_create_permissions` - Peut créer des permissions
- `can_modify_permissions` - Peut modifier des permissions
- `can_delete_permissions` - Peut supprimer des permissions
- `can_create_roles` - Peut créer des rôles
- `can_modify_roles` - Peut modifier des rôles
- `can_delete_roles` - Peut supprimer des rôles
- `can_assign_roles` - Peut assigner des rôles
- `can_create_groups` - Peut créer des groupes
- `can_modify_groups` - Peut modifier des groupes
- `can_delete_groups` - Peut supprimer des groupes
- `can_manage_groups` - Peut gérer les groupes
- `can_delegate_permissions` - Peut déléguer des permissions
- `can_delegate_roles` - Peut déléguer des rôles
- `max_delegation_duration_days` - Durée max de délégation
- `max_delegation_uses` - Utilisations max de délégation
- `allowed_apps` - Applications autorisées
- `allowed_models` - Modèles autorisés

## 🚀 API Endpoints

### 🔐 Permissions

#### Liste des permissions
```http
GET /api/permissions/permissions/
```

**Paramètres de requête :**
- `app_label` - Filtrer par application
- `model` - Filtrer par modèle
- `action` - Filtrer par action
- `is_custom` - Filtrer par type (true/false)
- `is_active` - Filtrer par statut (true/false)
- `search` - Recherche textuelle
- `ordering` - Tri (ex: `app_label,model,action`)
- `page` - Numéro de page
- `page_size` - Taille de page

**Réponse :**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Can view user profile",
      "codename": "users.userprofile.view",
      "description": "Permission to view user profiles",
      "app_label": "users",
      "model": "userprofile",
      "action": "view",
      "field_name": null,
      "min_value": null,
      "max_value": null,
      "conditions": null,
      "is_custom": false,
      "is_custom_display": "Système",
      "is_active": true,
      "created_by": 1,
      "created_by_username": "admin@example.com",
      "created_at": "2025-09-08T10:00:00Z",
      "updated_at": "2025-09-08T10:00:00Z"
    }
  ],
  "count": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Détails d'une permission
```http
GET /api/permissions/permissions/{id}/
```

#### Créer une permission
```http
POST /api/permissions/permissions/create/
```

**Corps de la requête :**
```json
{
  "name": "Can modify user salary",
  "codename": "users.userprofile.change_salary",
  "description": "Permission to modify user salary field",
  "app_label": "users",
  "model": "userprofile",
  "action": "change",
  "field_name": "salary",
  "min_value": 0,
  "max_value": 100000,
  "conditions": {
    "department": "HR",
    "level": "manager"
  }
}
```

#### Modifier une permission
```http
PUT /api/permissions/permissions/{id}/update/
PATCH /api/permissions/permissions/{id}/update/
```

#### Supprimer une permission
```http
DELETE /api/permissions/permissions/{id}/delete/
```

#### Statistiques des permissions
```http
GET /api/permissions/permissions/stats/
```

**Réponse :**
```json
{
  "total_permissions": 25,
  "custom_permissions": 5,
  "active_permissions": 23,
  "permissions_by_app": {
    "users": 10,
    "permissions": 8,
    "notifications": 7
  },
  "permissions_by_action": {
    "view": 8,
    "add": 6,
    "change": 7,
    "delete": 4
  }
}
```

### 👑 Rôles

#### Liste des rôles
```http
GET /api/permissions/roles/
```

**Paramètres de requête :**
- `is_system` - Filtrer par type (true/false)
- `is_active` - Filtrer par statut (true/false)
- `search` - Recherche textuelle
- `ordering` - Tri
- `page` - Numéro de page
- `page_size` - Taille de page

#### Détails d'un rôle
```http
GET /api/permissions/roles/{id}/
```

#### Créer un rôle
```http
POST /api/permissions/roles/create/
```

**Corps de la requête :**
```json
{
  "name": "HR Manager",
  "description": "Human Resources Manager role",
  "permission_ids": [1, 2, 3, 4],
  "is_system": false
}
```

#### Modifier un rôle
```http
PUT /api/permissions/roles/{id}/update/
PATCH /api/permissions/roles/{id}/update/
```

#### Supprimer un rôle
```http
DELETE /api/permissions/roles/{id}/delete/
```

#### Statistiques des rôles
```http
GET /api/permissions/roles/stats/
```

#### Permissions d'un rôle
```http
GET /api/permissions/roles/{role_id}/permissions/
```

#### Détails d'une permission de rôle
```http
GET /api/permissions/roles/{role_id}/permissions/{permission_id}/
```

### 👥 Groupes

#### Liste des groupes
```http
GET /api/permissions/groups/
```

#### Détails d'un groupe
```http
GET /api/permissions/groups/{id}/
```

#### Créer un groupe
```http
POST /api/permissions/groups/create/
```

**Corps de la requête :**
```json
{
  "name": "Development Team",
  "description": "Software development team",
  "role_ids": [1, 2],
  "user_ids": [1, 2, 3]
}
```

#### Modifier un groupe
```http
PUT /api/permissions/groups/{id}/update/
PATCH /api/permissions/groups/{id}/update/
```

#### Supprimer un groupe
```http
DELETE /api/permissions/groups/{id}/delete/
```

#### Statistiques des groupes
```http
GET /api/permissions/groups/stats/
```

#### Adhésions aux groupes
```http
GET /api/permissions/group-memberships/
GET /api/permissions/group-memberships/{id}/
```

#### Rôles des groupes
```http
GET /api/permissions/group-roles/
GET /api/permissions/group-roles/{id}/
```

### 👤 Rôles Utilisateur

#### Liste des assignations de rôles
```http
GET /api/permissions/user-roles/
```

**Paramètres de requête :**
- `user_id` - Filtrer par utilisateur
- `role_id` - Filtrer par rôle
- `is_active` - Filtrer par statut
- `ordering` - Tri
- `page` - Numéro de page
- `page_size` - Taille de page

#### Détails d'une assignation
```http
GET /api/permissions/user-roles/{id}/
```

#### Assigner un rôle
```http
POST /api/permissions/user-roles/create/
```

**Corps de la requête :**
```json
{
  "user": 1,
  "role": 2,
  "expires_at": "2025-12-31T23:59:59Z"
}
```

#### Modifier une assignation
```http
PUT /api/permissions/user-roles/{id}/update/
PATCH /api/permissions/user-roles/{id}/update/
```

#### Supprimer une assignation
```http
DELETE /api/permissions/user-roles/{id}/delete/
```

#### Statistiques des assignations
```http
GET /api/permissions/user-roles/stats/
```

### 🔄 Délégations

#### Délégations de permissions
```http
GET /api/permissions/permission-delegations/
GET /api/permissions/permission-delegations/{id}/
POST /api/permissions/permission-delegations/create/
POST /api/permissions/permission-delegations/{id}/revoke/
```

**Créer une délégation :**
```json
{
  "delegatee": 2,
  "permission": 1,
  "start_date": "2025-09-08T10:00:00Z",
  "end_date": "2025-09-15T18:00:00Z",
  "max_uses": 10,
  "allowed_ips": ["192.168.1.100", "10.0.0.50"],
  "allowed_actions": ["GET", "POST"],
  "conditions": {
    "department": "HR",
    "time_range": "business_hours"
  }
}
```

#### Délégations de rôles
```http
GET /api/permissions/role-delegations/
GET /api/permissions/role-delegations/{id}/
POST /api/permissions/role-delegations/create/
POST /api/permissions/role-delegations/{id}/revoke/
```

**Créer une délégation de rôle :**
```json
{
  "delegatee": 2,
  "role": 1,
  "excluded_permission_ids": [3, 4],
  "start_date": "2025-09-08T10:00:00Z",
  "end_date": "2025-09-15T18:00:00Z",
  "max_uses": 5,
  "allowed_ips": ["192.168.1.100"]
}
```

#### Statistiques des délégations
```http
GET /api/permissions/delegations/stats/
```

### ⚙️ Gestionnaires de Permissions

#### Liste des gestionnaires
```http
GET /api/permissions/permission-managers/
```

#### Détails d'un gestionnaire
```http
GET /api/permissions/permission-managers/{id}/
```

#### Créer un gestionnaire
```http
POST /api/permissions/permission-managers/create/
```

**Corps de la requête :**
```json
{
  "user": 2,
  "can_create_permissions": true,
  "can_modify_permissions": true,
  "can_delete_permissions": false,
  "can_create_roles": true,
  "can_modify_roles": true,
  "can_delete_roles": false,
  "can_assign_roles": true,
  "can_create_groups": true,
  "can_modify_groups": true,
  "can_delete_groups": false,
  "can_manage_groups": true,
  "can_delegate_permissions": true,
  "can_delegate_roles": true,
  "max_delegation_duration_days": 30,
  "max_delegation_uses": 100,
  "allowed_apps": ["users", "permissions"],
  "allowed_models": ["userprofile", "role"]
}
```

#### Modifier un gestionnaire
```http
PUT /api/permissions/permission-managers/{id}/update/
PATCH /api/permissions/permission-managers/{id}/update/
```

#### Supprimer un gestionnaire
```http
DELETE /api/permissions/permission-managers/{id}/delete/
```

#### Statistiques des gestionnaires
```http
GET /api/permissions/permission-managers/stats/
```

## 🛡️ Middleware

### PermissionMiddleware
Vérifie automatiquement les permissions sur toutes les requêtes.

**Fonctionnalités :**
- Vérification automatique basée sur l'URL et la méthode HTTP
- Support des décorateurs de permissions
- Génération automatique de permissions
- Enregistrement des événements de sécurité
- Headers de réponse informatifs

### DelegationMiddleware
Gère les délégations de permissions via headers.

**Headers supportés :**
```http
X-Use-Delegation: permission:users.userprofile.change
X-Use-Delegation: role:Manager
```

### AuditMiddleware
Enregistre tous les accès pour l'audit.

**Informations trackées :**
- Utilisateur et IP
- Permissions et rôles
- Temps de réponse
- Délégations utilisées
- Événements de sécurité

## 🎨 Décorateurs

### Décorateurs de permissions
```python
from apps.permissions.decorators import (
    permission_required,
    any_permission_required,
    all_permissions_required,
    method_permissions
)

@permission_required('users.userprofile.view')
def view_profile(request):
    pass

@any_permission_required(['users.userprofile.view', 'users.userprofile.change'])
def view_or_edit_profile(request):
    pass

@method_permissions({
    'GET': 'users.userprofile.view',
    'POST': 'users.userprofile.add',
    'PUT': 'users.userprofile.change',
    'DELETE': 'users.userprofile.delete'
})
def profile_api(request):
    pass
```

### Décorateurs d'audit
```python
from apps.permissions.decorators import audit_required, audit_sensitive

@audit_required
def normal_view(request):
    pass

@audit_sensitive
def sensitive_operation(request):
    pass
```

### Décorateurs de délégation
```python
from apps.permissions.decorators import use_delegation

@use_delegation(permission_codename='users.userprofile.change')
def edit_with_delegation(request):
    pass
```

## 🔧 Utilitaires

### Vérification des permissions
```python
from apps.permissions.utils import (
    has_permission,
    has_any_permission,
    has_all_permissions,
    get_user_permissions,
    get_user_roles
)

# Vérifier une permission
if has_permission(user, 'users.userprofile.view'):
    # Utilisateur a la permission
    pass

# Vérifier plusieurs permissions
if has_any_permission(user, ['users.userprofile.view', 'users.userprofile.change']):
    # Utilisateur a au moins une permission
    pass

# Récupérer toutes les permissions d'un utilisateur
permissions = get_user_permissions(user)
roles = get_user_roles(user)
```

### Gestion des délégations
```python
from apps.permissions.utils import (
    create_delegation,
    revoke_delegation,
    has_delegated_permission
)

# Créer une délégation
delegation = create_delegation(
    delegator=admin_user,
    delegatee=temp_user,
    permission=permission,
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=7),
    max_uses=10
)

# Vérifier une délégation
if has_delegated_permission(user, 'users.userprofile.change'):
    # Utilisateur a la permission via délégation
    pass
```

## 📝 Exemples d'utilisation

### Créer un système de permissions complet

```python
# 1. Créer des permissions granulaires
from apps.permissions.models import Permission

# Permission pour modifier le salaire
salary_permission = Permission.objects.create(
    name="Can modify user salary",
    codename="users.userprofile.change_salary",
    description="Permission to modify user salary field",
    app_label="users",
    model="userprofile",
    action="change",
    field_name="salary",
    min_value=0,
    max_value=100000,
    is_custom=True
)

# 2. Créer un rôle HR Manager
from apps.permissions.models import Role

hr_manager_role = Role.objects.create(
    name="HR Manager",
    description="Human Resources Manager role",
    is_system=False
)

# Assigner des permissions au rôle
hr_manager_role.add_permission(salary_permission)

# 3. Créer un groupe
from apps.permissions.models import Group

hr_group = Group.objects.create(
    name="HR Team",
    description="Human Resources team"
)

# Assigner le rôle au groupe
hr_group.add_role(hr_manager_role)

# 4. Ajouter des utilisateurs au groupe
from apps.authentication.models import User

hr_user = User.objects.get(email="hr@example.com")
hr_group.add_user(hr_user)

# 5. Créer une délégation temporaire
from apps.permissions.models import PermissionDelegation
from django.utils import timezone
from datetime import timedelta

delegation = PermissionDelegation.objects.create(
    delegator=admin_user,
    delegatee=temp_user,
    permission=salary_permission,
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=7),
    max_uses=5,
    allowed_ips=["192.168.1.100"]
)
```

### Utiliser les permissions dans les vues

```python
from django.http import JsonResponse
from apps.permissions.decorators import permission_required, audit_sensitive
from apps.permissions.utils import has_permission

@permission_required('users.userprofile.change_salary')
@audit_sensitive
def update_user_salary(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_salary = request.data.get('salary')
    
    # Vérification supplémentaire avec contraintes
    if has_permission(request.user, 'users.userprofile.change_salary', 
                     resource=user, context={'salary': new_salary}):
        user.profile.salary = new_salary
        user.profile.save()
        return JsonResponse({'message': 'Salary updated successfully'})
    else:
        return JsonResponse({'error': 'Permission denied'}, status=403)
```

### Utiliser les délégations

```python
# Dans une requête API, utiliser une délégation
import requests

headers = {
    'Authorization': 'Bearer your_token',
    'X-Use-Delegation': 'permission:users.userprofile.change_salary'
}

response = requests.put(
    'http://localhost:8000/api/users/profile/1/',
    json={'salary': 75000},
    headers=headers
)
```

## ⚙️ Configuration

### Settings Django

```python
# config/settings/base.py

INSTALLED_APPS = [
    # ... autres apps
    'apps.permissions',
]

MIDDLEWARE = [
    # ... autres middlewares
    'apps.permissions.middleware.AuditMiddleware',
    'apps.permissions.middleware.DelegationMiddleware',
    'apps.permissions.middleware.PermissionMiddleware',
]
```

### URLs

```python
# config/urls.py

urlpatterns = [
    # ... autres URLs
    path('api/permissions/', include('apps.permissions.urls')),
]
```

## 🧪 Tests

### Tests unitaires

```python
# apps/permissions/tests/test_permissions.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.permissions.models import Permission, Role, UserRole
from apps.permissions.utils import has_permission

User = get_user_model()

class PermissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.permission = Permission.objects.create(
            name="Test Permission",
            codename="test.permission",
            app_label="test",
            model="test",
            action="view"
        )
        self.role = Role.objects.create(
            name="Test Role",
            description="Test role"
        )
        self.role.add_permission(self.permission)
    
    def test_user_has_permission_via_role(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role
        )
        self.assertTrue(has_permission(self.user, 'test.permission'))
    
    def test_user_without_permission(self):
        self.assertFalse(has_permission(self.user, 'test.permission'))
```

### Tests d'intégration

```python
# apps/permissions/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class PermissionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_permissions(self):
        response = self.client.get('/api/permissions/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_permission(self):
        data = {
            'name': 'Test Permission',
            'codename': 'test.permission',
            'app_label': 'test',
            'model': 'test',
            'action': 'view'
        }
        response = self.client.post('/api/permissions/permissions/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

## 📚 Ressources supplémentaires

- [Documentation Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions)
- [Django REST Framework Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [Middleware Django](https://docs.djangoproject.com/en/stable/topics/http/middleware/)

## 🤝 Contribution

Pour contribuer à l'app permissions :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**🛡️ Système de Permissions Avancé - Développé avec ❤️ pour Django**



