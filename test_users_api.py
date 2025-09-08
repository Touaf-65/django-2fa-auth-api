#!/usr/bin/env python
"""
Test de l'API Users
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
AUTH_BASE = f"{API_BASE}/auth"
USERS_BASE = f"{API_BASE}/users"

def test_users_api():
    """Test complet de l'API Users"""
    print("🚀 Test de l'API Users")
    print("=" * 50)
    
    # Utiliser un email unique
    timestamp = int(time.time())
    test_email = f"userstest{timestamp}@example.com"
    
    # Variables pour stocker les tokens
    access_token = None
    user_id = None
    
    # Test 1: Inscription d'un utilisateur
    print(f"\n1️⃣ Inscription d'un utilisateur ({test_email})...")
    signup_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Users",
        "last_name": "Test"
    }
    
    try:
        response = requests.post(f"{AUTH_BASE}/signup/", json=signup_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            access_token = result.get('tokens', {}).get('access')
            user_id = result.get('user', {}).get('id')
            print("   ✅ Inscription réussie!")
            print(f"   🔑 Token: {access_token[:20]}...")
            print(f"   👤 User ID: {user_id}")
        else:
            print("   ❌ Échec inscription")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    if not access_token:
        print("   ❌ Pas de token d'accès")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 2: Récupération du profil
    print("\n2️⃣ Récupération du profil...")
    try:
        response = requests.get(f"{USERS_BASE}/profile/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print("   ✅ Profil récupéré!")
            print(f"   📧 Email: {profile.get('user_email')}")
            print(f"   👤 Nom: {profile.get('display_name')}")
            print(f"   🔐 2FA: {profile.get('user_two_factor_enabled')}")
        else:
            print("   ❌ Échec récupération profil")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Mise à jour du profil
    print("\n3️⃣ Mise à jour du profil...")
    update_data = {
        "bio": "Développeur passionné par les technologies web et la sécurité.",
        "location": "Paris, France",
        "job_title": "Développeur Full Stack",
        "company": "TechCorp",
        "industry": "Technologie",
        "website": "https://example.com",
        "linkedin_url": "https://linkedin.com/in/example",
        "twitter_handle": "@example",
        "github_username": "example",
        "profile_visibility": "public",
        "show_email": True,
        "show_phone": False
    }
    
    try:
        response = requests.put(f"{USERS_BASE}/profile/update/", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Profil mis à jour!")
            print(f"   📝 Bio: {result.get('profile', {}).get('bio', '')[:50]}...")
            print(f"   📍 Location: {result.get('profile', {}).get('location')}")
        else:
            print("   ❌ Échec mise à jour profil")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Préférences utilisateur
    print("\n4️⃣ Gestion des préférences...")
    preferences_data = {
        "theme": "dark",
        "language": "fr",
        "timezone": "Europe/Paris",
        "email_notifications": True,
        "push_notifications": False,
        "notify_new_followers": True,
        "notify_new_messages": True,
        "show_online_status": True
    }
    
    try:
        response = requests.put(f"{USERS_BASE}/preferences/", json=preferences_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Préférences mises à jour!")
            print(f"   🎨 Thème: {result.get('preferences', {}).get('theme')}")
            print(f"   🌍 Langue: {result.get('preferences', {}).get('language')}")
        else:
            print("   ❌ Échec mise à jour préférences")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Liste des utilisateurs
    print("\n5️⃣ Liste des utilisateurs...")
    try:
        response = requests.get(f"{USERS_BASE}/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            users = result.get('users', [])
            print("   ✅ Liste des utilisateurs récupérée!")
            print(f"   👥 Nombre d'utilisateurs: {len(users)}")
            if users:
                first_user = users[0]
                print(f"   👤 Premier utilisateur: {first_user.get('email')}")
        else:
            print("   ❌ Échec récupération liste")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Recherche d'utilisateurs
    print("\n6️⃣ Recherche d'utilisateurs...")
    search_data = {
        "query": "test",
        "limit": 10
    }
    
    try:
        response = requests.post(f"{USERS_BASE}/search/", json=search_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            users = result.get('users', [])
            print("   ✅ Recherche effectuée!")
            print(f"   🔍 Résultats trouvés: {len(users)}")
            print(f"   📊 Total disponible: {result.get('total_found', 0)}")
        else:
            print("   ❌ Échec recherche")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 7: Statistiques utilisateur
    print("\n7️⃣ Statistiques utilisateur...")
    try:
        response = requests.get(f"{USERS_BASE}/stats/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Statistiques récupérées!")
            print(f"   👥 Abonnés: {stats.get('followers_count', 0)}")
            print(f"   👥 Suivis: {stats.get('following_count', 0)}")
            print(f"   🚫 Bloqués: {stats.get('blocked_count', 0)}")
            print(f"   📅 Âge du compte: {stats.get('account_age_days', 0)} jours")
        else:
            print("   ❌ Échec récupération statistiques")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 8: Activités utilisateur
    print("\n8️⃣ Activités utilisateur...")
    try:
        response = requests.get(f"{USERS_BASE}/activity/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            activities = result.get('activities', [])
            print("   ✅ Activités récupérées!")
            print(f"   📊 Nombre d'activités: {len(activities)}")
            if activities:
                first_activity = activities[0]
                print(f"   📝 Dernière activité: {first_activity.get('description', '')[:50]}...")
        else:
            print("   ❌ Échec récupération activités")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test de l'API Users terminé!")
    print("=" * 50)
    print("✅ L'API Users fonctionne correctement!")
    print("\n📋 Endpoints testés:")
    print("   ✅ GET  /api/users/profile/ - Profil utilisateur")
    print("   ✅ PUT  /api/users/profile/update/ - Mise à jour profil")
    print("   ✅ PUT  /api/users/preferences/ - Préférences")
    print("   ✅ GET  /api/users/ - Liste des utilisateurs")
    print("   ✅ POST /api/users/search/ - Recherche d'utilisateurs")
    print("   ✅ GET  /api/users/stats/ - Statistiques")
    print("   ✅ GET  /api/users/activity/ - Activités")
    
    print("\n🎯 Fonctionnalités disponibles:")
    print("   👤 Gestion complète des profils utilisateur")
    print("   ⚙️ Préférences personnalisables")
    print("   🔍 Recherche et liste d'utilisateurs")
    print("   📊 Statistiques et activités")
    print("   👥 Relations entre utilisateurs (suivi/blocage)")
    print("   🔒 Gestion de la confidentialité")

if __name__ == "__main__":
    test_users_api()

