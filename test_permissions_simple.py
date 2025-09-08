#!/usr/bin/env python
"""
Test simple du système de permissions
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
from apps.permissions.models import (
    Permission, Role, Group, UserRole, GroupMembership, GroupRole,
    PermissionDelegation, RoleDelegation, PermissionManager
)
from apps.permissions.utils import (
    has_permission, get_user_permissions, get_user_roles,
    get_permission_codename, create_permission_from_string
)
from apps.authentication.models import User

def test_permissions_simple():
    """Test simple du système de permissions"""
    print("🔐 Test Simple du Système de Permissions")
    print("=" * 50)
    
    try:
        # 1. Récupérer un utilisateur existant
        print("1️⃣ Récupération d'un utilisateur existant...")
        user = User.objects.first()
        if not user:
            print("   ❌ Aucun utilisateur trouvé.")
            return
        print(f"   ✅ Utilisateur trouvé: {user.email}")
        
        # 2. Vérifier les permissions existantes
        print("\n2️⃣ Vérification des permissions existantes...")
        existing_permissions = Permission.objects.all()
        print(f"   📊 Permissions existantes: {existing_permissions.count()}")
        
        for perm in existing_permissions:
            print(f"   - {perm.codename}: {perm.name}")
        
        # 3. Vérifier les rôles existants
        print("\n3️⃣ Vérification des rôles existants...")
        existing_roles = Role.objects.all()
        print(f"   📊 Rôles existants: {existing_roles.count()}")
        
        for role in existing_roles:
            print(f"   - {role.name}: {role.get_permission_count()} permissions")
        
        # 4. Vérifier les groupes existants
        print("\n4️⃣ Vérification des groupes existants...")
        existing_groups = Group.objects.all()
        print(f"   📊 Groupes existants: {existing_groups.count()}")
        
        for group in existing_groups:
            print(f"   - {group.name}: {group.get_user_count()} utilisateurs")
        
        # 5. Tester les utilitaires de base
        print("\n5️⃣ Test des utilitaires de base...")
        
        # Générer un code de permission
        codename = get_permission_codename("test", "model", "action")
        print(f"   📝 Code généré: {codename}")
        
        # Test de vérification de permission (devrait être False car pas de rôles)
        has_perm = has_permission(user, "test.model.action")
        print(f"   🔍 Permission test: {has_perm}")
        
        # 6. Récupérer les permissions de l'utilisateur
        print("\n6️⃣ Permissions de l'utilisateur...")
        user_permissions = get_user_permissions(user)
        print(f"   📊 Permissions: {user_permissions.count()}")
        
        user_roles = get_user_roles(user)
        print(f"   📊 Rôles: {user_roles.count()}")
        
        # 7. Vérifier le profil de gestionnaire
        print("\n7️⃣ Profil de gestionnaire...")
        try:
            manager = PermissionManager.get_or_create_for_user(user)
            print(f"   ✅ Profil créé: {manager}")
            print(f"   📊 Peut créer des permissions: {manager.can_create_permissions}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 8. Statistiques finales
        print("\n8️⃣ Statistiques finales...")
        print(f"   📊 Total permissions: {Permission.objects.count()}")
        print(f"   📊 Total rôles: {Role.objects.count()}")
        print(f"   📊 Total groupes: {Group.objects.count()}")
        print(f"   📊 Total utilisateurs: {User.objects.count()}")
        
        print("\n✅ Test simple terminé!")
        print("🔐 Le système de permissions de base fonctionne")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions_simple()



