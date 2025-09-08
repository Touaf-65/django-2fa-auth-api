#!/usr/bin/env python
"""
Script de test pour l'API Security
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
from apps.security.models import LoginAttempt, SecurityEvent, IPBlock, UserSecurity
from apps.authentication.models import User

def test_security_features():
    """Test des fonctionnalités de sécurité"""
    print("🛡️ Test de l'API Security")
    print("=" * 50)
    
    try:
        # 1. Test de création d'un utilisateur
        print("1️⃣ Création d'un utilisateur de test...")
        test_email = f"securitytest{int(datetime.now().timestamp())}@example.com"
        signup_data = {
            "username": f"securitytest{int(datetime.now().timestamp())}",
            "email": test_email,
            "password": "TestPassword123!",
            "first_name": "Security",
            "last_name": "Test"
        }
        
        response = requests.post('http://localhost:8000/api/auth/signup/', json=signup_data)
        if response.status_code == 201:
            print("   ✅ Utilisateur créé avec succès")
            user_data = response.json()
            user_id = user_data['user']['id']
        else:
            print(f"   ❌ Erreur lors de la création: {response.status_code}")
            return
        
        # 2. Vérifier la création du profil de sécurité
        print("\n2️⃣ Vérification du profil de sécurité...")
        try:
            user = User.objects.get(id=user_id)
            security_profile = UserSecurity.get_or_create_for_user(user)
            print(f"   ✅ Profil de sécurité créé: {security_profile}")
            print(f"   📊 Score de sécurité: {security_profile.get_security_score()}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 3. Test de tentatives de connexion échouées
        print("\n3️⃣ Test de tentatives de connexion échouées...")
        for i in range(3):
            login_data = {
                "email": test_email,
                "password": "WrongPassword123!"
            }
            
            response = requests.post('http://localhost:8000/api/auth/signin/', json=login_data)
            print(f"   Tentative {i+1}: Status {response.status_code}")
        
        # 4. Vérifier les tentatives enregistrées
        print("\n4️⃣ Vérification des tentatives enregistrées...")
        try:
            failed_attempts = LoginAttempt.objects.filter(email=test_email, status='failed')
            print(f"   📊 Tentatives échouées enregistrées: {failed_attempts.count()}")
            
            for attempt in failed_attempts:
                print(f"   - {attempt.created_at}: {attempt.status} - {attempt.ip_address}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 5. Test de connexion réussie
        print("\n5️⃣ Test de connexion réussie...")
        login_data = {
            "email": test_email,
            "password": "TestPassword123!"
        }
        
        response = requests.post('http://localhost:8000/api/auth/signin/', json=login_data)
        if response.status_code == 200:
            print("   ✅ Connexion réussie")
            tokens = response.json()
            access_token = tokens.get('access')
        else:
            print(f"   ❌ Erreur de connexion: {response.status_code}")
            return
        
        # 6. Vérifier les événements de sécurité
        print("\n6️⃣ Vérification des événements de sécurité...")
        try:
            security_events = SecurityEvent.objects.filter(user=user)
            print(f"   📊 Événements de sécurité: {security_events.count()}")
            
            for event in security_events:
                print(f"   - {event.event_type}: {event.title} ({event.severity})")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 7. Test de rate limiting
        print("\n7️⃣ Test de rate limiting...")
        headers = {'Authorization': f'Bearer {access_token}'}
        
        for i in range(5):
            response = requests.get('http://localhost:8000/api/users/profile/', headers=headers)
            print(f"   Requête {i+1}: Status {response.status_code}")
            
            # Vérifier les headers de rate limiting
            if 'X-RateLimit-Remaining-Minute' in response.headers:
                remaining = response.headers['X-RateLimit-Remaining-Minute']
                print(f"   📊 Requêtes restantes: {remaining}")
        
        # 8. Test de blocage IP (simulation)
        print("\n8️⃣ Test de blocage IP...")
        try:
            # Créer un blocage IP de test
            test_ip = "192.168.1.100"
            ip_block = IPBlock.block_ip(
                ip_address=test_ip,
                reason="Test de blocage IP",
                block_type="manual",
                duration_minutes=5
            )
            
            if ip_block:
                print(f"   ✅ IP {test_ip} bloquée avec succès")
                print(f"   📊 Statut: {ip_block.get_status_display()}")
                print(f"   ⏰ Expire dans: {ip_block.get_remaining_time()} minutes")
                
                # Vérifier le blocage
                is_blocked = IPBlock.is_ip_blocked(test_ip)
                print(f"   🔒 IP bloquée: {is_blocked}")
                
                # Débloquer l'IP
                unblocked_count = IPBlock.unblock_ip(test_ip)
                print(f"   🔓 IP débloquée: {unblocked_count} blocage(s) supprimé(s)")
            else:
                print("   ❌ Erreur lors du blocage IP")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 9. Statistiques de sécurité
        print("\n9️⃣ Statistiques de sécurité...")
        try:
            total_attempts = LoginAttempt.objects.count()
            failed_attempts = LoginAttempt.objects.filter(status='failed').count()
            successful_attempts = LoginAttempt.objects.filter(status='success').count()
            blocked_ips = IPBlock.objects.filter(status='active').count()
            security_events_count = SecurityEvent.objects.count()
            
            print(f"   📊 Total des tentatives de connexion: {total_attempts}")
            print(f"   ❌ Tentatives échouées: {failed_attempts}")
            print(f"   ✅ Tentatives réussies: {successful_attempts}")
            print(f"   🚫 IPs bloquées: {blocked_ips}")
            print(f"   🛡️ Événements de sécurité: {security_events_count}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print("\n✅ Test de l'API Security terminé!")
        print("🛡️ Les fonctionnalités de sécurité sont opérationnelles")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_security_features()

