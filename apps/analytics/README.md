# 📈 Analytics App

## Vue d'ensemble

L'app **Analytics** fournit un système complet d'analytics et de reporting avec tableaux de bord personnalisables, rapports automatisés, métriques personnalisées et export de données.

## 🚀 Fonctionnalités

### ✅ Tableaux de bord personnalisables
- Widgets configurables (graphiques, compteurs, tableaux)
- Mise en page drag & drop
- Partage de tableaux de bord
- Tableaux de bord publics/privés

### ✅ Rapports automatisés
- Templates de rapports personnalisables
- Génération automatique de rapports
- Planification de rapports
- Export multi-formats (PDF, Excel, CSV)

### ✅ Métriques personnalisées
- Définition de métriques métier
- Calculs en temps réel
- Agrégations et groupements
- Historique des métriques

### ✅ Export de données
- Export en temps réel
- Formats multiples (CSV, Excel, PDF, JSON)
- Filtrage et pagination
- Planification d'exports

## 📁 Structure

```
apps/analytics/
├── models/
│   ├── dashboard.py           # Tableaux de bord
│   ├── dashboard_widget.py    # Widgets
│   ├── report_template.py     # Templates de rapport
│   ├── report.py             # Rapports
│   ├── custom_metric.py      # Métriques personnalisées
│   └── data_export.py        # Exports de données
├── serializers/
│   ├── dashboard_serializers.py # Sérialiseurs tableaux de bord
│   ├── report_serializers.py    # Sérialiseurs rapports
│   ├── metric_serializers.py    # Sérialiseurs métriques
│   └── export_serializers.py    # Sérialiseurs exports
├── views/
│   ├── dashboard_views.py       # Vues tableaux de bord
│   ├── report_views.py         # Vues rapports
│   ├── metric_views.py         # Vues métriques
│   └── export_views.py         # Vues exports
├── services/
│   ├── dashboard_service.py     # Service tableaux de bord
│   ├── report_service.py       # Service rapports
│   ├── metric_service.py       # Service métriques
│   └── export_service.py       # Service exports
└── utils/
    ├── chart_utils.py          # Utilitaires graphiques
    └── data_utils.py           # Utilitaires données
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration des analytics
ANALYTICS_ENABLED=true
DASHBOARD_CACHE_TTL=300  # 5 minutes
REPORT_GENERATION_TIMEOUT=300  # 5 minutes
EXPORT_MAX_SIZE=10000  # Nombre max d'enregistrements

# Configuration des rapports
REPORT_STORAGE_PATH=/tmp/reports
REPORT_RETENTION_DAYS=30
REPORT_FORMATS=pdf,excel,csv

# Configuration des exports
EXPORT_STORAGE_PATH=/tmp/exports
EXPORT_RETENTION_DAYS=7
EXPORT_MAX_FILE_SIZE=100MB
```

### Dépendances requises

```bash
pip install xlsxwriter reportlab pandas matplotlib seaborn
```

## 📡 APIs disponibles

### 📊 Gestion des tableaux de bord

#### Lister les tableaux de bord
```http
GET /api/analytics/dashboards/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "User Analytics",
      "description": "Analytics des utilisateurs",
      "dashboard_type": "user_analytics",
      "is_public": false,
      "owner": {
        "id": 123,
        "email": "admin@example.com"
      },
      "widgets_count": 8,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer un tableau de bord
```http
POST /api/analytics/dashboards/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Sales Dashboard",
  "description": "Tableau de bord des ventes",
  "dashboard_type": "sales",
  "is_public": false,
  "layout_config": {
    "grid_size": 12,
    "widgets": []
  }
}
```

#### Récupérer les données d'un tableau de bord
```http
GET /api/analytics/dashboards/{id}/data/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "dashboard": {
    "id": 1,
    "name": "User Analytics",
    "description": "Analytics des utilisateurs"
  },
  "widgets": [
    {
      "id": 1,
      "name": "Active Users",
      "type": "counter",
      "data": {
        "value": 1250,
        "change": "+5.2%",
        "trend": "up"
      }
    },
    {
      "id": 2,
      "name": "User Registrations",
      "type": "line_chart",
      "data": {
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "datasets": [
          {
            "label": "Registrations",
            "data": [100, 150, 200, 180],
            "borderColor": "#3B82F6"
          }
        ]
      }
    }
  ]
}
```

#### Partager un tableau de bord
```http
POST /api/analytics/dashboards/{id}/share/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_emails": ["user1@example.com", "user2@example.com"],
  "permissions": ["view"]
}
```

### 📋 Gestion des rapports

#### Lister les rapports
```http
GET /api/analytics/reports/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Monthly User Report",
      "template": {
        "id": 1,
        "name": "User Report Template"
      },
      "status": "completed",
      "format": "pdf",
      "file_size": "2.5MB",
      "created_at": "2024-01-01T00:00:00Z",
      "generated_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

#### Créer un rapport
```http
POST /api/analytics/reports/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "template": 1,
  "name": "Weekly Sales Report",
  "format": "excel",
  "parameters": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
    "include_charts": true
  }
}
```

#### Télécharger un rapport
```http
GET /api/analytics/reports/{id}/download/
Authorization: Bearer <access_token>
```

### 📊 Gestion des métriques

#### Lister les métriques personnalisées
```http
GET /api/analytics/metrics/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "user_engagement_rate",
      "description": "Taux d'engagement des utilisateurs",
      "metric_type": "percentage",
      "calculation_method": "custom",
      "query": "SELECT COUNT(*) FROM user_actions WHERE created_at > NOW() - INTERVAL 1 DAY",
      "aggregation": "daily",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer une métrique personnalisée
```http
POST /api/analytics/metrics/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "conversion_rate",
  "description": "Taux de conversion",
  "metric_type": "percentage",
  "calculation_method": "sql",
  "query": "SELECT (COUNT(*) FILTER (WHERE status = 'converted') * 100.0 / COUNT(*)) FROM orders",
  "aggregation": "daily",
  "labels": ["product", "campaign"]
}
```

#### Récupérer les données d'une métrique
```http
GET /api/analytics/metrics/{id}/data/?start_date=2024-01-01&end_date=2024-01-31&aggregation=daily
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "metric": {
    "id": 1,
    "name": "user_engagement_rate",
    "description": "Taux d'engagement des utilisateurs"
  },
  "data": [
    {
      "date": "2024-01-01",
      "value": 75.5,
      "labels": {}
    },
    {
      "date": "2024-01-02",
      "value": 78.2,
      "labels": {}
    }
  ],
  "summary": {
    "average": 76.8,
    "min": 72.1,
    "max": 82.5,
    "trend": "up"
  }
}
```

### 📤 Gestion des exports

#### Créer un export
```http
POST /api/analytics/exports/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "User Data Export",
  "data_source": "users",
  "format": "excel",
  "filters": {
    "created_at__gte": "2024-01-01",
    "is_active": true
  },
  "fields": ["id", "email", "first_name", "last_name", "created_at"],
  "schedule": {
    "frequency": "daily",
    "time": "09:00"
  }
}
```

#### Lister les exports
```http
GET /api/analytics/exports/
Authorization: Bearer <access_token>
```

#### Télécharger un export
```http
GET /api/analytics/exports/{id}/download/
Authorization: Bearer <access_token>
```

## 🛠️ Utilisation dans le code

### Service de tableaux de bord

```python
from apps.analytics.services import DashboardService

dashboard_service = DashboardService()

# Créer un tableau de bord
dashboard = dashboard_service.create_dashboard(
    name="User Analytics",
    description="Analytics des utilisateurs",
    dashboard_type="user_analytics",
    owner=request.user
)

# Ajouter un widget
widget = dashboard_service.add_widget(
    dashboard=dashboard,
    name="Active Users",
    widget_type="counter",
    config={
        "metric": "active_users",
        "refresh_interval": 300
    }
)

# Récupérer les données
data = dashboard_service.get_dashboard_data(dashboard.id, request.user)
```

### Service de rapports

```python
from apps.analytics.services import ReportService

report_service = ReportService()

# Créer un template de rapport
template = report_service.create_template(
    name="User Report Template",
    description="Template pour les rapports utilisateur",
    query="SELECT * FROM users WHERE created_at >= %(start_date)s",
    parameters=["start_date", "end_date"],
    format="pdf"
)

# Générer un rapport
report = report_service.generate_report(
    template=template,
    name="Monthly User Report",
    parameters={
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
)

# Planifier un rapport
report_service.schedule_report(
    template=template,
    name="Weekly User Report",
    schedule="weekly",
    parameters={"start_date": "auto", "end_date": "auto"}
)
```

### Service de métriques

```python
from apps.analytics.services import MetricService

metric_service = MetricService()

# Créer une métrique personnalisée
metric = metric_service.create_metric(
    name="user_retention_rate",
    description="Taux de rétention des utilisateurs",
    metric_type="percentage",
    calculation_method="sql",
    query="""
        SELECT 
            COUNT(DISTINCT user_id) FILTER (WHERE created_at >= %(start_date)s) * 100.0 / 
            COUNT(DISTINCT user_id) FILTER (WHERE created_at < %(start_date)s)
        FROM user_actions
    """,
    aggregation="monthly"
)

# Calculer la métrique
value = metric_service.calculate_metric(
    metric=metric,
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Récupérer l'historique
history = metric_service.get_metric_history(
    metric=metric,
    start_date="2024-01-01",
    end_date="2024-01-31",
    aggregation="daily"
)
```

### Service d'exports

```python
from apps.analytics.services import ExportService

export_service = ExportService()

# Créer un export
export = export_service.create_export(
    name="User Data Export",
    data_source="users",
    format="excel",
    filters={
        "created_at__gte": "2024-01-01",
        "is_active": True
    },
    fields=["id", "email", "first_name", "last_name", "created_at"]
)

# Générer l'export
file_path = export_service.generate_export(export)

# Planifier un export
export_service.schedule_export(
    export=export,
    frequency="daily",
    time="09:00"
)
```

## 📊 Types de widgets disponibles

### Counter (Compteur)
```json
{
  "type": "counter",
  "config": {
    "metric": "active_users",
    "format": "number",
    "show_change": true,
    "show_trend": true
  }
}
```

### Line Chart (Graphique linéaire)
```json
{
  "type": "line_chart",
  "config": {
    "metric": "user_registrations",
    "aggregation": "daily",
    "period": "30d",
    "show_legend": true,
    "show_grid": true
  }
}
```

### Bar Chart (Graphique en barres)
```json
{
  "type": "bar_chart",
  "config": {
    "metric": "sales_by_category",
    "group_by": "category",
    "period": "7d",
    "orientation": "vertical"
  }
}
```

### Pie Chart (Graphique en secteurs)
```json
{
  "type": "pie_chart",
  "config": {
    "metric": "user_distribution",
    "group_by": "country",
    "limit": 10,
    "show_percentages": true
  }
}
```

### Table (Tableau)
```json
{
  "type": "table",
  "config": {
    "data_source": "users",
    "columns": ["id", "email", "created_at"],
    "filters": {"is_active": true},
    "pagination": true,
    "page_size": 20
  }
}
```

### Gauge (Jauge)
```json
{
  "type": "gauge",
  "config": {
    "metric": "system_health",
    "min_value": 0,
    "max_value": 100,
    "thresholds": [
      {"value": 80, "color": "green"},
      {"value": 60, "color": "yellow"},
      {"value": 40, "color": "red"}
    ]
  }
}
```

## 🔧 Configuration avancée

### Configuration des métriques

```python
# settings.py
ANALYTICS_METRICS = {
    'user_engagement': {
        'type': 'percentage',
        'calculation': 'custom',
        'query': 'SELECT COUNT(*) FROM user_actions WHERE created_at > NOW() - INTERVAL 1 DAY',
        'aggregation': 'daily'
    },
    'conversion_rate': {
        'type': 'percentage',
        'calculation': 'sql',
        'query': 'SELECT (COUNT(*) FILTER (WHERE status = "converted") * 100.0 / COUNT(*)) FROM orders',
        'aggregation': 'daily'
    }
}
```

### Configuration des rapports

```python
# Templates de rapports par défaut
DEFAULT_REPORT_TEMPLATES = [
    {
        'name': 'User Activity Report',
        'description': 'Rapport d\'activité des utilisateurs',
        'query': 'SELECT * FROM user_actions WHERE created_at >= %(start_date)s',
        'parameters': ['start_date', 'end_date'],
        'format': 'pdf'
    },
    {
        'name': 'Sales Summary',
        'description': 'Résumé des ventes',
        'query': 'SELECT product, SUM(amount) as total FROM sales WHERE date >= %(start_date)s GROUP BY product',
        'parameters': ['start_date', 'end_date'],
        'format': 'excel'
    }
]
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.analytics

# Tests avec couverture
coverage run --source='apps.analytics' manage.py test apps.analytics
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.analytics.services import DashboardService, ReportService

class AnalyticsServiceTestCase(TestCase):
    def setUp(self):
        self.dashboard_service = DashboardService()
        self.report_service = ReportService()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
    
    def test_create_dashboard(self):
        dashboard = self.dashboard_service.create_dashboard(
            name="Test Dashboard",
            description="Test description",
            dashboard_type="test",
            owner=self.user
        )
        
        self.assertEqual(dashboard.name, "Test Dashboard")
        self.assertEqual(dashboard.owner, self.user)
        self.assertFalse(dashboard.is_public)
    
    def test_generate_report(self):
        template = self.report_service.create_template(
            name="Test Template",
            description="Test template",
            query="SELECT 1 as test",
            parameters=[],
            format="pdf"
        )
        
        report = self.report_service.generate_report(
            template=template,
            name="Test Report",
            parameters={}
        )
        
        self.assertEqual(report.template, template)
        self.assertEqual(report.name, "Test Report")
        self.assertEqual(report.status, "completed")
```

## 📊 Intégration avec des outils externes

### Grafana

```python
# Configuration des dashboards Grafana
GRAFANA_DASHBOARDS = {
    'user_analytics': {
        'title': 'User Analytics',
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
            }
        ]
    }
}
```

### Tableau

```python
# Export vers Tableau
class TableauExportService:
    def export_to_tableau(self, data, filename):
        # Convertir les données au format Tableau
        tableau_data = self.convert_to_tableau_format(data)
        
        # Créer le fichier .twbx
        with open(filename, 'wb') as f:
            f.write(tableau_data)
        
        return filename
```

## 🐛 Dépannage

### Problèmes courants

1. **Rapport non généré** : Vérifiez les permissions et la configuration
2. **Métriques incorrectes** : Vérifiez les requêtes SQL
3. **Export échoué** : Vérifiez la taille des données et les limites
4. **Performance lente** : Optimisez les requêtes et activez le cache

### Configuration de debug

```python
# settings.py
DEBUG_ANALYTICS = True
ANALYTICS_LOG_LEVEL = 'DEBUG'
REPORT_DEBUG = True
```

## 📚 Ressources

- [Django ORM](https://docs.djangoproject.com/en/stable/topics/db/queries/)
- [Pandas](https://pandas.pydata.org/docs/)
- [Matplotlib](https://matplotlib.org/stable/index.html)
- [ReportLab](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

*Dernière mise à jour: Septembre 2024*
