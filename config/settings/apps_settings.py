"""
Configuration des apps basée sur les variables d'environnement
"""
import os
from .apps_config import (
    get_enabled_apps, DEFAULT_CONFIG, MINIMAL_CONFIG, 
    PRODUCTION_CONFIG, DEVELOPMENT_CONFIG, validate_config
)

# Configuration des apps basée sur l'environnement
APPS_CONFIG_MODE = os.environ.get('APPS_CONFIG_MODE', 'default').lower()

# Modes de configuration disponibles
CONFIG_MODES = {
    'minimal': MINIMAL_CONFIG,
    'default': DEFAULT_CONFIG,
    'development': DEVELOPMENT_CONFIG,
    'production': PRODUCTION_CONFIG,
}

# Configuration personnalisée via variables d'environnement
CUSTOM_CONFIG = {}
for app_name in ['notifications', 'security', 'permissions', 'admin_api', 'api', 'monitoring', 'analytics']:
    env_var = f'ENABLE_{app_name.upper()}'
    if env_var in os.environ:
        CUSTOM_CONFIG[app_name] = os.environ[env_var].lower() in ('true', '1', 'yes', 'on')

# Utiliser la configuration personnalisée si définie, sinon utiliser le mode
if CUSTOM_CONFIG:
    APPS_CONFIG = CUSTOM_CONFIG
else:
    APPS_CONFIG = CONFIG_MODES.get(APPS_CONFIG_MODE, DEFAULT_CONFIG)

# Valider la configuration
is_valid, errors = validate_config(APPS_CONFIG)
if not is_valid:
    print("❌ Configuration des apps invalide:")
    for error in errors:
        print(f"  - {error}")
    print("Utilisation de la configuration minimale par défaut.")
    APPS_CONFIG = MINIMAL_CONFIG

# Obtenir les apps, URLs et middleware activés
ENABLED_APPS, ENABLED_URLS, ENABLED_MIDDLEWARE = get_enabled_apps(APPS_CONFIG)

# Afficher la configuration active
print(f"🔧 Configuration des apps: {APPS_CONFIG_MODE}")
print("📦 Apps activées:")
for app in ENABLED_APPS:
    if app.startswith('apps.'):
        print(f"  ✅ {app}")
print("🚫 Apps désactivées:")
for app_name, enabled in APPS_CONFIG.items():
    if not enabled:
        print(f"  ❌ {app_name}")

# Variables d'environnement pour contrôler les apps individuellement
APPS_CONFIG_VARS = {
    'ENABLE_NOTIFICATIONS': 'notifications',
    'ENABLE_SECURITY': 'security', 
    'ENABLE_PERMISSIONS': 'permissions',
    'ENABLE_ADMIN_API': 'admin_api',
    'ENABLE_API': 'api',
    'ENABLE_MONITORING': 'monitoring',
    'ENABLE_ANALYTICS': 'analytics',
    'ENABLE_INTERNATIONALIZATION': 'internationalization',
}

# Instructions d'utilisation
USAGE_INSTRUCTIONS = """
🔧 Configuration des Apps - Instructions d'utilisation:

1. Configuration par mode:
   export APPS_CONFIG_MODE=minimal     # Apps essentielles seulement
   export APPS_CONFIG_MODE=default     # Toutes les apps (défaut)
   export APPS_CONFIG_MODE=development # Configuration de développement
   export APPS_CONFIG_MODE=production  # Configuration de production

2. Configuration individuelle:
   export ENABLE_NOTIFICATIONS=false   # Désactiver les notifications
   export ENABLE_SECURITY=false        # Désactiver la sécurité
   export ENABLE_PERMISSIONS=false     # Désactiver les permissions
   export ENABLE_ADMIN_API=false       # Désactiver l'admin API
   export ENABLE_API=false             # Désactiver l'API
   export ENABLE_MONITORING=false      # Désactiver le monitoring
   export ENABLE_ANALYTICS=false       # Désactiver l'analytics

3. Exemples:
   # Starter minimal (authentification + utilisateurs seulement)
   export APPS_CONFIG_MODE=minimal
   
   # Starter sans monitoring (pour développement rapide)
   export ENABLE_MONITORING=false
   export ENABLE_ANALYTICS=false
   
   # Starter sans notifications (pour tests)
   export ENABLE_NOTIFICATIONS=false
"""
