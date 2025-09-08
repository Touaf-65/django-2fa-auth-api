#!/usr/bin/env python
"""
Script de test pour les templates d'email
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
from datetime import datetime
from apps.notifications.services.template_email_service import TemplateEmailService
from apps.authentication.models import User

def test_email_templates():
    """Test des templates d'email"""
    print("🚀 Test des Templates d'Email")
    print("=" * 50)
    
    # Créer un utilisateur de test
    test_email = f"emailtest{int(datetime.now().timestamp())}@example.com"
    
    try:
        # 1. Inscription d'un utilisateur
        print(f"1️⃣ Inscription d'un utilisateur ({test_email})...")
        signup_data = {
            "username": f"emailtest{int(datetime.now().timestamp())}",
            "email": test_email,
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "Email"
        }
        
        response = requests.post('http://localhost:8000/api/auth/signup/', json=signup_data)
        if response.status_code == 201:
            print("   ✅ Utilisateur créé avec succès")
            user_data = response.json()
            user_id = user_data['user']['id']
        else:
            print(f"   ❌ Erreur lors de la création: {response.status_code}")
            return
        
        # 2. Récupérer l'utilisateur
        user = User.objects.get(id=user_id)
        
        # 3. Test des différents templates
        email_service = TemplateEmailService()
        
        print("\n2️⃣ Test des templates d'email...")
        
        # Test email de bienvenue
        print("   📧 Test email de bienvenue...")
        success = email_service.send_welcome_email(user)
        print(f"   {'✅' if success else '❌'} Email de bienvenue: {'Envoyé' if success else 'Échec'}")
        
        # Test email de connexion
        print("   🔐 Test email de connexion...")
        success = email_service.send_login_success_email(
            user=user,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            login_time=datetime.now()
        )
        print(f"   {'✅' if success else '❌'} Email de connexion: {'Envoyé' if success else 'Échec'}")
        
        # Test email de réinitialisation de mot de passe
        print("   🔑 Test email de réinitialisation...")
        success = email_service.send_password_reset_email(
            user=user,
            reset_code="123456",
            ip_address="192.168.1.100",
            expiry_minutes=30
        )
        print(f"   {'✅' if success else '❌'} Email de réinitialisation: {'Envoyé' if success else 'Échec'}")
        
        # Test email de changement de mot de passe
        print("   🔄 Test email de changement de mot de passe...")
        success = email_service.send_password_changed_email(
            user=user,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            change_time=datetime.now()
        )
        print(f"   {'✅' if success else '❌'} Email de changement: {'Envoyé' if success else 'Échec'}")
        
        # Test email de mise à jour de profil
        print("   👤 Test email de mise à jour de profil...")
        changes = {
            'first_name': {'old': 'Test', 'new': 'Test Updated'},
            'last_name': {'old': 'Email', 'new': 'Email Updated'}
        }
        success = email_service.send_profile_updated_email(
            user=user,
            changes=changes,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            update_time=datetime.now()
        )
        print(f"   {'✅' if success else '❌'} Email de profil: {'Envoyé' if success else 'Échec'}")
        
        # Test email d'alerte de sécurité
        print("   🚨 Test email d'alerte de sécurité...")
        success = email_service.send_security_alert_email(
            user=user,
            alert_type="Tentative de connexion suspecte",
            alert_description="Une tentative de connexion a été détectée depuis une nouvelle localisation.",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            alert_time=datetime.now(),
            recommended_actions=[
                "Changez votre mot de passe immédiatement",
                "Révoquez toutes les sessions actives",
                "Contactez notre support si nécessaire"
            ]
        )
        print(f"   {'✅' if success else '❌'} Email d'alerte: {'Envoyé' if success else 'Échec'}")
        
        # Test email d'activation 2FA
        print("   🔐 Test email d'activation 2FA...")
        backup_codes = ["123456", "789012", "345678", "901234", "567890"]
        success = email_service.send_2fa_enabled_email(
            user=user,
            backup_codes=backup_codes,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            activation_time=datetime.now()
        )
        print(f"   {'✅' if success else '❌'} Email 2FA: {'Envoyé' if success else 'Échec'}")
        
        print("\n3️⃣ Vérification des notifications...")
        response = requests.get('http://localhost:8000/api/notifications/')
        if response.status_code == 200:
            notifications = response.json()
            print(f"   📊 Total des notifications: {notifications.get('count', 0)}")
        else:
            print(f"   ❌ Erreur lors de la récupération des notifications: {response.status_code}")
        
        print("\n✅ Test des templates d'email terminé!")
        print(f"📧 Vérifiez votre boîte email: {test_email}")
        print("📋 Vérifiez les logs du serveur Django pour voir les emails envoyés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_templates()



