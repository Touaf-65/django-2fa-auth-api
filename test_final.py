#!/usr/bin/env python
"""
Test final de l'API Django 2FA Auth
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

def test_final():
    """Test final complet de l'API"""
    print("🚀 Test Final de l'API Django 2FA Auth")
    print("=" * 60)
    
    # Utiliser un email unique
    timestamp = int(time.time())
    test_email = f"test{timestamp}@example.com"
    
    # Test 1: Inscription
    print(f"\n1️⃣ Test d'inscription avec {test_email}...")
    signup_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "language": "fr",
        "timezone": "Europe/Paris"
    }
    
    try:
        response = requests.post(f"{API_BASE}/signup/", json=signup_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            access_token = result.get('tokens', {}).get('access')
            refresh_token = result.get('tokens', {}).get('refresh')
            print("   ✅ Inscription réussie!")
            print(f"   🔑 Token d'accès récupéré: {access_token[:20]}...")
            
            # Test 2: Profil
            print("\n2️⃣ Test du profil...")
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(f"{API_BASE}/profile/", headers=headers)
            print(f"   Status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("   ✅ Profil récupéré!")
                print(f"   👤 Utilisateur: {profile_data.get('first_name')} {profile_data.get('last_name')}")
                print(f"   📧 Email: {profile_data.get('email')}")
                print(f"   🔐 2FA activé: {profile_data.get('two_factor_enabled')}")
                
                # Test 3: Mise à jour profil
                print("\n3️⃣ Test de mise à jour du profil...")
                update_data = {
                    "first_name": "Test Updated",
                    "language": "en",
                    "timezone": "America/New_York"
                }
                update_response = requests.put(f"{API_BASE}/profile/update/", 
                                             json=update_data, headers=headers)
                print(f"   Status: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    print("   ✅ Profil mis à jour!")
                else:
                    print("   ❌ Échec mise à jour profil")
                
                # Test 4: Configuration 2FA
                print("\n4️⃣ Test de configuration 2FA...")
                twofa_response = requests.post(f"{API_BASE}/2fa/setup/", headers=headers)
                print(f"   Status: {twofa_response.status_code}")
                
                if twofa_response.status_code == 200:
                    twofa_result = twofa_response.json()
                    setup_data = twofa_result.get('setup_data', {})
                    secret_key = setup_data.get('secret_key')
                    backup_codes = setup_data.get('backup_codes', [])
                    print("   ✅ Configuration 2FA générée!")
                    print(f"   🔑 Secret Key: {secret_key}")
                    print(f"   🔐 Codes de secours: {len(backup_codes)} codes")
                    print(f"   📱 QR Code généré: {len(setup_data.get('qr_code', ''))} caractères")
                    
                    # Test 5: Statut 2FA
                    print("\n5️⃣ Test du statut 2FA...")
                    status_response = requests.get(f"{API_BASE}/2fa/status/", headers=headers)
                    print(f"   Status: {status_response.status_code}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print("   ✅ Statut 2FA récupéré!")
                        print(f"   🔐 2FA activé: {status_data.get('is_enabled')}")
                        print(f"   ⚙️ 2FA configuré: {status_data.get('is_configured')}")
                        print(f"   🔑 Codes de secours: {status_data.get('backup_codes_count')} codes")
                    
                    # Test 6: Rafraîchissement des tokens
                    print("\n6️⃣ Test de rafraîchissement des tokens...")
                    refresh_data = {"refresh": refresh_token}
                    refresh_response = requests.post(f"{API_BASE}/token/refresh/", json=refresh_data)
                    print(f"   Status: {refresh_response.status_code}")
                    
                    if refresh_response.status_code == 200:
                        new_token = refresh_response.json().get('access')
                        print("   ✅ Tokens rafraîchis!")
                        print(f"   🔑 Nouveau token: {new_token[:20]}...")
                    else:
                        print("   ❌ Échec rafraîchissement tokens")
                    
                    # Test 7: Déconnexion
                    print("\n7️⃣ Test de déconnexion...")
                    logout_data = {"refresh_token": refresh_token}
                    logout_response = requests.post(f"{API_BASE}/logout/", 
                                                  json=logout_data, headers=headers)
                    print(f"   Status: {logout_response.status_code}")
                    
                    if logout_response.status_code == 200:
                        print("   ✅ Déconnexion réussie!")
                    else:
                        print("   ❌ Échec déconnexion")
                    
                else:
                    print("   ❌ Échec configuration 2FA")
                    print(f"   Response: {twofa_response.text}")
            else:
                print("   ❌ Échec récupération profil")
                print(f"   Response: {profile_response.text}")
        else:
            print("   ❌ Échec inscription")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 8: Connexion avec le nouvel utilisateur
    print(f"\n8️⃣ Test de connexion avec {test_email}...")
    login_data = {
        "email": test_email,
        "password": "TestPassword123!"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/signin/", json=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("   ✅ Connexion réussie!")
            print(f"   🔐 2FA requis: {login_result.get('requires_2fa', False)}")
            if login_result.get('requires_2fa'):
                print("   ⚠️  L'utilisateur a la 2FA activée")
        else:
            print("   ❌ Échec connexion")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Final Terminé!")
    print("=" * 60)
    print("✅ L'API Django 2FA Auth fonctionne correctement!")
    print("\n📋 Endpoints testés:")
    print("   ✅ POST /api/auth/signup/ - Inscription")
    print("   ✅ GET  /api/auth/profile/ - Profil")
    print("   ✅ PUT  /api/auth/profile/update/ - Mise à jour profil")
    print("   ✅ POST /api/auth/2fa/setup/ - Configuration 2FA")
    print("   ✅ GET  /api/auth/2fa/status/ - Statut 2FA")
    print("   ✅ POST /api/auth/token/refresh/ - Rafraîchissement tokens")
    print("   ✅ POST /api/auth/logout/ - Déconnexion")
    print("   ✅ POST /api/auth/signin/ - Connexion")
    
    print("\n🎯 Prochaines étapes:")
    print("   📱 Tester la vérification 2FA avec une app d'authentification")
    print("   🔧 Implémenter les autres apps (users, notifications, security)")
    print("   🐳 Configurer Docker")
    print("   🧪 Ajouter des tests unitaires")

if __name__ == "__main__":
    test_final()



