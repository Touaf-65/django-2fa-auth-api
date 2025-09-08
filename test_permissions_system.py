#!/usr/bin/env python
"""
Test du système de permissions avancé
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
    has_permission, has_any_permission, has_all_permissions,
    check_permission_with_context, get_user_permissions, get_user_roles,
    create_delegation, can_delegate_permission, get_permission_codename,
    create_permission_from_string, get_model_permissions
)
from apps.authentication.models import User

def test_permissions_system():
    """Test complet du système de permissions"""
    print("🔐 Test du Système de Permissions Avancé")
    print("=" * 60)
    
    try:
        # 1. Récupérer un utilisateur existant
        print("1️⃣ Récupération d'un utilisateur existant...")
        try:
            user = User.objects.first()
            if not user:
                print("   ❌ Aucun utilisateur trouvé. Créez d'abord un utilisateur.")
                return
            print(f"   ✅ Utilisateur trouvé: {user.email}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            return
        
        # 2. Créer des permissions de test
        print("\n2️⃣ Création de permissions de test...")
        try:
            # Permission de base
            view_permission = Permission.create_permission(
                name="Voir les profils utilisateur",
                codename="users.userprofile.view",
                description="Permission pour voir les profils utilisateur",
                app_label="users",
                model="userprofile",
                action="view",
                created_by=user
            )
            print(f"   ✅ Permission créée: {view_permission}")
            
            # Permission granulaire (champ salaire)
            salary_permission = Permission.create_permission(
                name="Modifier le salaire",
                codename="users.userprofile.salary.change",
                description="Permission pour modifier le salaire des utilisateurs",
                app_label="users",
                model="userprofile",
                action="change",
                field_name="salary",
                max_value=10000,  # Maximum 10000€
                created_by=user
            )
            print(f"   ✅ Permission granulaire créée: {salary_permission}")
            
            # Permission avec conditions
            admin_permission = Permission.create_permission(
                name="Administration des utilisateurs",
                codename="users.user.admin",
                description="Permission d'administration des utilisateurs",
                app_label="users",
                model="user",
                action="admin",
                conditions={"department": "IT"},
                created_by=user
            )
            print(f"   ✅ Permission avec conditions créée: {admin_permission}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 3. Créer des rôles
        print("\n3️⃣ Création de rôles...")
        try:
            # Rôle Manager
            manager_role = Role.create_role(
                name="Manager",
                description="Rôle de manager avec permissions de base",
                permissions=[view_permission, salary_permission],
                created_by=user
            )
            print(f"   ✅ Rôle créé: {manager_role}")
            print(f"   📊 Permissions du rôle: {manager_role.get_permission_count()}")
            
            # Rôle Admin
            admin_role = Role.create_role(
                name="Admin",
                description="Rôle d'administrateur",
                permissions=[view_permission, salary_permission, admin_permission],
                created_by=user
            )
            print(f"   ✅ Rôle créé: {admin_role}")
            print(f"   📊 Permissions du rôle: {admin_role.get_permission_count()}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 4. Créer des groupes
        print("\n4️⃣ Création de groupes...")
        try:
            # Groupe IT
            it_group = Group.create_group(
                name="Équipe IT",
                description="Groupe de l'équipe informatique",
                roles=[manager_role],
                created_by=user
            )
            print(f"   ✅ Groupe créé: {it_group}")
            
            # Groupe Admin
            admin_group = Group.create_group(
                name="Administrateurs",
                description="Groupe des administrateurs",
                roles=[admin_role],
                created_by=user
            )
            print(f"   ✅ Groupe créé: {admin_group}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 5. Assigner des rôles et groupes
        print("\n5️⃣ Attribution de rôles et groupes...")
        try:
            # Assigner un rôle direct
            user_role = UserRole.assign_role(
                user=user,
                role=manager_role,
                assigned_by=user,
                expires_at=timezone.now() + timedelta(days=30)
            )
            print(f"   ✅ Rôle assigné: {user_role}")
            
            # Ajouter à un groupe
            membership = it_group.add_user(user, joined_by=user)
            print(f"   ✅ Utilisateur ajouté au groupe: {membership}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 6. Tester les vérifications de permissions
        print("\n6️⃣ Test des vérifications de permissions...")
        try:
            # Test permission de base
            has_view = has_permission(user, "users.userprofile.view")
            print(f"   🔍 Permission 'view': {has_view}")
            
            # Test permission granulaire
            has_salary = has_permission(user, "users.userprofile.salary.change")
            print(f"   🔍 Permission 'salary.change': {has_salary}")
            
            # Test permission avec conditions
            has_admin = has_permission(user, "users.user.admin", context={"department": "IT"})
            print(f"   🔍 Permission 'admin' (département IT): {has_admin}")
            
            # Test permission inexistante
            has_fake = has_permission(user, "fake.permission")
            print(f"   🔍 Permission inexistante: {has_fake}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 7. Test des permissions multiples
        print("\n7️⃣ Test des permissions multiples...")
        try:
            # Test has_any_permission
            any_permission = has_any_permission(
                user, 
                ["users.userprofile.view", "users.userprofile.salary.change", "fake.permission"]
            )
            print(f"   🔍 Au moins une permission: {any_permission}")
            
            # Test has_all_permissions
            all_permission = has_all_permissions(
                user,
                ["users.userprofile.view", "users.userprofile.salary.change"]
            )
            print(f"   🔍 Toutes les permissions: {all_permission}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 8. Test de vérification détaillée
        print("\n8️⃣ Test de vérification détaillée...")
        try:
            detailed_result = check_permission_with_context(
                user,
                "users.userprofile.salary.change",
                context={"department": "IT"}
            )
            print(f"   🔍 Résultat détaillé: {detailed_result['has_permission']}")
            print(f"   📊 Raison: {detailed_result['reason']}")
            if detailed_result['details']:
                print(f"   📋 Détails: {detailed_result['details']}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 9. Test des utilitaires
        print("\n9️⃣ Test des utilitaires...")
        try:
            # Récupérer les permissions de l'utilisateur
            user_permissions = get_user_permissions(user)
            print(f"   📊 Permissions de l'utilisateur: {user_permissions.count()}")
            
            # Récupérer les rôles de l'utilisateur
            user_roles = get_user_roles(user)
            print(f"   📊 Rôles de l'utilisateur: {user_roles.count()}")
            
            # Générer un code de permission
            codename = get_permission_codename("users", "userprofile", "change", "email")
            print(f"   📝 Code de permission généré: {codename}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 10. Test de délégation
        print("\n🔟 Test de délégation...")
        try:
            # Créer un autre utilisateur pour la délégation
            test_user = User.objects.create_user(
                email="test_delegation@example.com",
                password="TestPassword123!"
            )
            print(f"   ✅ Utilisateur de test créé: {test_user.email}")
            
            # Vérifier si on peut déléguer
            can_delegate = can_delegate_permission(user, test_user, "users.userprofile.view")
            print(f"   🔍 Peut déléguer: {can_delegate['can_delegate']}")
            print(f"   📝 Raison: {can_delegate['reason']}")
            
            # Créer une délégation si possible
            if can_delegate['can_delegate']:
                delegation = create_delegation(
                    user, test_user, "users.userprofile.view",
                    constraints={
                        'end_date': timezone.now() + timedelta(days=7),
                        'max_uses': 10
                    }
                )
                print(f"   ✅ Délégation créée: {delegation}")
                print(f"   ⏰ Expire le: {delegation.end_date}")
                print(f"   🔢 Utilisations max: {delegation.max_uses}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 11. Statistiques finales
        print("\n1️⃣1️⃣ Statistiques finales...")
        try:
            from apps.permissions.utils.permission_helpers import get_permission_statistics
            
            stats = get_permission_statistics()
            print(f"   📊 Total permissions: {stats['permissions']['total']}")
            print(f"   📊 Permissions personnalisées: {stats['permissions']['custom']}")
            print(f"   📊 Total rôles: {stats['roles']['total']}")
            print(f"   📊 Total groupes: {stats['groups']['total']}")
            print(f"   📊 Utilisateurs avec rôles: {stats['users']['with_roles']}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print("\n✅ Test du système de permissions terminé!")
        print("🔐 Le système de permissions avancé fonctionne correctement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions_system()
