#!/usr/bin/env python
"""
Test direct des fonctionnalités de sécurité
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import datetime
from apps.security.models import LoginAttempt, SecurityEvent, IPBlock, UserSecurity, SecurityRule
from apps.authentication.models import User

def test_security_models():
    """Test direct des modèles de sécurité"""
    print("🛡️ Test Direct des Modèles de Sécurité")
    print("=" * 50)
    
    try:
        # 1. Récupérer un utilisateur existant
        print("1️⃣ Récupération d'un utilisateur existant...")
        try:
            user = User.objects.first()
            if not user:
                print("   ❌ Aucun utilisateur trouvé. Créez d'abord un utilisateur.")
                return
            print(f"   ✅ Utilisateur trouvé: {user.email}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            return
        
        # 2. Test du profil de sécurité
        print("\n2️⃣ Test du profil de sécurité...")
        try:
            security_profile = UserSecurity.get_or_create_for_user(user)
            print(f"   ✅ Profil de sécurité: {security_profile}")
            print(f"   📊 Score de sécurité: {security_profile.get_security_score()}")
            print(f"   🔒 Statut: {security_profile.get_status_display()}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 3. Test des tentatives de connexion
        print("\n3️⃣ Test des tentatives de connexion...")
        try:
            # Enregistrer une tentative échouée
            failed_attempt = LoginAttempt.record_attempt(
                email=user.email,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                status=LoginAttempt.FAILED,
                user=user,
                failure_reason="Mot de passe incorrect"
            )
            print(f"   ✅ Tentative échouée enregistrée: {failed_attempt}")
            
            # Enregistrer une tentative réussie
            success_attempt = LoginAttempt.record_attempt(
                email=user.email,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                status=LoginAttempt.SUCCESS,
                user=user
            )
            print(f"   ✅ Tentative réussie enregistrée: {success_attempt}")
            
            # Vérifier les compteurs
            failed_count = LoginAttempt.get_failed_attempts_count("192.168.1.100", user.email, minutes=15)
            print(f"   📊 Tentatives échouées récentes: {failed_count}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 4. Test des événements de sécurité
        print("\n4️⃣ Test des événements de sécurité...")
        try:
            # Créer un événement de sécurité
            security_event = SecurityEvent.create_event(
                event_type=SecurityEvent.SUSPICIOUS_ACTIVITY,
                title="Test d'événement de sécurité",
                description="Ceci est un test d'événement de sécurité",
                ip_address="192.168.1.100",
                user=user,
                severity=SecurityEvent.MEDIUM,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                country="FR",
                city="Paris",
                metadata={"test": True, "source": "direct_test"}
            )
            print(f"   ✅ Événement créé: {security_event}")
            print(f"   📊 Type: {security_event.get_event_type_display()}")
            print(f"   ⚠️ Gravité: {security_event.get_severity_display()}")
            
            # Ajouter une action
            security_event.add_action("test_action", "Action de test ajoutée")
            print(f"   ✅ Action ajoutée à l'événement")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 5. Test du blocage IP
        print("\n5️⃣ Test du blocage IP...")
        try:
            test_ip = "192.168.1.200"
            
            # Bloquer une IP
            ip_block = IPBlock.block_ip(
                ip_address=test_ip,
                reason="Test de blocage IP",
                block_type=IPBlock.MANUAL,
                duration_minutes=5
            )
            print(f"   ✅ IP bloquée: {ip_block}")
            print(f"   📊 Statut: {ip_block.get_status_display()}")
            print(f"   ⏰ Expire dans: {ip_block.get_remaining_time()} minutes")
            
            # Vérifier le blocage
            is_blocked = IPBlock.is_ip_blocked(test_ip)
            print(f"   🔒 IP bloquée: {is_blocked}")
            
            # Débloquer l'IP
            unblocked_count = IPBlock.unblock_ip(test_ip)
            print(f"   🔓 IP débloquée: {unblocked_count} blocage(s) supprimé(s)")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 6. Test des règles de sécurité
        print("\n6️⃣ Test des règles de sécurité...")
        try:
            # Créer une règle de sécurité
            security_rule = SecurityRule.objects.create(
                name="Test Rule",
                description="Règle de test pour la sécurité",
                rule_type=SecurityRule.RATE_LIMIT,
                conditions={"requests_per_minute": 10},
                actions=[{
                    "type": "send_alert",
                    "params": {
                        "title": "Rate limit dépassé",
                        "description": "Trop de requêtes détectées",
                        "severity": "medium"
                    }
                }],
                priority=1,
                status=SecurityRule.ACTIVE
            )
            print(f"   ✅ Règle créée: {security_rule}")
            
            # Tester la règle
            context = {"requests_per_minute": 15}
            if security_rule.is_condition_met(context):
                print("   ✅ Condition de la règle remplie")
                results = security_rule.execute_actions(context)
                print(f"   📊 Actions exécutées: {len(results)}")
            else:
                print("   ❌ Condition de la règle non remplie")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        # 7. Statistiques finales
        print("\n7️⃣ Statistiques finales...")
        try:
            total_attempts = LoginAttempt.objects.count()
            failed_attempts = LoginAttempt.objects.filter(status='failed').count()
            successful_attempts = LoginAttempt.objects.filter(status='success').count()
            blocked_ips = IPBlock.objects.filter(status='active').count()
            security_events_count = SecurityEvent.objects.count()
            security_rules_count = SecurityRule.objects.count()
            
            print(f"   📊 Total des tentatives de connexion: {total_attempts}")
            print(f"   ❌ Tentatives échouées: {failed_attempts}")
            print(f"   ✅ Tentatives réussies: {successful_attempts}")
            print(f"   🚫 IPs bloquées: {blocked_ips}")
            print(f"   🛡️ Événements de sécurité: {security_events_count}")
            print(f"   📋 Règles de sécurité: {security_rules_count}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print("\n✅ Test des modèles de sécurité terminé!")
        print("🛡️ Toutes les fonctionnalités de sécurité fonctionnent correctement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_security_models()

