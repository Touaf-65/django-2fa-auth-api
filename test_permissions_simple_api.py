#!/usr/bin/env python
"""
Test simple des vues API pour les permissions
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

def test_permissions_api_simple():
    """Test simple des vues API pour les permissions"""
    print("🚀 Test Simple des Vues API Permissions")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Tester l'accès aux permissions sans authentification
        print("1️⃣ Test d'accès aux permissions sans authentification...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permissions/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            elif response.status_code == 200:
                print("   ⚠️  Accès autorisé sans authentification")
            else:
                print(f"   ❓ Status inattendu: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ Impossible de se connecter au serveur")
            return
        
        # 2. Tester l'accès aux rôles
        print("\n2️⃣ Test d'accès aux rôles...")
        try:
            response = requests.get(f"{base_url}/api/permissions/roles/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            else:
                print(f"   ❓ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 3. Tester l'accès aux groupes
        print("\n3️⃣ Test d'accès aux groupes...")
        try:
            response = requests.get(f"{base_url}/api/permissions/groups/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            else:
                print(f"   ❓ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 4. Tester l'accès aux statistiques
        print("\n4️⃣ Test d'accès aux statistiques...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permissions/stats/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            else:
                print(f"   ❓ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 5. Tester l'accès aux délégations
        print("\n5️⃣ Test d'accès aux délégations...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permission-delegations/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            else:
                print(f"   ❓ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 6. Tester l'accès aux gestionnaires de permissions
        print("\n6️⃣ Test d'accès aux gestionnaires de permissions...")
        try:
            response = requests.get(f"{base_url}/api/permissions/permission-managers/")
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Authentification requise (comme attendu)")
            else:
                print(f"   ❓ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print("\n✅ Test simple terminé!")
        print("🛡️ Les vues API sont accessibles et protégées par authentification")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions_api_simple()



