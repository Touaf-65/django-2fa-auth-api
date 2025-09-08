#!/usr/bin/env python3
"""
Script de test pour l'Admin API
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_admin_api():
    """Test des endpoints de l'Admin API"""
    print("🚀 Test de l'Admin API")
    print("=" * 50)
    
    # 1. Connexion admin
    print("\n1. Connexion admin...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signin/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            print(f"✅ Connexion réussie: {data.get('user', {}).get('email')}")
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(response.text)
            return
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que le serveur Django est démarré.")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. Test des endpoints système
    print("\n2. Test des endpoints système...")
    
    # Informations système
    try:
        response = requests.get(f"{BASE_URL}/api/admin/system/info/", headers=headers)
        if response.status_code == 200:
            print("✅ Informations système récupérées")
            system_info = response.json()
            print(f"   - Plateforme: {system_info.get('platform', {}).get('system')}")
            print(f"   - Django: {system_info.get('django', {}).get('version')}")
        else:
            print(f"❌ Erreur info système: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur info système: {e}")
    
    # Santé du système
    try:
        response = requests.get(f"{BASE_URL}/api/admin/system/health/", headers=headers)
        if response.status_code == 200:
            print("✅ Santé du système vérifiée")
            health = response.json()
            print(f"   - Statut global: {health.get('overall')}")
        else:
            print(f"❌ Erreur santé système: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur santé système: {e}")
    
    # 3. Test des statistiques utilisateurs
    print("\n3. Test des statistiques utilisateurs...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/stats/", headers=headers)
        if response.status_code == 200:
            print("✅ Statistiques utilisateurs récupérées")
            stats = response.json()
            print(f"   - Total utilisateurs: {stats.get('total_users')}")
            print(f"   - Utilisateurs actifs: {stats.get('active_users')}")
        else:
            print(f"❌ Erreur stats utilisateurs: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats utilisateurs: {e}")
    
    # 4. Test des actions d'administration
    print("\n4. Test des actions d'administration...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/actions/", headers=headers)
        if response.status_code == 200:
            print("✅ Liste des actions récupérée")
            actions = response.json()
            print(f"   - Nombre d'actions: {len(actions.get('results', []))}")
        else:
            print(f"❌ Erreur liste actions: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur liste actions: {e}")
    
    # 5. Test des logs d'administration
    print("\n5. Test des logs d'administration...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/logs/", headers=headers)
        if response.status_code == 200:
            print("✅ Liste des logs récupérée")
            logs = response.json()
            print(f"   - Nombre de logs: {len(logs.get('results', []))}")
        else:
            print(f"❌ Erreur liste logs: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur liste logs: {e}")
    
    # 6. Test du dashboard
    print("\n6. Test du dashboard...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/dashboard/stats/", headers=headers)
        if response.status_code == 200:
            print("✅ Statistiques dashboard récupérées")
            dashboard_stats = response.json()
            print(f"   - Utilisateurs: {dashboard_stats.get('users', {}).get('total')}")
        else:
            print(f"❌ Erreur dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur dashboard: {e}")
    
    # 7. Test de la configuration système
    print("\n7. Test de la configuration système...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/config/", headers=headers)
        if response.status_code == 200:
            print("✅ Configuration système récupérée")
            configs = response.json()
            print(f"   - Nombre de configurations: {len(configs.get('results', []))}")
        else:
            print(f"❌ Erreur configuration: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test de l'Admin API terminé !")

if __name__ == "__main__":
    test_admin_api()

