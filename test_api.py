#!/usr/bin/env python
"""
Script de test pour l'API Django 2FA Auth
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

def test_user_registration():
    """Test de l'inscription d'un utilisateur"""
    print("🧪 Test d'inscription d'utilisateur...")
    
    url = f"{API_BASE}/signup/"
    data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "language": "fr",
        "timezone": "Europe/Paris"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json() if response.status_code == 201 else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_user_login():
    """Test de connexion d'un utilisateur"""
    print("\n🧪 Test de connexion d'utilisateur...")
    
    url = f"{API_BASE}/signin/"
    data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_2fa_setup(access_token):
    """Test de configuration 2FA"""
    print("\n🧪 Test de configuration 2FA...")
    
    url = f"{API_BASE}/2fa/setup/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_user_profile(access_token):
    """Test de récupération du profil utilisateur"""
    print("\n🧪 Test de récupération du profil...")
    
    url = f"{API_BASE}/profile/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de l'API Django 2FA Auth")
    print("=" * 50)
    
    # Test 1: Inscription
    registration_result = test_user_registration()
    
    if registration_result:
        print("✅ Inscription réussie!")
        access_token = registration_result.get('tokens', {}).get('access')
        
        if access_token:
            # Test 2: Profil utilisateur
            test_user_profile(access_token)
            
            # Test 3: Configuration 2FA
            test_2fa_setup(access_token)
    
    # Test 4: Connexion
    login_result = test_user_login()
    
    if login_result:
        print("✅ Connexion réussie!")
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés!")

if __name__ == "__main__":
    main()



