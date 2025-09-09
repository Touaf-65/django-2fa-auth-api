# 📊 Monitoring App

## Vue d'ensemble

L'app **Monitoring** fournit un système complet de monitoring et d'observabilité avec logs structurés, métriques personnalisées, alertes configurables et dashboards de monitoring.

## 🚀 Fonctionnalités

### ✅ Logs structurés
- Logs avec niveaux (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Métadonnées enrichies (utilisateur, IP, user-agent)
- Tags et catégories personnalisables
- Rotation automatique des logs

### ✅ Métriques personnalisées
- **Counters** : Compteurs d'événements
- **Gauges** : Valeurs instantanées
- **Histograms** : Distribution des valeurs
- **Timers** : Mesure des durées

### ✅ Alertes configurables
- Règles d'alerte personnalisables
- Notifications multi-canaux (email, SMS, webhook)
- Escalade automatique
- Historique des alertes

### ✅ Dashboards de monitoring
- Tableaux de bord personnalisables
- Widgets de métriques
- Visualisations en temps réel
- Export des données

## 📁 Structure

```
apps/monitoring/
├── models/
│   ├── log_entry.py           # Entrées de log
│   ├── metric.py             # Métriques
│   ├── alert.py              # Alertes
│   ├── alert_rule.py         # Règles d'alerte
│   ├── dashboard.py          # Tableaux de bord
│   └── monitoring_config.py  # Configuration
├── serializers/
│   ├── log_serializers.py    # Sérialiseurs logs
│   ├── metric_serializers.py # Sérialiseurs métriques
│   ├── alert_serializers.py  # Sérialiseurs alertes
│   └── dashboard_serializers.py # Sérialiseurs dashboards
├── views/
│   ├── log_views.py          # Vues logs
│   ├── metric_views.py       # Vues métriques
│   ├── alert_views.py        # Vues alertes
│   └── dashboard_views.py    # Vues dashboards
├── services/
│   ├── logging_service.py    # Service de logging
│   ├── metrics_service.py    # Service de métriques
│   ├── alert_service.py      # Service d'alertes
│   └── dashboard_service.py  # Service de dashboards
├── middleware/
│   └── monitoring_middleware.py # Middleware de monitoring
└── utils/
    ├── log_utils.py          # Utilitaires de log
    └── metric_utils.py       # Utilitaires de métriques
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration du monitoring
MONITORING_ENABLED=true
LOG_LEVEL=INFO
METRICS_ENABLED=true
ALERTS_ENABLED=true

# Configuration des logs
LOG_RETENTION_DAYS=30
LOG_MAX_SIZE=100MB
LOG_ROTATION_COUNT=10

# Configuration des métriques
METRICS_RETENTION_DAYS=90
METRICS_AGGREGATION_INTERVAL=300  # 5 minutes

# Configuration des alertes
ALERT_CHECK_INTERVAL=60  # 1 minute
ALERT_RETRY_COUNT=3
ALERT_COOLDOWN_PERIOD=300  # 5 minutes
```

### Middleware requis

```python
# settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.monitoring.middleware.monitoring_middleware.MonitoringMiddleware',
]
```

## 📡 APIs disponibles

### 📝 Gestion des logs

#### Lister les logs
```http
GET /api/monitoring/logs/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "level": "INFO",
      "message": "User logged in successfully",
      "user": {
        "id": 123,
        "email": "user@example.com"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "tags": ["authentication", "login"],
      "metadata": {
        "login_method": "email",
        "session_id": "abc123"
      },
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### Créer un log
```http
POST /api/monitoring/logs/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "level": "INFO",
  "message": "Custom log message",
  "tags": ["custom", "test"],
  "metadata": {
    "custom_field": "custom_value"
  }
}
```

#### Rechercher dans les logs
```http
GET /api/monitoring/logs/search/?q=error&level=ERROR&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### 📊 Gestion des métriques

#### Lister les métriques
```http
GET /api/monitoring/metrics/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "name": "user_logins",
      "type": "counter",
      "value": 1250,
      "labels": {
        "method": "email"
      },
      "timestamp": "2024-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "active_users",
      "type": "gauge",
      "value": 150,
      "labels": {},
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### Créer une métrique
```http
POST /api/monitoring/metrics/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "api_requests",
  "type": "counter",
  "value": 1,
  "labels": {
    "endpoint": "/api/users/",
    "method": "GET",
    "status": "200"
  }
}
```

#### Récupérer les statistiques des métriques
```http
GET /api/monitoring/metrics/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "total_metrics": 50,
  "metrics_by_type": {
    "counter": 25,
    "gauge": 15,
    "histogram": 10
  },
  "top_metrics": [
    {
      "name": "user_logins",
      "value": 1250,
      "type": "counter"
    },
    {
      "name": "active_users",
      "value": 150,
      "type": "gauge"
    }
  ],
  "recent_metrics": [
    {
      "name": "api_requests",
      "value": 100,
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 🚨 Gestion des alertes

#### Lister les alertes
```http
GET /api/monitoring/alerts/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "High Error Rate",
      "description": "Taux d'erreur élevé détecté",
      "status": "active",
      "severity": "high",
      "condition": "error_rate > 5%",
      "threshold": 5,
      "current_value": 7.5,
      "triggered_at": "2024-01-01T10:00:00Z",
      "notification_channels": ["email", "slack"]
    }
  ]
}
```

#### Créer une alerte
```http
POST /api/monitoring/alerts/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Low Memory Warning",
  "description": "Mémoire disponible faible",
  "condition": "memory_usage > 90%",
  "threshold": 90,
  "severity": "medium",
  "notification_channels": ["email"],
  "cooldown_period": 300
}
```

#### Créer une règle d'alerte
```http
POST /api/monitoring/alert-rules/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "API Error Rate",
  "description": "Surveille le taux d'erreur des APIs",
  "metric_name": "api_error_rate",
  "condition": ">",
  "threshold": 5,
  "evaluation_interval": 60,
  "notification_channels": ["email", "slack"]
}
```

### 📈 Dashboards de monitoring

#### Lister les dashboards
```http
GET /api/monitoring/dashboards/
Authorization: Bearer <access_token>
```

#### Créer un dashboard
```http
POST /api/monitoring/dashboards/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "System Overview",
  "description": "Vue d'ensemble du système",
  "is_public": false,
  "widgets": [
    {
      "name": "Active Users",
      "type": "gauge",
      "metric_name": "active_users",
      "position": {"x": 0, "y": 0, "width": 6, "height": 4}
    },
    {
      "name": "API Requests",
      "type": "line_chart",
      "metric_name": "api_requests",
      "position": {"x": 6, "y": 0, "width": 6, "height": 4}
    }
  ]
}
```

## 🛠️ Utilisation dans le code

### Service de logging

```python
from apps.monitoring.services import LoggingService

logging_service = LoggingService()

# Log simple
logging_service.log('INFO', 'User action performed', user=request.user)

# Log avec métadonnées
logging_service.log(
    level='ERROR',
    message='Database connection failed',
    tags=['database', 'error'],
    metadata={
        'database': 'postgresql',
        'host': 'localhost',
        'port': 5432
    }
)

# Log avec contexte de requête
logging_service.log_request(
    level='INFO',
    message='API request processed',
    request=request,
    response_time=0.5
)
```

### Service de métriques

```python
from apps.monitoring.services import MetricsService

metrics_service = MetricsService()

# Counter (compteur)
metrics_service.increment_counter(
    name='user_logins',
    labels={'method': 'email'}
)

# Gauge (valeur instantanée)
metrics_service.set_gauge(
    name='active_users',
    value=150,
    labels={'region': 'us-east'}
)

# Histogram (distribution)
metrics_service.record_histogram(
    name='response_time',
    value=0.5,
    labels={'endpoint': '/api/users/'}
)

# Timer (mesure de durée)
with metrics_service.timer('database_query'):
    # Code à mesurer
    result = database.query()
```

### Service d'alertes

```python
from apps.monitoring.services import AlertService

alert_service = AlertService()

# Créer une alerte
alert = alert_service.create_alert(
    name='High CPU Usage',
    description='CPU usage is above threshold',
    condition='cpu_usage > 80%',
    threshold=80,
    severity='high'
)

# Déclencher une alerte
alert_service.trigger_alert(
    alert_id=alert.id,
    current_value=85,
    message='CPU usage is at 85%'
)

# Résoudre une alerte
alert_service.resolve_alert(alert_id=alert.id)
```

### Middleware de monitoring

```python
# Le middleware enregistre automatiquement:
# - Les requêtes HTTP
# - Les temps de réponse
# - Les erreurs
# - Les métriques de performance

# Dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.monitoring.middleware.monitoring_middleware.MonitoringMiddleware',
]
```

### Décorateurs de monitoring

```python
from apps.monitoring.decorators import monitor_performance, log_action

@monitor_performance('user_creation')
@log_action('create_user')
def create_user(request):
    """Création d'utilisateur avec monitoring automatique"""
    # Le décorateur enregistre automatiquement:
    # - Le temps d'exécution
    # - Les métriques de performance
    # - Les logs d'action
    pass
```

## 🔧 Configuration avancée

### Configuration des logs

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'monitoring': {
            'level': 'INFO',
            'class': 'apps.monitoring.handlers.MonitoringHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'apps.monitoring': {
            'handlers': ['file', 'monitoring'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Configuration des métriques

```python
# Configuration des métriques personnalisées
CUSTOM_METRICS = {
    'user_actions': {
        'type': 'counter',
        'description': 'Nombre d\'actions utilisateur',
        'labels': ['action_type', 'user_id']
    },
    'api_response_time': {
        'type': 'histogram',
        'description': 'Temps de réponse des APIs',
        'buckets': [0.1, 0.5, 1.0, 2.0, 5.0],
        'labels': ['endpoint', 'method']
    },
    'system_memory': {
        'type': 'gauge',
        'description': 'Utilisation mémoire système',
        'labels': ['host']
    }
}
```

### Configuration des alertes

```python
# Règles d'alerte par défaut
DEFAULT_ALERT_RULES = [
    {
        'name': 'High Error Rate',
        'metric_name': 'error_rate',
        'condition': '>',
        'threshold': 5,
        'severity': 'high',
        'notification_channels': ['email', 'slack']
    },
    {
        'name': 'Low Memory',
        'metric_name': 'memory_usage',
        'condition': '>',
        'threshold': 90,
        'severity': 'medium',
        'notification_channels': ['email']
    }
]
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.monitoring

# Tests avec couverture
coverage run --source='apps.monitoring' manage.py test apps.monitoring
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.monitoring.services import LoggingService, MetricsService

class MonitoringServiceTestCase(TestCase):
    def setUp(self):
        self.logging_service = LoggingService()
        self.metrics_service = MetricsService()
    
    def test_log_creation(self):
        # Créer un log
        log_entry = self.logging_service.log(
            level='INFO',
            message='Test log message',
            tags=['test']
        )
        
        self.assertEqual(log_entry.level, 'INFO')
        self.assertEqual(log_entry.message, 'Test log message')
        self.assertIn('test', log_entry.tags)
    
    def test_metric_creation(self):
        # Créer une métrique
        metric = self.metrics_service.increment_counter(
            name='test_counter',
            labels={'test': 'value'}
        )
        
        self.assertEqual(metric.name, 'test_counter')
        self.assertEqual(metric.type, 'counter')
        self.assertEqual(metric.labels['test'], 'value')
```

## 📊 Intégration avec des outils externes

### Prometheus

```python
# Exporter les métriques vers Prometheus
from prometheus_client import Counter, Gauge, Histogram

# Métriques Prometheus
user_logins = Counter('user_logins_total', 'Total user logins', ['method'])
active_users = Gauge('active_users', 'Number of active users')
response_time = Histogram('response_time_seconds', 'Response time', ['endpoint'])

# Intégration avec le service de métriques
class PrometheusMetricsService(MetricsService):
    def increment_counter(self, name, labels=None):
        if name == 'user_logins':
            user_logins.labels(method=labels.get('method', 'unknown')).inc()
        return super().increment_counter(name, labels)
```

### Grafana

```python
# Configuration des dashboards Grafana
GRAFANA_DASHBOARDS = {
    'system_overview': {
        'title': 'System Overview',
        'panels': [
            {
                'title': 'Active Users',
                'type': 'stat',
                'targets': [
                    {
                        'expr': 'active_users',
                        'legendFormat': 'Active Users'
                    }
                ]
            },
            {
                'title': 'API Response Time',
                'type': 'graph',
                'targets': [
                    {
                        'expr': 'rate(response_time_seconds_sum[5m]) / rate(response_time_seconds_count[5m])',
                        'legendFormat': 'Average Response Time'
                    }
                ]
            }
        ]
    }
}
```

## 🐛 Dépannage

### Problèmes courants

1. **Logs non enregistrés** : Vérifiez la configuration LOGGING
2. **Métriques manquantes** : Vérifiez l'activation du middleware
3. **Alertes non déclenchées** : Vérifiez les règles d'alerte
4. **Performance lente** : Optimisez la rétention des données

### Configuration de debug

```python
# settings.py
DEBUG_MONITORING = True
MONITORING_LOG_LEVEL = 'DEBUG'
METRICS_DEBUG = True
```

## 📚 Ressources

- [Django Logging](https://docs.djangoproject.com/en/stable/topics/logging/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [OpenTelemetry](https://opentelemetry.io/docs/)

---

*Dernière mise à jour: Septembre 2024*
