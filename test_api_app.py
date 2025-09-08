#!/usr/bin/env python3
"""
Script de test pour l'API App
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_api_app():
    """Test de l'API App"""
    print("🚀 Test de l'API App")
    print("=" * 60)
    
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
    
    # 2. Test des versions d'API
    print("\n2. Test des versions d'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/versions/", headers=headers)
        if response.status_code == 200:
            print("✅ Versions d'API récupérées")
            versions = response.json()
            print(f"   - Nombre de versions: {len(versions.get('results', []))}")
        else:
            print(f"❌ Erreur versions: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur versions: {e}")
    
    # 3. Test des endpoints d'API
    print("\n3. Test des endpoints d'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/endpoints/", headers=headers)
        if response.status_code == 200:
            print("✅ Endpoints d'API récupérés")
            endpoints = response.json()
            print(f"   - Nombre d'endpoints: {len(endpoints.get('results', []))}")
        else:
            print(f"❌ Erreur endpoints: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoints: {e}")
    
    # 4. Test de l'utilisation de l'API
    print("\n4. Test de l'utilisation de l'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/usage/", headers=headers)
        if response.status_code == 200:
            print("✅ Utilisation de l'API récupérée")
            usage = response.json()
            print(f"   - Nombre d'utilisations: {len(usage.get('results', []))}")
        else:
            print(f"❌ Erreur utilisation: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur utilisation: {e}")
    
    # 5. Test des limites de taux
    print("\n5. Test des limites de taux...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/rate-limits/", headers=headers)
        if response.status_code == 200:
            print("✅ Limites de taux récupérées")
            rate_limits = response.json()
            print(f"   - Nombre de limites: {len(rate_limits.get('results', []))}")
        else:
            print(f"❌ Erreur limites de taux: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur limites de taux: {e}")
    
    # 6. Test des métadonnées d'API
    print("\n6. Test des métadonnées d'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/metadata/", headers=headers)
        if response.status_code == 200:
            print("✅ Métadonnées d'API récupérées")
            metadata = response.json()
            print(f"   - Nombre de métadonnées: {len(metadata.get('results', []))}")
        else:
            print(f"❌ Erreur métadonnées: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur métadonnées: {e}")
    
    # 7. Test des health checks
    print("\n7. Test des health checks...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/health-checks/", headers=headers)
        if response.status_code == 200:
            print("✅ Health checks récupérés")
            health_checks = response.json()
            print(f"   - Nombre de health checks: {len(health_checks.get('results', []))}")
        else:
            print(f"❌ Erreur health checks: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur health checks: {e}")
    
    # 8. Test de la documentation d'API
    print("\n8. Test de la documentation d'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/documentation/", headers=headers)
        if response.status_code == 200:
            print("✅ Documentation d'API récupérée")
            documentation = response.json()
            print(f"   - Nombre de documents: {len(documentation.get('results', []))}")
        else:
            print(f"❌ Erreur documentation: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur documentation: {e}")
    
    # 9. Test des SDKs
    print("\n9. Test des SDKs...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/sdks/", headers=headers)
        if response.status_code == 200:
            print("✅ SDKs récupérés")
            sdks = response.json()
            print(f"   - Nombre de SDKs: {len(sdks.get('results', []))}")
        else:
            print(f"❌ Erreur SDKs: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur SDKs: {e}")
    
    # 10. Test des statistiques d'API
    print("\n10. Test des statistiques d'API...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/statistics/", headers=headers)
        if response.status_code == 200:
            print("✅ Statistiques d'API récupérées")
            stats = response.json()
            print(f"   - Total versions: {stats.get('total_versions', 0)}")
            print(f"   - Total endpoints: {stats.get('total_endpoints', 0)}")
            print(f"   - Total utilisations: {stats.get('total_usage', 0)}")
        else:
            print(f"❌ Erreur statistiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test de l'API App terminé !")

if __name__ == "__main__":
    test_api_app()



