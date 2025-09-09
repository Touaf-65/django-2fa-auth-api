# 🛡️ Security App

## Vue d'ensemble

L'app **Security** fournit un système de sécurité avancé avec monitoring des événements, blocage d'IP, détection d'intrusion, rate limiting et audit trail complet.

## 🚀 Fonctionnalités

### ✅ Monitoring de sécurité
- Surveillance des événements de sécurité
- Détection d'intrusion en temps réel
- Alertes de sécurité automatiques
- Logs d'audit complets

### ✅ Protection par IP
- Blocage automatique d'IPs suspectes
- Liste blanche et noire d'IPs
- Géolocalisation des IPs
- Détection de proxy/VPN

### ✅ Rate limiting
- Limitation de débit par IP
- Limitation de débit par utilisateur
- Protection contre les attaques DDoS
- Configuration flexible des limites

### ✅ Audit et conformité
- Traçabilité complète des actions
- Logs d'audit structurés
- Rapports de sécurité
- Conformité RGPD

## 📁 Structure

```
apps/security/
├── models/
│   ├── security_event.py      # Événements de sécurité
│   ├── blocked_ip.py         # IPs bloquées
│   ├── security_alert.py     # Alertes de sécurité
│   ├── audit_log.py          # Logs d'audit
│   └── security_settings.py  # Configuration sécurité
├── serializers/
│   ├── event_serializers.py  # Sérialiseurs événements
│   ├── ip_serializers.py     # Sérialiseurs IP
│   ├── alert_serializers.py  # Sérialiseurs alertes
│   └── audit_serializers.py  # Sérialiseurs audit
├── views/
│   ├── event_views.py        # Vues événements
│   ├── ip_views.py          # Vues IP
│   ├── alert_views.py       # Vues alertes
│   └── audit_views.py       # Vues audit
├── services/
│   ├── security_service.py   # Service sécurité
│   ├── ip_service.py        # Service IP
│   ├── alert_service.py     # Service alertes
│   └── audit_service.py     # Service audit
├── middleware/
│   ├── ip_blocking_middleware.py # Middleware blocage IP
│   ├── rate_limiting_middleware.py # Middleware rate limiting
│   └── security_monitoring_middleware.py # Middleware monitoring
└── utils/
    ├── ip_utils.py          # Utilitaires IP
    └── security_utils.py    # Utilitaires sécurité
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration de sécurité
SECURITY_ENABLED=true
SECURITY_LOG_LEVEL=INFO
SECURITY_RETENTION_DAYS=365

# Configuration IP
IP_BLOCKING_ENABLED=true
IP_WHITELIST_ENABLED=true
IP_GEOLOCATION_ENABLED=true
IP_BLOCK_DURATION=3600  # 1 heure en secondes

# Configuration Rate Limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_PER_IP=100  # requêtes par heure
RATE_LIMIT_PER_USER=1000  # requêtes par heure
RATE_LIMIT_BURST=10  # requêtes par minute

# Configuration des alertes
SECURITY_ALERTS_ENABLED=true
ALERT_EMAIL_RECIPIENTS=admin@example.com,security@example.com
ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/...
```

### Middleware requis

```python
# settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.security.middleware.ip_blocking_middleware.IPBlockingMiddleware',
    'apps.security.middleware.rate_limiting_middleware.RateLimitingMiddleware',
    'apps.security.middleware.security_monitoring_middleware.SecurityMonitoringMiddleware',
]
```

## 📡 APIs disponibles

### 🚨 Gestion des événements de sécurité

#### Lister les événements de sécurité
```http
GET /api/security/events/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "event_type": "failed_login",
      "severity": "medium",
      "description": "Tentative de connexion échouée",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "user": {
        "id": 123,
        "email": "user@example.com"
      },
      "metadata": {
        "attempts": 3,
        "username": "user@example.com"
      },
      "location": {
        "country": "France",
        "city": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522
      },
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### Créer un événement de sécurité
```http
POST /api/security/events/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "event_type": "suspicious_activity",
  "severity": "high",
  "description": "Activité suspecte détectée",
  "ip_address": "192.168.1.100",
  "metadata": {
    "activity_type": "multiple_failed_logins",
    "attempts": 10
  }
}
```

#### Rechercher des événements
```http
GET /api/security/events/search/?event_type=failed_login&severity=high&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### 🚫 Gestion des IPs bloquées

#### Lister les IPs bloquées
```http
GET /api/security/blocked-ips/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "ip_address": "192.168.1.100",
      "reason": "Multiple failed login attempts",
      "blocked_at": "2024-01-01T10:00:00Z",
      "expires_at": "2024-01-01T11:00:00Z",
      "is_active": true,
      "blocked_by": {
        "id": 1,
        "email": "admin@example.com"
      },
      "location": {
        "country": "France",
        "city": "Paris"
      }
    }
  ]
}
```

#### Bloquer une IP
```http
POST /api/security/block-ip/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "ip_address": "192.168.1.100",
  "reason": "Tentative d'intrusion détectée",
  "duration": 3600,
  "auto_block": false
}
```

#### Débloquer une IP
```http
DELETE /api/security/blocked-ips/{id}/
Authorization: Bearer <access_token>
```

#### Ajouter une IP à la liste blanche
```http
POST /api/security/whitelist-ip/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "ip_address": "192.168.1.100",
  "reason": "IP de confiance",
  "permanent": true
}
```

### 🚨 Gestion des alertes

#### Lister les alertes de sécurité
```http
GET /api/security/alerts/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "alert_type": "intrusion_detected",
      "severity": "critical",
      "title": "Tentative d'intrusion détectée",
      "description": "Multiple tentatives de connexion échouées depuis la même IP",
      "ip_address": "192.168.1.100",
      "status": "active",
      "triggered_at": "2024-01-01T10:00:00Z",
      "resolved_at": null,
      "metadata": {
        "failed_attempts": 15,
        "time_window": "5 minutes"
      }
    }
  ]
}
```

#### Créer une alerte
```http
POST /api/security/alerts/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "alert_type": "suspicious_activity",
  "severity": "high",
  "title": "Activité suspecte",
  "description": "Activité suspecte détectée sur le système",
  "ip_address": "192.168.1.100",
  "metadata": {
    "activity_type": "data_exfiltration",
    "data_size": "10MB"
  }
}
```

#### Résoudre une alerte
```http
PUT /api/security/alerts/{id}/resolve/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "resolution_notes": "IP bloquée et utilisateur notifié"
}
```

### 📊 Audit et logs

#### Lister les logs d'audit
```http
GET /api/security/audit-logs/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 5000,
  "results": [
    {
      "id": 1,
      "action": "user_login",
      "user": {
        "id": 123,
        "email": "user@example.com"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "resource": "authentication",
      "resource_id": 123,
      "metadata": {
        "login_method": "email",
        "success": true
      },
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### Rechercher dans les logs d'audit
```http
GET /api/security/audit-logs/search/?action=user_login&user_id=123&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### 📈 Statistiques de sécurité

#### Récupérer les statistiques
```http
GET /api/security/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "total_events": 10000,
  "events_by_type": {
    "failed_login": 5000,
    "suspicious_activity": 2000,
    "intrusion_attempt": 1000,
    "data_breach": 100
  },
  "events_by_severity": {
    "low": 3000,
    "medium": 4000,
    "high": 2500,
    "critical": 500
  },
  "blocked_ips": {
    "total": 150,
    "active": 50,
    "auto_blocked": 100,
    "manually_blocked": 50
  },
  "alerts": {
    "total": 200,
    "active": 25,
    "resolved": 175
  },
  "top_threat_ips": [
    {
      "ip_address": "192.168.1.100",
      "event_count": 150,
      "last_seen": "2024-01-01T10:00:00Z"
    }
  ],
  "security_score": 85
}
```

## 🛠️ Utilisation dans le code

### Service de sécurité

```python
from apps.security.services import SecurityService

security_service = SecurityService()

# Enregistrer un événement de sécurité
security_service.record_event(
    event_type="failed_login",
    severity="medium",
    description="Tentative de connexion échouée",
    ip_address="192.168.1.100",
    user=user,
    metadata={"attempts": 3}
)

# Vérifier si une IP est bloquée
is_blocked = security_service.is_ip_blocked("192.168.1.100")

# Bloquer une IP
security_service.block_ip(
    ip_address="192.168.1.100",
    reason="Multiple failed login attempts",
    duration=3600
)
```

### Service d'alertes

```python
from apps.security.services import AlertService

alert_service = AlertService()

# Créer une alerte
alert = alert_service.create_alert(
    alert_type="intrusion_detected",
    severity="critical",
    title="Tentative d'intrusion",
    description="Multiple tentatives de connexion échouées",
    ip_address="192.168.1.100"
)

# Résoudre une alerte
alert_service.resolve_alert(
    alert_id=alert.id,
    resolution_notes="IP bloquée automatiquement"
)
```

### Service d'audit

```python
from apps.security.services import AuditService

audit_service = AuditService()

# Enregistrer une action d'audit
audit_service.log_action(
    action="user_login",
    user=user,
    ip_address="192.168.1.100",
    resource="authentication",
    resource_id=user.id,
    metadata={"login_method": "email"}
)

# Récupérer l'historique d'audit
audit_logs = audit_service.get_audit_logs(
    user=user,
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Middleware de sécurité

```python
# Le middleware surveille automatiquement:
# - Les tentatives de connexion
# - Les accès aux ressources sensibles
# - Les activités suspectes
# - Les violations de sécurité

# Dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.security.middleware.ip_blocking_middleware.IPBlockingMiddleware',
    'apps.security.middleware.rate_limiting_middleware.RateLimitingMiddleware',
    'apps.security.middleware.security_monitoring_middleware.SecurityMonitoringMiddleware',
]
```

### Décorateurs de sécurité

```python
from apps.security.decorators import security_required, audit_required

@security_required('high')
@audit_required('sensitive_action')
def sensitive_view(request):
    """Vue nécessitant un niveau de sécurité élevé"""
    # Le décorateur enregistre automatiquement:
    # - L'accès à la ressource
    # - Les tentatives d'accès non autorisées
    # - Les violations de sécurité
    pass
```

## 🔧 Configuration avancée

### Configuration des événements de sécurité

```python
# settings.py
SECURITY_EVENTS = {
    'failed_login': {
        'severity': 'medium',
        'auto_block_threshold': 5,
        'block_duration': 3600
    },
    'intrusion_attempt': {
        'severity': 'critical',
        'auto_block_threshold': 1,
        'block_duration': 86400
    },
    'data_breach': {
        'severity': 'critical',
        'auto_block_threshold': 1,
        'block_duration': 86400
    }
}
```

### Configuration du rate limiting

```python
# Configuration du rate limiting
RATE_LIMITING = {
    'default': {
        'requests_per_hour': 1000,
        'requests_per_minute': 100,
        'burst_limit': 10
    },
    'api': {
        'requests_per_hour': 5000,
        'requests_per_minute': 500,
        'burst_limit': 50
    },
    'auth': {
        'requests_per_hour': 100,
        'requests_per_minute': 10,
        'burst_limit': 5
    }
}
```

### Configuration des alertes

```python
# Règles d'alerte par défaut
SECURITY_ALERT_RULES = [
    {
        'name': 'Multiple Failed Logins',
        'condition': 'failed_login_count > 5',
        'severity': 'high',
        'auto_block': True,
        'notification_channels': ['email', 'slack']
    },
    {
        'name': 'Intrusion Attempt',
        'condition': 'intrusion_attempt_count > 0',
        'severity': 'critical',
        'auto_block': True,
        'notification_channels': ['email', 'slack', 'sms']
    }
]
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.security

# Tests avec couverture
coverage run --source='apps.security' manage.py test apps.security
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.security.services import SecurityService, AlertService

class SecurityServiceTestCase(TestCase):
    def setUp(self):
        self.security_service = SecurityService()
        self.alert_service = AlertService()
    
    def test_record_security_event(self):
        event = self.security_service.record_event(
            event_type="failed_login",
            severity="medium",
            description="Test event",
            ip_address="192.168.1.100"
        )
        
        self.assertEqual(event.event_type, "failed_login")
        self.assertEqual(event.severity, "medium")
        self.assertEqual(event.ip_address, "192.168.1.100")
    
    def test_block_ip(self):
        blocked_ip = self.security_service.block_ip(
            ip_address="192.168.1.100",
            reason="Test block",
            duration=3600
        )
        
        self.assertEqual(blocked_ip.ip_address, "192.168.1.100")
        self.assertEqual(blocked_ip.reason, "Test block")
        self.assertTrue(blocked_ip.is_active)
    
    def test_create_alert(self):
        alert = self.alert_service.create_alert(
            alert_type="intrusion_detected",
            severity="critical",
            title="Test Alert",
            description="Test alert description",
            ip_address="192.168.1.100"
        )
        
        self.assertEqual(alert.alert_type, "intrusion_detected")
        self.assertEqual(alert.severity, "critical")
        self.assertEqual(alert.status, "active")
```

## 📊 Intégration avec des outils externes

### Intégration avec des SIEM

```python
# Export vers des systèmes SIEM
class SIEMExportService:
    def export_to_siem(self, events, siem_type='splunk'):
        if siem_type == 'splunk':
            return self.export_to_splunk(events)
        elif siem_type == 'elasticsearch':
            return self.export_to_elasticsearch(events)
    
    def export_to_splunk(self, events):
        # Format Splunk
        splunk_data = []
        for event in events:
            splunk_data.append({
                'time': event.timestamp.isoformat(),
                'source': 'django_security',
                'sourcetype': 'security_event',
                'event': {
                    'event_type': event.event_type,
                    'severity': event.severity,
                    'ip_address': event.ip_address,
                    'description': event.description
                }
            })
        return splunk_data
```

### Intégration avec des services de géolocalisation

```python
# Service de géolocalisation
class GeolocationService:
    def get_ip_location(self, ip_address):
        # Utiliser un service comme MaxMind ou IPinfo
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()
        
        return {
            'country': data.get('country'),
            'city': data.get('city'),
            'latitude': data.get('loc', '').split(',')[0],
            'longitude': data.get('loc', '').split(',')[1]
        }
```

## 🐛 Dépannage

### Problèmes courants

1. **IP bloquée par erreur** : Vérifiez les règles de blocage automatique
2. **Rate limiting trop strict** : Ajustez les limites dans la configuration
3. **Alertes non envoyées** : Vérifiez la configuration des notifications
4. **Performance lente** : Optimisez les requêtes et activez le cache

### Configuration de debug

```python
# settings.py
DEBUG_SECURITY = True
SECURITY_LOG_LEVEL = 'DEBUG'
IP_BLOCKING_DEBUG = True
RATE_LIMITING_DEBUG = True
```

## 📚 Ressources

- [OWASP Security](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Rate Limiting](https://en.wikipedia.org/wiki/Rate_limiting)
- [IP Geolocation](https://en.wikipedia.org/wiki/Geolocation)

---

*Dernière mise à jour: Septembre 2024*
