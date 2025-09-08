#!/usr/bin/env python
"""
Script de test complet pour l'API Django 2FA Auth
"""

import requests
import json
import time
import pyotp
from io import BytesIO
import base64

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        self.two_factor_secret = None
        
    def print_response(self, response, title):
        """Affiche la réponse de manière formatée"""
        print(f"\n{'='*50}")
        print(f"🧪 {title}")
        print(f"{'='*50}")
        print(f"Status: {response.status_code}")
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            return response_json
        except:
            print(f"Response: {response.text}")
            return None
    
    def test_user_registration(self):
        """Test de l'inscription d'un utilisateur"""
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
        
        response = self.session.post(url, json=data)
        result = self.print_response(response, "Test d'inscription d'utilisateur")
        
        if response.status_code == 201 and result:
            self.access_token = result.get('tokens', {}).get('access')
            self.refresh_token = result.get('tokens', {}).get('refresh')
            self.user_data = result.get('user')
            print("✅ Inscription réussie!")
            return True
        else:
            print("❌ Échec de l'inscription")
            return False
    
    def test_user_login(self):
        """Test de connexion d'un utilisateur"""
        url = f"{API_BASE}/signin/"
        data = {
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        response = self.session.post(url, json=data)
        result = self.print_response(response, "Test de connexion d'utilisateur")
        
        if response.status_code == 200 and result:
            if result.get('requires_2fa'):
                print("⚠️ 2FA requis - utilisateur avec 2FA activé")
                return "2fa_required"
            else:
                self.access_token = result.get('tokens', {}).get('access')
                self.refresh_token = result.get('tokens', {}).get('refresh')
                print("✅ Connexion réussie!")
                return True
        else:
            print("❌ Échec de la connexion")
            return False
    
    def test_user_profile(self):
        """Test de récupération du profil utilisateur"""
        if not self.access_token:
            print("❌ Pas de token d'accès disponible")
            return False
            
        url = f"{API_BASE}/profile/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = self.session.get(url, headers=headers)
        result = self.print_response(response, "Test de récupération du profil")
        
        if response.status_code == 200:
            print("✅ Profil récupéré avec succès!")
            return True
        else:
            print("❌ Échec de récupération du profil")
            return False
    
    def test_update_profile(self):
        """Test de mise à jour du profil"""
        if not self.access_token:
            print("❌ Pas de token d'accès disponible")
            return False
            
        url = f"{API_BASE}/profile/update/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "first_name": "Test Updated",
            "language": "en",
            "timezone": "America/New_York"
        }
        
        response = self.session.put(url, json=data, headers=headers)
        result = self.print_response(response, "Test de mise à jour du profil")
        
        if response.status_code == 200:
            print("✅ Profil mis à jour avec succès!")
            return True
        else:
            print("❌ Échec de mise à jour du profil")
            return False
    
    def test_2fa_setup(self):
        """Test de configuration 2FA"""
        if not self.access_token:
            print("❌ Pas de token d'accès disponible")
            return False
            
        url = f"{API_BASE}/2fa/setup/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = self.session.post(url, headers=headers)
        result = self.print_response(response, "Test de configuration 2FA")
        
        if response.status_code == 200 and result:
            setup_data = result.get('setup_data', {})
            self.two_factor_secret = setup_data.get('secret_key')
            print("✅ Configuration 2FA générée!")
            print(f"🔑 Secret Key: {self.two_factor_secret}")
            print(f"📱 QR Code généré: {len(setup_data.get('qr_code', ''))} caractères")
            print(f"🔐 Codes de secours: {len(setup_data.get('backup_codes', []))} codes")
            return True
        else:
            print("❌ Échec de configuration 2FA")
            return False
    
    def test_2fa_verify_setup(self):
        """Test de vérification et activation 2FA"""
        if not self.access_token or not self.two_factor_secret:
            print("❌ Pas de token d'accès ou secret 2FA disponible")
            return False
        
        # Générer un code TOTP valide
        totp = pyotp.TOTP(self.two_factor_secret)
        current_code = totp.now()
        
        url = f"{API_BASE}/2fa/verify-setup/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {"code": current_code}
        
        response = self.session.post(url, json=data, headers=headers)
        result = self.print_response(response, "Test de vérification 2FA (activation)")
        
        if response.status_code == 200:
            print("✅ 2FA activé avec succès!")
            return True
        else:
            print("❌ Échec d'activation 2FA")
            return False
    
    def test_2fa_status(self):
        """Test de récupération du statut 2FA"""
        if not self.access_token:
            print("❌ Pas de token d'accès disponible")
            return False
            
        url = f"{API_BASE}/2fa/status/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = self.session.get(url, headers=headers)
        result = self.print_response(response, "Test de statut 2FA")
        
        if response.status_code == 200:
            print("✅ Statut 2FA récupéré!")
            return True
        else:
            print("❌ Échec de récupération du statut 2FA")
            return False
    
    def test_2fa_verify_login(self):
        """Test de vérification 2FA lors de la connexion"""
        if not self.two_factor_secret:
            print("❌ Pas de secret 2FA disponible")
            return False
        
        # Générer un code TOTP valide
        totp = pyotp.TOTP(self.two_factor_secret)
        current_code = totp.now()
        
        url = f"{API_BASE}/2fa/verify-login/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {"code": current_code}
        
        response = self.session.post(url, json=data, headers=headers)
        result = self.print_response(response, "Test de vérification 2FA (connexion)")
        
        if response.status_code == 200:
            print("✅ Connexion 2FA réussie!")
            return True
        else:
            print("❌ Échec de connexion 2FA")
            return False
    
    def test_token_refresh(self):
        """Test de rafraîchissement des tokens"""
        if not self.refresh_token:
            print("❌ Pas de token de rafraîchissement disponible")
            return False
            
        url = f"{API_BASE}/token/refresh/"
        data = {"refresh": self.refresh_token}
        
        response = self.session.post(url, json=data)
        result = self.print_response(response, "Test de rafraîchissement des tokens")
        
        if response.status_code == 200 and result:
            self.access_token = result.get('access')
            print("✅ Tokens rafraîchis avec succès!")
            return True
        else:
            print("❌ Échec de rafraîchissement des tokens")
            return False
    
    def test_logout(self):
        """Test de déconnexion"""
        if not self.access_token or not self.refresh_token:
            print("❌ Pas de tokens disponibles")
            return False
            
        url = f"{API_BASE}/logout/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {"refresh_token": self.refresh_token}
        
        response = self.session.post(url, json=data, headers=headers)
        result = self.print_response(response, "Test de déconnexion")
        
        if response.status_code == 200:
            print("✅ Déconnexion réussie!")
            return True
        else:
            print("❌ Échec de déconnexion")
            return False
    
    def run_complete_test(self):
        """Exécute tous les tests dans l'ordre"""
        print("🚀 Démarrage des tests complets de l'API Django 2FA Auth")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Inscription
        total_tests += 1
        if self.test_user_registration():
            tests_passed += 1
        
        # Test 2: Profil
        total_tests += 1
        if self.test_user_profile():
            tests_passed += 1
        
        # Test 3: Mise à jour profil
        total_tests += 1
        if self.test_update_profile():
            tests_passed += 1
        
        # Test 4: Configuration 2FA
        total_tests += 1
        if self.test_2fa_setup():
            tests_passed += 1
        
        # Test 5: Activation 2FA
        total_tests += 1
        if self.test_2fa_verify_setup():
            tests_passed += 1
        
        # Test 6: Statut 2FA
        total_tests += 1
        if self.test_2fa_status():
            tests_passed += 1
        
        # Test 7: Connexion avec 2FA
        total_tests += 1
        if self.test_2fa_verify_login():
            tests_passed += 1
        
        # Test 8: Rafraîchissement tokens
        total_tests += 1
        if self.test_token_refresh():
            tests_passed += 1
        
        # Test 9: Déconnexion
        total_tests += 1
        if self.test_logout():
            tests_passed += 1
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"✅ Tests réussis: {tests_passed}/{total_tests}")
        print(f"❌ Tests échoués: {total_tests - tests_passed}/{total_tests}")
        print(f"📈 Taux de réussite: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("🎉 Tous les tests sont passés avec succès!")
        else:
            print("⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        
        return tests_passed == total_tests

def main():
    """Fonction principale"""
    tester = APITester()
    success = tester.run_complete_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

