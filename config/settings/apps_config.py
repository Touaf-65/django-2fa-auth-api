"""
Configuration modulaire des apps pour le starter Django 2FA Auth API
Permet d'activer/désactiver facilement les apps selon les besoins
"""

# Apps de base (toujours requises)
CORE_APPS = [
    'core',
    'apps.authentication',
    'apps.users',
]

# Apps optionnelles (peuvent être désactivées)
OPTIONAL_APPS = {
    'notifications': {
        'app': 'apps.notifications',
        'urls': 'apps.notifications.urls',
        'middleware': [],
        'dependencies': ['authentication', 'users'],
        'description': 'Système de notifications (Email, SMS, Push)',
        'enabled': True,
    },
    'security': {
        'app': 'apps.security',
        'urls': 'apps.security.urls',
        'middleware': [
            'apps.security.middleware.IPBlockingMiddleware',
            'apps.security.middleware.RateLimitMiddleware',
            'apps.security.middleware.SecurityMiddleware',
        ],
        'dependencies': ['authentication', 'users'],
        'description': 'Sécurité avancée (rate limiting, IP blocking, etc.)',
        'enabled': True,
    },
    'permissions': {
        'app': 'apps.permissions',
        'urls': 'apps.permissions.urls',
        'middleware': [
            'apps.permissions.middleware.AuditMiddleware',
            'apps.permissions.middleware.DelegationMiddleware',
            'apps.permissions.middleware.PermissionMiddleware',
        ],
        'dependencies': ['authentication', 'users'],
        'description': 'Système de permissions granulaires (RBAC, ABAC, délégations)',
        'enabled': True,
    },
    'admin_api': {
        'app': 'apps.admin_api',
        'urls': 'apps.admin_api.urls',
        'middleware': [],
        'dependencies': ['authentication', 'users', 'permissions'],
        'description': 'API d\'administration avancée',
        'enabled': True,
    },
    'api': {
        'app': 'apps.api',
        'urls': 'apps.api.urls',
        'middleware': [],
        'dependencies': ['authentication', 'users'],
        'description': 'Gestion des endpoints API et métadonnées',
        'enabled': True,
    },
    'monitoring': {
        'app': 'apps.monitoring',
        'urls': 'apps.monitoring.urls',
        'middleware': [
            'apps.monitoring.middleware.monitoring_middleware.MonitoringMiddleware',
            'apps.monitoring.middleware.monitoring_middleware.PerformanceMonitoringMiddleware',
            'apps.monitoring.middleware.monitoring_middleware.DatabaseMonitoringMiddleware',
        ],
        'dependencies': ['authentication', 'users'],
        'description': 'Monitoring, métriques, alertes et dashboards',
        'enabled': True,
    },
    'analytics': {
        'app': 'apps.analytics',
        'urls': 'apps.analytics.urls',
        'middleware': [],
        'dependencies': ['authentication', 'users', 'monitoring'],
        'description': 'Analytics, rapports et tableaux de bord avancés',
        'enabled': True,
    },
    'internationalization': {
        'app': 'apps.internationalization',
        'urls': 'apps.internationalization.urls',
        'middleware': [
            'apps.internationalization.middleware.language_middleware.LanguageMiddleware',
        ],
        'dependencies': ['authentication', 'users'],
        'description': 'Internationalisation avec traductions automatiques multilingues',
        'enabled': True,
    },
}

# Configuration par défaut (toutes les apps activées)
DEFAULT_CONFIG = {
    'notifications': True,
    'security': True,
    'permissions': True,
    'admin_api': True,
    'api': True,
    'monitoring': True,
    'analytics': True,
    'internationalization': True,
}

# Configuration minimale (seulement les apps essentielles)
MINIMAL_CONFIG = {
    'notifications': False,
    'security': False,
    'permissions': False,
    'admin_api': False,
    'api': False,
    'monitoring': False,
    'analytics': False,
    'internationalization': False,
}

# Configuration de production (sans monitoring en développement)
PRODUCTION_CONFIG = {
    'notifications': True,
    'security': True,
    'permissions': True,
    'admin_api': True,
    'api': True,
    'monitoring': True,
    'analytics': True,
    'internationalization': True,
}

# Configuration de développement (avec monitoring)
DEVELOPMENT_CONFIG = {
    'notifications': True,
    'security': True,
    'permissions': True,
    'admin_api': True,
    'api': True,
    'monitoring': True,
    'analytics': True,
    'internationalization': True,
}


def get_enabled_apps(config=None):
    """
    Retourne la liste des apps activées selon la configuration
    
    Args:
        config (dict): Configuration des apps (None = DEFAULT_CONFIG)
    
    Returns:
        tuple: (apps, urls, middleware)
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    # Créer une configuration complète avec les apps de base
    full_config = config.copy()
    full_config['authentication'] = True  # Toujours activé
    full_config['users'] = True  # Toujours activé
    
    enabled_apps = CORE_APPS.copy()
    enabled_urls = []
    enabled_middleware = []
    
    for app_name, app_config in OPTIONAL_APPS.items():
        if full_config.get(app_name, False):
            # Vérifier les dépendances
            dependencies_met = all(
                full_config.get(dep, False) or dep in CORE_APPS
                for dep in app_config['dependencies']
            )
            
            if dependencies_met:
                enabled_apps.append(app_config['app'])
                enabled_urls.append({
                    'path': f'api/{app_name}/',
                    'include': app_config['urls']
                })
                enabled_middleware.extend(app_config['middleware'])
            else:
                print(f"⚠️  App '{app_name}' désactivée: dépendances non satisfaites")
    
    return enabled_apps, enabled_urls, enabled_middleware


def get_app_status():
    """
    Retourne le statut de toutes les apps
    """
    status = {}
    for app_name, app_config in OPTIONAL_APPS.items():
        status[app_name] = {
            'enabled': app_config['enabled'],
            'description': app_config['description'],
            'dependencies': app_config['dependencies']
        }
    return status


def validate_config(config):
    """
    Valide une configuration d'apps
    
    Args:
        config (dict): Configuration à valider
    
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Créer une configuration complète avec les apps de base
    full_config = config.copy()
    full_config['authentication'] = True  # Toujours activé
    full_config['users'] = True  # Toujours activé
    
    for app_name, enabled in config.items():
        if app_name not in OPTIONAL_APPS:
            errors.append(f"App inconnue: {app_name}")
            continue
        
        if enabled:
            app_config = OPTIONAL_APPS[app_name]
            # Vérifier les dépendances
            for dep in app_config['dependencies']:
                if dep not in CORE_APPS and not full_config.get(dep, False):
                    errors.append(f"App '{app_name}' nécessite '{dep}'")
    
    return len(errors) == 0, errors
