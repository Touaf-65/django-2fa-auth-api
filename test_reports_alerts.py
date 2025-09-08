#!/usr/bin/env python3
"""
Script de test pour les rapports automatiques et alertes système
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_reports_alerts():
    """Test des rapports automatiques et alertes système"""
    print("🚀 Test des Rapports Automatiques et Alertes Système")
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
    
    # 2. Test des métriques système
    print("\n2. Test des métriques système...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/metrics/", headers=headers)
        if response.status_code == 200:
            print("✅ Métriques système récupérées")
            metrics = response.json()
            print(f"   - Score de santé: {metrics.get('health_score')}")
            print(f"   - CPU: {metrics.get('system_info', {}).get('cpu_percent')}%")
            print(f"   - Mémoire: {metrics.get('system_info', {}).get('memory_percent')}%")
            print(f"   - Disque: {metrics.get('system_info', {}).get('disk_percent')}%")
        else:
            print(f"❌ Erreur métriques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur métriques: {e}")
    
    # 3. Test de la santé du système
    print("\n3. Test de la santé du système...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/health/", headers=headers)
        if response.status_code == 200:
            print("✅ Santé du système vérifiée")
            health = response.json()
            print(f"   - Score: {health.get('health_score')}")
            print(f"   - Statut: {health.get('status')}")
        else:
            print(f"❌ Erreur santé: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur santé: {e}")
    
    # 4. Test des templates de rapport
    print("\n4. Test des templates de rapport...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/reports/templates/", headers=headers)
        if response.status_code == 200:
            print("✅ Templates de rapport récupérés")
            templates = response.json()
            print(f"   - Nombre de templates: {len(templates.get('results', []))}")
        else:
            print(f"❌ Erreur templates: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur templates: {e}")
    
    # 5. Test des rapports programmés
    print("\n5. Test des rapports programmés...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/reports/scheduled/", headers=headers)
        if response.status_code == 200:
            print("✅ Rapports programmés récupérés")
            reports = response.json()
            print(f"   - Nombre de rapports: {len(reports.get('results', []))}")
        else:
            print(f"❌ Erreur rapports: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur rapports: {e}")
    
    # 6. Test des exécutions de rapport
    print("\n6. Test des exécutions de rapport...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/reports/executions/", headers=headers)
        if response.status_code == 200:
            print("✅ Exécutions de rapport récupérées")
            executions = response.json()
            print(f"   - Nombre d'exécutions: {len(executions.get('results', []))}")
        else:
            print(f"❌ Erreur exécutions: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur exécutions: {e}")
    
    # 7. Test des statistiques de rapport
    print("\n7. Test des statistiques de rapport...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/reports/statistics/", headers=headers)
        if response.status_code == 200:
            print("✅ Statistiques de rapport récupérées")
            stats = response.json()
            print(f"   - Templates actifs: {stats.get('total_templates')}")
            print(f"   - Rapports programmés: {stats.get('total_scheduled_reports')}")
            print(f"   - Exécutions réussies: {stats.get('successful_executions')}")
        else:
            print(f"❌ Erreur stats rapports: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats rapports: {e}")
    
    # 8. Test des règles d'alerte
    print("\n8. Test des règles d'alerte...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/alerts/rules/", headers=headers)
        if response.status_code == 200:
            print("✅ Règles d'alerte récupérées")
            rules = response.json()
            print(f"   - Nombre de règles: {len(rules.get('results', []))}")
        else:
            print(f"❌ Erreur règles: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur règles: {e}")
    
    # 9. Test des alertes système
    print("\n9. Test des alertes système...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/alerts/", headers=headers)
        if response.status_code == 200:
            print("✅ Alertes système récupérées")
            alerts = response.json()
            print(f"   - Nombre d'alertes: {len(alerts.get('results', []))}")
        else:
            print(f"❌ Erreur alertes: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur alertes: {e}")
    
    # 10. Test des notifications d'alerte
    print("\n10. Test des notifications d'alerte...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/alerts/notifications/", headers=headers)
        if response.status_code == 200:
            print("✅ Notifications d'alerte récupérées")
            notifications = response.json()
            print(f"   - Nombre de notifications: {len(notifications.get('results', []))}")
        else:
            print(f"❌ Erreur notifications: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur notifications: {e}")
    
    # 11. Test des statistiques d'alerte
    print("\n11. Test des statistiques d'alerte...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/alerts/statistics/", headers=headers)
        if response.status_code == 200:
            print("✅ Statistiques d'alerte récupérées")
            stats = response.json()
            print(f"   - Total alertes: {stats.get('total_alerts')}")
            print(f"   - Alertes actives: {stats.get('active_alerts')}")
            print(f"   - Alertes résolues: {stats.get('resolved_alerts')}")
        else:
            print(f"❌ Erreur stats alertes: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats alertes: {e}")
    
    # 12. Test de vérification des alertes
    print("\n12. Test de vérification des alertes...")
    try:
        response = requests.post(f"{BASE_URL}/api/admin/alerts/check/", headers=headers)
        if response.status_code == 200:
            print("✅ Vérification des alertes terminée")
            result = response.json()
            print(f"   - Message: {result.get('message')}")
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test des Rapports et Alertes terminé !")

if __name__ == "__main__":
    test_reports_alerts()

