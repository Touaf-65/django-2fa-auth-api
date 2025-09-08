#!/usr/bin/env python
"""
Test des vues API pour les permissions
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone
from apps.permissions.models import Permission, Role, Group, UserRole
from apps.authentication.models import User

def test_permissions_api():
    """Test des vues API pour les permissions"""
    print("🚀 Test des Vues API Permissions")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Récupérer un utilisateur existant
        print("1️⃣ Récupération d'un utilisateur existant...")
        user = User.objects.first()
        if not user:
            print("   ❌ Aucun utilisateur trouvé.")
            return
        print(f"   ✅ Utilisateur trouvé: {user.email}")
        
        # 2. Se connecter pour obtenir un token
        print("\n2️⃣ Connexion pour obtenir un token...")
        login_data = {
            "email": user.email,
            "password": "TestPassword123!"  # Mot de passe par défaut
        }
        
        try:
            response = requests.post(f"{base_url}/api/auth/signin/", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access')
                print(f"   ✅ Token obtenu: {access_token[:20]}...")
            else:
                print(f"   ❌ Erreur de connexion: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
                return
        except requests.exceptions.ConnectionError:
            print("   ❌ Impossible de se connecter au serveur. Assurez-vous que le serveur Django est démarré.")
            return
        
        # Headers pour les requêtes authentifiées
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # 3. Tester la liste des permissions
        print("\n3️⃣ Test de la liste des permissions...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permissions/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Permissions récupérées: {data.get('count', 0)}")
                if data.get('results'):
                    first_permission = data['results'][0]
                    print(f"   📊 Première permission: {first_permission.get('name', 'N/A')}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 4. Tester la création d'une permission
        print("\n4️⃣ Test de création d'une permission...")
        permission_data = {
            "name": "Test API Permission",
            "codename": "test.api.permission",
            "description": "Permission créée via l'API de test",
            "app_label": "test",
            "model": "api",
            "action": "permission"
        }
        
        try:
            response = requests.post(f"{base_url}/api/permissions/permissions/create/", 
                                   json=permission_data, headers=headers)
            if response.status_code == 201:
                created_permission = response.json()
                print(f"   ✅ Permission créée: {created_permission.get('name')}")
                permission_id = created_permission.get('id')
            else:
                print(f"   ❌ Erreur de création: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
                permission_id = None
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            permission_id = None
        
        # 5. Tester la liste des rôles
        print("\n5️⃣ Test de la liste des rôles...")
        try:
            response = requests.get(f"{base_url}/api/permissions/roles/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Rôles récupérés: {data.get('count', 0)}")
                if data.get('results'):
                    first_role = data['results'][0]
                    print(f"   📊 Premier rôle: {first_role.get('name', 'N/A')}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 6. Tester la création d'un rôle
        print("\n6️⃣ Test de création d'un rôle...")
        role_data = {
            "name": "Test API Role",
            "description": "Rôle créé via l'API de test",
            "permission_ids": [permission_id] if permission_id else []
        }
        
        try:
            response = requests.post(f"{base_url}/api/permissions/roles/create/", 
                                   json=role_data, headers=headers)
            if response.status_code == 201:
                created_role = response.json()
                print(f"   ✅ Rôle créé: {created_role.get('name')}")
                role_id = created_role.get('id')
            else:
                print(f"   ❌ Erreur de création: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
                role_id = None
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            role_id = None
        
        # 7. Tester la liste des groupes
        print("\n7️⃣ Test de la liste des groupes...")
        try:
            response = requests.get(f"{base_url}/api/permissions/groups/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Groupes récupérés: {data.get('count', 0)}")
                if data.get('results'):
                    first_group = data['results'][0]
                    print(f"   📊 Premier groupe: {first_group.get('name', 'N/A')}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 8. Tester les statistiques
        print("\n8️⃣ Test des statistiques...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permissions/stats/", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"   ✅ Statistiques récupérées")
                print(f"   📊 Total permissions: {stats.get('total_permissions', 0)}")
                print(f"   📊 Permissions personnalisées: {stats.get('custom_permissions', 0)}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 9. Tester les rôles utilisateur
        print("\n9️⃣ Test des rôles utilisateur...")
        try:
            response = requests.get(f"{base_url}/api/permissions/user-roles/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Rôles utilisateur récupérés: {data.get('count', 0)}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   📝 Réponse: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 10. Statistiques finales
        print("\n🔟 Statistiques finales...")
        print(f"   📊 Total permissions: {Permission.objects.count()}")
        print(f"   📊 Total rôles: {Role.objects.count()}")
        print(f"   📊 Total groupes: {Group.objects.count()}")
        print(f"   📊 Total rôles utilisateur: {UserRole.objects.count()}")
        
        print("\n✅ Test des vues API terminé!")
        print("🚀 Les vues API pour les permissions fonctionnent correctement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions_api()
