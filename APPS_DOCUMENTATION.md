# 📚 Documentation des Apps - Django 2FA Auth API Starter

## 🎯 Vue d'ensemble

Ce starter Django comprend **9 apps modulaires** qui peuvent être activées/désactivées selon les besoins du projet. Chaque app est indépendante et peut fonctionner seule ou en combinaison avec d'autres.

## 📋 Table des matières

1. [🔐 Authentication App](#-authentication-app)
2. [👥 Users App](#-users-app)
3. [🔔 Notifications App](#-notifications-app)
4. [🛡️ Security App](#️-security-app)
5. [🔑 Permissions App](#-permissions-app)
6. [⚙️ Admin API App](#️-admin-api-app)
7. [🌐 API App](#-api-app)
8. [📊 Monitoring App](#-monitoring-app)
9. [📈 Analytics App](#-analytics-app)
10. [🌍 Internationalization App](#-internationalization-app)

---

## 🔐 Authentication App

### **Description**
Gestion complète de l'authentification avec support 2FA (TOTP et Email OTP).

### **Fonctionnalités principales**
- ✅ **Inscription/Connexion** avec email et mot de passe
- ✅ **2FA TOTP** (Google Authenticator, Authy)
- ✅ **2FA Email OTP** (codes à usage unique)
- ✅ **JWT Tokens** (access + refresh)
- ✅ **Réinitialisation de mot de passe**
- ✅ **Vérification d'email**
- ✅ **Gestion des sessions**

### **Modèles**
```python
# apps/authentication/models/
├── User                    # Utilisateur étendu
├── TwoFactorAuth          # Configuration 2FA
├── EmailOTP              # Codes OTP par email
├── PasswordResetToken    # Tokens de réinitialisation
└── EmailVerificationToken # Tokens de vérification
```

### **APIs disponibles**
```
POST /api/auth/register/           # Inscription
POST /api/auth/login/              # Connexion
POST /api/auth/logout/             # Déconnexion
POST /api/auth/refresh/            # Rafraîchir token
POST /api/auth/2fa/setup/          # Configurer 2FA
POST /api/auth/2fa/verify/         # Vérifier 2FA
POST /api/auth/password/reset/     # Réinitialiser mot de passe
POST /api/auth/email/verify/       # Vérifier email
```

### **Configuration requise**
```env
# JWT Configuration
JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_password

# 2FA Configuration
TOTP_ISSUER_NAME=YourApp
OTP_VALIDITY_PERIOD=300  # seconds
```

### **Exemple d'utilisation**
```python
# Inscription
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}

# Connexion avec 2FA
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "securepassword123",
  "totp_code": "123456"  # Code TOTP si 2FA activé
}
```

---

## 👥 Users App

### **Description**
Gestion des profils utilisateur et des préférences.

### **Fonctionnalités principales**
- ✅ **Profils utilisateur** complets
- ✅ **Préférences utilisateur** (thème, langue, notifications)
- ✅ **Gestion des avatars**
- ✅ **Historique des connexions**
- ✅ **Statistiques utilisateur**

### **Modèles**
```python
# apps/users/models/
├── UserProfile           # Profil utilisateur étendu
├── UserPreference       # Préférences utilisateur
├── UserAvatar          # Gestion des avatars
├── LoginHistory        # Historique des connexions
└── UserStats           # Statistiques utilisateur
```

### **APIs disponibles**
```
GET    /api/users/profile/           # Profil utilisateur
PUT    /api/users/profile/           # Modifier profil
POST   /api/users/avatar/            # Upload avatar
GET    /api/users/preferences/       # Préférences
PUT    /api/users/preferences/       # Modifier préférences
GET    /api/users/login-history/     # Historique connexions
GET    /api/users/stats/             # Statistiques
```

### **Exemple d'utilisation**
```python
# Récupérer le profil
GET /api/users/profile/
Authorization: Bearer <access_token>

# Modifier le profil
PUT /api/users/profile/
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Développeur passionné"
}
```

---

## 🔔 Notifications App

### **Description**
Système de notifications multicanaux (email, SMS, push, webhook).

### **Fonctionnalités principales**
- ✅ **Notifications email** avec templates
- ✅ **Notifications SMS** (Twilio, etc.)
- ✅ **Notifications push** (Firebase, etc.)
- ✅ **Webhooks** pour intégrations externes
- ✅ **Templates personnalisables**
- ✅ **Planification des notifications**
- ✅ **Historique et statistiques**

### **Modèles**
```python
# apps/notifications/models/
├── NotificationTemplate    # Templates de notifications
├── EmailNotification      # Notifications email
├── SMSNotification        # Notifications SMS
├── PushNotification       # Notifications push
├── WebhookNotification    # Notifications webhook
├── NotificationSchedule   # Planification
└── NotificationHistory    # Historique
```

### **APIs disponibles**
```
GET    /api/notifications/           # Liste des notifications
POST   /api/notifications/send/      # Envoyer notification
GET    /api/notifications/templates/ # Templates
POST   /api/notifications/templates/ # Créer template
GET    /api/notifications/history/   # Historique
POST   /api/notifications/schedule/  # Planifier notification
```

### **Configuration requise**
```env
# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number

# Push (Firebase)
FIREBASE_SERVER_KEY=your_server_key
```

### **Exemple d'utilisation**
```python
# Envoyer une notification email
POST /api/notifications/send/
{
  "type": "email",
  "recipient": "user@example.com",
  "template": "welcome",
  "context": {
    "user_name": "John Doe",
    "app_name": "MyApp"
  }
}
```

---

## 🛡️ Security App

### **Description**
Système de sécurité avancé avec monitoring et protection.

### **Fonctionnalités principales**
- ✅ **Monitoring des événements** de sécurité
- ✅ **Blocage d'IP** automatique
- ✅ **Détection d'intrusion**
- ✅ **Rate limiting** par IP/utilisateur
- ✅ **Audit trail** complet
- ✅ **Alertes de sécurité**

### **Modèles**
```python
# apps/security/models/
├── SecurityEvent        # Événements de sécurité
├── BlockedIP           # IPs bloquées
├── SecurityAlert       # Alertes de sécurité
├── AuditLog           # Logs d'audit
└── SecuritySettings   # Configuration sécurité
```

### **APIs disponibles**
```
GET    /api/security/events/         # Événements de sécurité
GET    /api/security/blocked-ips/    # IPs bloquées
POST   /api/security/block-ip/       # Bloquer IP
GET    /api/security/alerts/         # Alertes
GET    /api/security/audit-logs/     # Logs d'audit
GET    /api/security/stats/          # Statistiques sécurité
```

### **Middleware de sécurité**
```python
# Middleware automatiquement activé
├── IPBlockingMiddleware      # Blocage d'IP
├── RateLimitingMiddleware    # Limitation de débit
├── SecurityMonitoringMiddleware # Monitoring
└── AuditMiddleware          # Audit des actions
```

### **Exemple d'utilisation**
```python
# Récupérer les événements de sécurité
GET /api/security/events/
Authorization: Bearer <access_token>

# Bloquer une IP
POST /api/security/block-ip/
{
  "ip_address": "192.168.1.100",
  "reason": "Tentative d'intrusion",
  "duration": 3600  # 1 heure
}
```

---

## 🔑 Permissions App

### **Description**
Système de permissions avancé avec RBAC et ABAC.

### **Fonctionnalités principales**
- ✅ **RBAC** (Role-Based Access Control)
- ✅ **ABAC** (Attribute-Based Access Control)
- ✅ **Délégation de permissions**
- ✅ **Permissions dynamiques**
- ✅ **Audit des permissions**
- ✅ **Gestion des groupes**

### **Modèles**
```python
# apps/permissions/models/
├── Permission          # Permissions
├── Role               # Rôles
├── Group              # Groupes
├── UserRole           # Rôles utilisateur
├── PermissionDelegation # Délégation
└── PermissionAudit    # Audit permissions
```

### **APIs disponibles**
```
GET    /api/permissions/             # Liste des permissions
POST   /api/permissions/             # Créer permission
GET    /api/roles/                   # Liste des rôles
POST   /api/roles/                   # Créer rôle
GET    /api/groups/                  # Liste des groupes
POST   /api/groups/                  # Créer groupe
POST   /api/permissions/delegate/    # Déléguer permission
GET    /api/permissions/audit/       # Audit permissions
```

### **Décorateurs disponibles**
```python
from apps.permissions.decorators import permission_required, audit_required

@permission_required('users.view_user')
def view_user(request):
    pass

@audit_required('users.create_user')
def create_user(request):
    pass
```

### **Exemple d'utilisation**
```python
# Créer un rôle
POST /api/roles/
{
  "name": "admin",
  "description": "Administrateur système",
  "permissions": ["users.view_user", "users.create_user"]
}

# Déléguer une permission
POST /api/permissions/delegate/
{
  "user_id": 123,
  "permission": "users.view_user",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

---

## ⚙️ Admin API App

### **Description**
APIs d'administration pour la gestion du système.

### **Fonctionnalités principales**
- ✅ **Gestion des utilisateurs** (création, modification, suppression)
- ✅ **Gestion des rôles** et permissions
- ✅ **Configuration système**
- ✅ **Statistiques d'administration**
- ✅ **Actions en lot**
- ✅ **Export/Import de données**

### **Modèles**
```python
# apps/admin_api/models/
├── AdminAction        # Actions d'administration
├── SystemConfig       # Configuration système
├── AdminStats         # Statistiques admin
└── BulkOperation      # Opérations en lot
```

### **APIs disponibles**
```
GET    /api/admin/users/             # Gestion utilisateurs
POST   /api/admin/users/             # Créer utilisateur
PUT    /api/admin/users/{id}/        # Modifier utilisateur
DELETE /api/admin/users/{id}/        # Supprimer utilisateur
GET    /api/admin/stats/             # Statistiques
POST   /api/admin/bulk-operations/   # Opérations en lot
GET    /api/admin/system-config/     # Configuration système
```

### **Exemple d'utilisation**
```python
# Créer un utilisateur (admin)
POST /api/admin/users/
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "roles": ["user"]
}

# Statistiques d'administration
GET /api/admin/stats/
{
  "total_users": 1250,
  "active_users": 1100,
  "new_users_today": 15,
  "failed_logins": 3
}
```

---

## 🌐 API App

### **Description**
Gestion des APIs et de leur documentation.

### **Fonctionnalités principales**
- ✅ **Documentation API** automatique
- ✅ **Versioning des APIs**
- ✅ **Rate limiting** par API
- ✅ **Monitoring des APIs**
- ✅ **Gestion des clés API**
- ✅ **Analytics des APIs**

### **Modèles**
```python
# apps/api/models/
├── APIKey            # Clés API
├── APIVersion        # Versions d'API
├── APIUsage          # Utilisation des APIs
├── APIDocumentation  # Documentation
└── APIAnalytics      # Analytics
```

### **APIs disponibles**
```
GET    /api/api/keys/                # Clés API
POST   /api/api/keys/                # Créer clé API
GET    /api/api/versions/            # Versions API
GET    /api/api/usage/               # Utilisation
GET    /api/api/analytics/           # Analytics
GET    /api/api/documentation/       # Documentation
```

### **Exemple d'utilisation**
```python
# Créer une clé API
POST /api/api/keys/
{
  "name": "Mobile App Key",
  "description": "Clé pour l'application mobile",
  "permissions": ["read", "write"],
  "expires_at": "2024-12-31T23:59:59Z"
}

# Utilisation avec clé API
GET /api/users/profile/
Authorization: ApiKey <api_key>
```

---

## 📊 Monitoring App

### **Description**
Système de monitoring et d'observabilité complet.

### **Fonctionnalités principales**
- ✅ **Logs structurés** avec niveaux
- ✅ **Métriques personnalisées** (counters, gauges, histograms)
- ✅ **Monitoring des performances**
- ✅ **Alertes configurables**
- ✅ **Dashboards de monitoring**
- ✅ **Export des données**

### **Modèles**
```python
# apps/monitoring/models/
├── LogEntry           # Entrées de log
├── Metric            # Métriques
├── Alert             # Alertes
├── AlertRule         # Règles d'alerte
├── Dashboard         # Tableaux de bord
└── MonitoringConfig  # Configuration
```

### **APIs disponibles**
```
GET    /api/monitoring/logs/         # Logs
POST   /api/monitoring/logs/         # Créer log
GET    /api/monitoring/metrics/      # Métriques
POST   /api/monitoring/metrics/      # Créer métrique
GET    /api/monitoring/alerts/       # Alertes
POST   /api/monitoring/alerts/       # Créer alerte
GET    /api/monitoring/dashboards/   # Tableaux de bord
```

### **Services disponibles**
```python
from apps.monitoring.services import LoggingService, MetricsService

# Logging
logging_service = LoggingService()
logging_service.log('INFO', 'User logged in', user=user)

# Métriques
metrics_service = MetricsService()
metrics_service.increment_counter('user_logins')
metrics_service.set_gauge('active_users', 150)
```

### **Exemple d'utilisation**
```python
# Créer une alerte
POST /api/monitoring/alerts/
{
  "name": "High Error Rate",
  "description": "Taux d'erreur élevé",
  "condition": "error_rate > 5%",
  "threshold": 5,
  "notification_channels": ["email", "slack"]
}

# Récupérer les métriques
GET /api/monitoring/metrics/
{
  "counters": {
    "user_logins": 1250,
    "api_requests": 15000
  },
  "gauges": {
    "active_users": 150,
    "memory_usage": 75.5
  }
}
```

---

## 📈 Analytics App

### **Description**
Système d'analytics et de reporting avancé.

### **Fonctionnalités principales**
- ✅ **Tableaux de bord** personnalisables
- ✅ **Rapports** automatisés
- ✅ **Métriques** personnalisées
- ✅ **Export** de données (CSV, Excel, PDF)
- ✅ **Planification** de rapports
- ✅ **Partage** de tableaux de bord

### **Modèles**
```python
# apps/analytics/models/
├── AnalyticsDashboard  # Tableaux de bord
├── DashboardWidget     # Widgets
├── ReportTemplate      # Templates de rapport
├── Report             # Rapports
├── CustomMetric       # Métriques personnalisées
└── DataExport         # Exports de données
```

### **APIs disponibles**
```
GET    /api/analytics/dashboards/    # Tableaux de bord
POST   /api/analytics/dashboards/    # Créer tableau de bord
GET    /api/analytics/reports/       # Rapports
POST   /api/analytics/reports/       # Créer rapport
GET    /api/analytics/metrics/       # Métriques
POST   /api/analytics/export/        # Exporter données
```

### **Exemple d'utilisation**
```python
# Créer un tableau de bord
POST /api/analytics/dashboards/
{
  "name": "User Analytics",
  "description": "Analytics des utilisateurs",
  "dashboard_type": "user_analytics",
  "is_public": false,
  "widgets": [
    {
      "name": "Active Users",
      "widget_type": "counter",
      "data_source": "users",
      "query": "SELECT COUNT(*) FROM users WHERE last_login > NOW() - INTERVAL 1 DAY"
    }
  ]
}

# Générer un rapport
POST /api/analytics/reports/
{
  "template": "user_report",
  "format": "pdf",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}
```

---

## 🌍 Internationalization App

### **Description**
Système d'internationalisation complet avec traduction automatique.

### **Fonctionnalités principales**
- ✅ **Gestion des langues** supportées
- ✅ **Traduction automatique** (Google, Microsoft, DeepL, OpenAI)
- ✅ **Cache des traductions**
- ✅ **Détection automatique** de langue
- ✅ **Préférences utilisateur**
- ✅ **Clés de traduction** pour l'interface

### **Modèles**
```python
# apps/internationalization/models/
├── Language              # Langues supportées
├── Content              # Contenu à traduire
├── ContentTranslation   # Traductions
├── TranslationKey       # Clés de traduction
├── LanguagePreference   # Préférences utilisateur
├── TranslationProvider  # Fournisseurs de traduction
├── TranslationJob       # Jobs de traduction
└── TranslationCache     # Cache des traductions
```

### **APIs disponibles**
```
GET    /api/internationalization/languages/           # Langues
POST   /api/internationalization/languages/           # Ajouter langue
GET    /api/internationalization/content/             # Contenu
POST   /api/internationalization/content/             # Créer contenu
POST   /api/internationalization/auto-translate/      # Traduction auto
POST   /api/internationalization/detect-language/     # Détection langue
GET    /api/internationalization/translation-keys/    # Clés de traduction
```

### **Services disponibles**
```python
from apps.internationalization.services import AutoTranslationService

# Traduction automatique
translation_service = AutoTranslationService()
result = translation_service.translate(
    text="Hello world",
    target_language="fr",
    provider="google"
)
# Résultat: "Bonjour le monde"
```

### **Configuration requise**
```env
# Fournisseurs de traduction
GOOGLE_TRANSLATE_API_KEY=your_key
MICROSOFT_TRANSLATE_API_KEY=your_key
DEEPL_API_KEY=your_key
OPENAI_API_KEY=your_key

# Configuration
DEFAULT_LANGUAGE=fr
SUPPORTED_LANGUAGES=fr,en,es,de,it
```

### **Exemple d'utilisation**
```python
# Traduction automatique
POST /api/internationalization/auto-translate/
{
  "text": "Welcome to our platform!",
  "target_language": "fr",
  "provider": "google"
}

# Réponse
{
  "original_text": "Welcome to our platform!",
  "translated_text": "Bienvenue sur notre plateforme !",
  "source_language": "en",
  "target_language": "fr",
  "provider": "google"
}

# Détection de langue
POST /api/internationalization/detect-language/
{
  "text": "Bonjour, comment allez-vous ?"
}

# Réponse
{
  "text": "Bonjour, comment allez-vous ?",
  "detected_language": "fr",
  "confidence": 0.95
}
```

---

## 🔧 Configuration des Apps

### **Activation/Désactivation**
```env
# Configuration globale
APPS_CONFIG_MODE=default  # minimal, default, production, development

# Ou activation individuelle
ENABLE_AUTHENTICATION=true
ENABLE_USERS=true
ENABLE_NOTIFICATIONS=true
ENABLE_SECURITY=true
ENABLE_PERMISSIONS=true
ENABLE_ADMIN_API=true
ENABLE_API=true
ENABLE_MONITORING=true
ENABLE_ANALYTICS=true
ENABLE_INTERNATIONALIZATION=true
```

### **Dépendances entre apps**
```python
# apps/core/apps_config.py
DEPENDENCIES = {
    'apps.permissions': ['apps.authentication', 'apps.users'],
    'apps.admin_api': ['apps.permissions'],
    'apps.monitoring': ['apps.authentication'],
    'apps.analytics': ['apps.authentication', 'apps.monitoring'],
    'apps.internationalization': ['apps.authentication', 'apps.users']
}
```

### **Script de gestion**
```bash
# Afficher le statut des apps
python manage_apps.py status

# Activer une configuration
python manage_apps.py set-config default

# Activer/désactiver une app
python manage_apps.py enable authentication
python manage_apps.py disable analytics
```

---

## 📚 Ressources supplémentaires

### **Documentation technique**
- [Configuration des Apps](APPS_CONFIGURATION.md)
- [Guide d'installation](INSTALLATION.md)
- [API Documentation](http://localhost:8000/api/docs/)

### **Exemples d'utilisation**
- [Exemples d'APIs](examples/)
- [Tests d'intégration](tests/)
- [Scripts de déploiement](deploy/)

### **Support**
- 📧 Email: support@example.com
- 📖 Documentation: [docs.example.com](https://docs.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/example/django-2fa-auth-api/issues)

---

*Cette documentation est maintenue à jour avec chaque version du starter. Dernière mise à jour: Septembre 2024*
