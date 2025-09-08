#!/usr/bin/env python
"""
Test rapide de l'API Django 2FA Auth
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

def test_quick():
    """Test rapide des endpoints principaux"""
    print("🚀 Test rapide de l'API Django 2FA Auth")
    print("=" * 50)
    
    # Test 1: Inscription
    print("\n1️⃣ Test d'inscription...")
    signup_data = {
        "email": "quicktest@example.com",
        "password": "QuickTest123!",
        "confirm_password": "QuickTest123!",
        "first_name": "Quick",
        "last_name": "Test"
    }
    
    try:
        response = requests.post(f"{API_BASE}/signup/", json=signup_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            access_token = result.get('tokens', {}).get('access')
            print("   ✅ Inscription réussie!")
            
            # Test 2: Profil
            print("\n2️⃣ Test du profil...")
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(f"{API_BASE}/profile/", headers=headers)
            print(f"   Status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("   ✅ Profil récupéré!")
                
                # Test 3: Configuration 2FA
                print("\n3️⃣ Test de configuration 2FA...")
                twofa_response = requests.post(f"{API_BASE}/2fa/setup/", headers=headers)
                print(f"   Status: {twofa_response.status_code}")
                
                if twofa_response.status_code == 200:
                    twofa_result = twofa_response.json()
                    secret_key = twofa_result.get('setup_data', {}).get('secret_key')
                    print("   ✅ Configuration 2FA générée!")
                    print(f"   🔑 Secret Key: {secret_key}")
                    
                    # Test 4: Statut 2FA
                    print("\n4️⃣ Test du statut 2FA...")
                    status_response = requests.get(f"{API_BASE}/2fa/status/", headers=headers)
                    print(f"   Status: {status_response.status_code}")
                    
                    if status_response.status_code == 200:
                        print("   ✅ Statut 2FA récupéré!")
                    
                else:
                    print("   ❌ Échec configuration 2FA")
            else:
                print("   ❌ Échec récupération profil")
        else:
            print("   ❌ Échec inscription")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Connexion
    print("\n5️⃣ Test de connexion...")
    login_data = {
        "email": "quicktest@example.com",
        "password": "QuickTest123!"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/signin/", json=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Connexion réussie!")
        else:
            print("   ❌ Échec connexion")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test rapide terminé!")
    print("\n📝 Pour des tests plus complets, utilisez:")
    print("   - test_api_complete.py (tests complets avec 2FA)")
    print("   - API_EXAMPLES.md (exemples de payloads)")
    print("   - test_curl_commands.sh (tests avec cURL)")

if __name__ == "__main__":
    test_quick()



