# 🔧 Configuration Modulaire des Apps

Le starter Django 2FA Auth API utilise maintenant une **configuration modulaire** qui permet d'activer/désactiver facilement les apps selon vos besoins.

## 📦 Apps Disponibles

### 🔧 Apps de Base (toujours activées)
- `core` - Utilitaires de base
- `apps.authentication` - Authentification JWT + 2FA
- `apps.users` - Gestion des utilisateurs

### 📦 Apps Optionnelles
- `apps.notifications` - Système de notifications (Email, SMS, Push)
- `apps.security` - Sécurité avancée (rate limiting, IP blocking, etc.)
- `apps.permissions` - Système de permissions granulaires (RBAC, ABAC, délégations)
- `apps.admin_api` - API d'administration avancée
- `apps.api` - Gestion des endpoints API et métadonnées
- `apps.monitoring` - Monitoring, métriques, alertes et dashboards
- `apps.analytics` - Analytics, rapports et tableaux de bord avancés

## ⚙️ Modes de Configuration

### 1. Configuration par Mode

```bash
# Starter minimal (authentification + utilisateurs seulement)
export APPS_CONFIG_MODE=minimal

# Starter complet (toutes les apps - défaut)
export APPS_CONFIG_MODE=default

# Configuration de développement
export APPS_CONFIG_MODE=development

# Configuration de production
export APPS_CONFIG_MODE=production
```

### 2. Configuration Individuelle

```bash
# Désactiver des apps spécifiques
export ENABLE_NOTIFICATIONS=false
export ENABLE_SECURITY=false
export ENABLE_PERMISSIONS=false
export ENABLE_ADMIN_API=false
export ENABLE_API=false
export ENABLE_MONITORING=false
export ENABLE_ANALYTICS=false
```

## 🛠️ Utilisation du Script de Gestion

### Installation
```bash
# Rendre le script exécutable
chmod +x manage_apps.py
```

### Commandes Disponibles

#### 1. Voir le statut des apps
```bash
python manage_apps.py status
```

#### 2. Voir les configurations disponibles
```bash
python manage_apps.py configs
```

#### 3. Appliquer une configuration
```bash
# Starter minimal
python manage_apps.py set-config minimal

# Starter complet
python manage_apps.py set-config default

# Configuration de développement
python manage_apps.py set-config development

# Configuration de production
python manage_apps.py set-config production
```

#### 4. Activer/désactiver des apps
```bash
# Activer une app
python manage_apps.py enable monitoring

# Désactiver une app
python manage_apps.py disable analytics

# Toggle (activer/désactiver selon l'état actuel)
python manage_apps.py toggle notifications
```

#### 5. Aide détaillée
```bash
python manage_apps.py help
```

## 📋 Exemples d'Utilisation

### Starter Minimal
```bash
# Pour un starter ultra-léger (authentification + utilisateurs seulement)
python manage_apps.py set-config minimal
python manage.py runserver
```

### Starter sans Monitoring
```bash
# Pour le développement rapide (sans monitoring/analytics)
python manage_apps.py disable monitoring
python manage_apps.py disable analytics
python manage.py runserver
```

### Starter sans Notifications
```bash
# Pour les tests (sans notifications)
python manage_apps.py disable notifications
python manage.py runserver
```

### Starter de Production
```bash
# Pour la production (toutes les apps activées)
python manage_apps.py set-config production
python manage.py runserver
```

## 🔗 Dépendances entre Apps

Certaines apps ont des dépendances :

- `apps.permissions` → `apps.authentication`, `apps.users`
- `apps.admin_api` → `apps.authentication`, `apps.users`, `apps.permissions`
- `apps.analytics` → `apps.authentication`, `apps.users`, `apps.monitoring`

Le système vérifie automatiquement les dépendances et désactive les apps si leurs dépendances ne sont pas satisfaites.

## 📁 Structure des Fichiers

```
config/settings/
├── apps_config.py      # Configuration des apps et dépendances
├── apps_settings.py    # Configuration basée sur l'environnement
└── base.py            # Configuration Django principale

manage_apps.py         # Script de gestion des apps
env.example           # Exemple de configuration d'environnement
APPS_CONFIGURATION.md # Cette documentation
```

## 🚀 Avantages

### ✅ Flexibilité
- Choisissez exactement les fonctionnalités dont vous avez besoin
- Réduisez la complexité pour des projets simples
- Ajoutez progressivement des fonctionnalités

### ✅ Performance
- Moins d'apps = moins de middleware = meilleures performances
- Réduction de la surface d'attaque
- Démarrage plus rapide

### ✅ Maintenance
- Configuration centralisée
- Validation automatique des dépendances
- Documentation intégrée

### ✅ Développement
- Tests plus rapides avec moins d'apps
- Débogage simplifié
- Configuration par environnement

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Mode de configuration
APPS_CONFIG_MODE=minimal

# Configuration individuelle (override le mode)
ENABLE_NOTIFICATIONS=false
ENABLE_MONITORING=false
ENABLE_ANALYTICS=false
```

### Fichier .env
```env
# Configuration des apps
APPS_CONFIG_MODE=default
ENABLE_NOTIFICATIONS=true
ENABLE_SECURITY=true
ENABLE_PERMISSIONS=true
ENABLE_ADMIN_API=true
ENABLE_API=true
ENABLE_MONITORING=true
ENABLE_ANALYTICS=true
```

## 🐛 Dépannage

### App non trouvée
```
❌ App 'monitoring' non trouvée.
Apps disponibles: notifications, security, permissions, admin_api, api, monitoring, analytics
```

### Dépendances non satisfaites
```
⚠️  App 'analytics' désactivée: dépendances non satisfaites
```

### Configuration invalide
```
❌ Configuration des apps invalide:
  - App 'analytics' nécessite 'monitoring'
Utilisation de la configuration minimale par défaut.
```

## 📚 Ressources

- [Documentation Django Apps](https://docs.djangoproject.com/en/stable/ref/applications/)
- [Configuration d'environnement](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Middleware Django](https://docs.djangoproject.com/en/stable/topics/http/middleware/)

---

**🎯 Le starter est maintenant 100% modulaire et configurable selon vos besoins !**

