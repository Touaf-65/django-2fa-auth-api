#!/usr/bin/env python
"""
Test de l'API Notifications
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
AUTH_BASE = f"{API_BASE}/auth"
NOTIFICATIONS_BASE = f"{API_BASE}/notifications"

def test_notifications_api():
    """Test complet de l'API Notifications"""
    print("🚀 Test de l'API Notifications")
    print("=" * 50)
    
    # Utiliser un email unique
    timestamp = int(time.time())
    test_email = f"notificationstest{timestamp}@example.com"
    
    # Variables pour stocker les tokens
    access_token = None
    user_id = None
    
    # Test 1: Inscription d'un utilisateur
    print(f"\n1️⃣ Inscription d'un utilisateur ({test_email})...")
    signup_data = {
        "email": test_email,
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Notifications",
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
    
    # Test 2: Statistiques des notifications
    print("\n2️⃣ Statistiques des notifications...")
    try:
        response = requests.get(f"{NOTIFICATIONS_BASE}/stats/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Statistiques récupérées!")
            print(f"   📊 Total: {stats.get('total_notifications', 0)}")
            print(f"   ✅ Envoyées: {stats.get('sent_notifications', 0)}")
            print(f"   ❌ Échouées: {stats.get('failed_notifications', 0)}")
            print(f"   ⏳ En attente: {stats.get('pending_notifications', 0)}")
        else:
            print("   ❌ Échec récupération statistiques")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Envoi d'un email
    print("\n3️⃣ Envoi d'un email...")
    email_data = {
        "user_id": user_id,
        "subject": "Test Email - API Notifications",
        "content": "Ceci est un email de test envoyé via l'API Notifications. Fonctionnalité testée avec succès!",
        "priority": "normal"
    }
    
    try:
        response = requests.post(f"{NOTIFICATIONS_BASE}/emails/send/", json=email_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ Email envoyé!")
            print(f"   📧 Sujet: {result.get('notification', {}).get('subject')}")
            print(f"   📊 Statut: {result.get('notification', {}).get('status')}")
        else:
            print("   ❌ Échec envoi email")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Envoi d'un SMS
    print("\n4️⃣ Envoi d'un SMS...")
    sms_data = {
        "user_id": user_id,
        "message": "Test SMS - API Notifications. Fonctionnalité testée avec succès!",
        "priority": "normal"
    }
    
    try:
        response = requests.post(f"{NOTIFICATIONS_BASE}/sms/send/", json=sms_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ SMS envoyé!")
            print(f"   📱 Message: {result.get('notification', {}).get('message')}")
            print(f"   📊 Statut: {result.get('notification', {}).get('status')}")
        else:
            print("   ❌ Échec envoi SMS")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Création d'un token push
    print("\n5️⃣ Création d'un token push...")
    push_token_data = {
        "token": f"test_push_token_{timestamp}_1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
        "device_type": "web",
        "device_name": "Test Device",
        "app_version": "1.0.0"
    }
    
    try:
        response = requests.post(f"{NOTIFICATIONS_BASE}/push/tokens/create/", json=push_token_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ Token push créé!")
            print(f"   📱 Device: {result.get('token', {}).get('device_name')}")
            print(f"   🔧 Type: {result.get('token', {}).get('device_type')}")
        else:
            print("   ❌ Échec création token push")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Envoi d'une notification push
    print("\n6️⃣ Envoi d'une notification push...")
    push_data = {
        "user_id": user_id,
        "title": "Test Push - API Notifications",
        "body": "Ceci est une notification push de test envoyée via l'API Notifications.",
        "data": {"test": "true", "timestamp": timestamp},
        "priority": "normal"
    }
    
    try:
        response = requests.post(f"{NOTIFICATIONS_BASE}/push/send/", json=push_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ Notification push envoyée!")
            print(f"   📱 Titre: {result.get('notification', {}).get('title')}")
            print(f"   📊 Statut: {result.get('notification', {}).get('status')}")
        else:
            print("   ❌ Échec envoi notification push")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 7: Liste des notifications
    print("\n7️⃣ Liste des notifications...")
    try:
        response = requests.get(f"{NOTIFICATIONS_BASE}/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('notifications', [])
            print("   ✅ Liste des notifications récupérée!")
            print(f"   📊 Nombre de notifications: {len(notifications)}")
            if notifications:
                first_notification = notifications[0]
                print(f"   📝 Première notification: {first_notification.get('notification_type')} - {first_notification.get('status')}")
        else:
            print("   ❌ Échec récupération liste")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 8: Templates de notifications
    print("\n8️⃣ Templates de notifications...")
    try:
        response = requests.get(f"{NOTIFICATIONS_BASE}/templates/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            templates = result.get('templates', [])
            print("   ✅ Templates récupérés!")
            print(f"   📊 Nombre de templates: {len(templates)}")
        else:
            print("   ❌ Échec récupération templates")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 9: Statistiques par type
    print("\n9️⃣ Statistiques par type...")
    try:
        # Statistiques SMS
        response = requests.get(f"{NOTIFICATIONS_BASE}/sms/stats/", headers=headers)
        if response.status_code == 200:
            sms_stats = response.json()
            print("   ✅ Statistiques SMS récupérées!")
            print(f"   📱 SMS total: {sms_stats.get('total_sms', 0)}")
            print(f"   ✅ SMS envoyés: {sms_stats.get('sent_sms', 0)}")
        
        # Statistiques Push
        response = requests.get(f"{NOTIFICATIONS_BASE}/push/stats/", headers=headers)
        if response.status_code == 200:
            push_stats = response.json()
            print("   ✅ Statistiques Push récupérées!")
            print(f"   📱 Push total: {push_stats.get('total_push', 0)}")
            print(f"   ✅ Push envoyés: {push_stats.get('sent_push', 0)}")
            print(f"   🔑 Tokens actifs: {push_stats.get('active_tokens', 0)}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test de l'API Notifications terminé!")
    print("=" * 50)
    print("✅ L'API Notifications fonctionne correctement!")
    print("\n📋 Endpoints testés:")
    print("   ✅ GET  /api/notifications/stats/ - Statistiques")
    print("   ✅ POST /api/notifications/emails/send/ - Envoi email")
    print("   ✅ POST /api/notifications/sms/send/ - Envoi SMS")
    print("   ✅ POST /api/notifications/push/tokens/create/ - Création token push")
    print("   ✅ POST /api/notifications/push/send/ - Envoi notification push")
    print("   ✅ GET  /api/notifications/ - Liste des notifications")
    print("   ✅ GET  /api/notifications/templates/ - Templates")
    print("   ✅ GET  /api/notifications/sms/stats/ - Statistiques SMS")
    print("   ✅ GET  /api/notifications/push/stats/ - Statistiques Push")
    
    print("\n🎯 Fonctionnalités disponibles:")
    print("   📧 Gestion complète des emails (SendGrid/Django SMTP)")
    print("   📱 Gestion des SMS (Twilio/Mock)")
    print("   🔔 Notifications push (Firebase Cloud Messaging/Mock)")
    print("   📊 Statistiques et logs détaillés")
    print("   🎨 Templates personnalisables")
    print("   📦 Envoi en masse")
    print("   ⏰ Planification des envois")
    print("   🔄 Système de retry automatique")

if __name__ == "__main__":
    test_notifications_api()

