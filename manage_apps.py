#!/usr/bin/env python
"""
Script de gestion des apps pour le starter Django 2FA Auth API
Permet d'activer/désactiver facilement les apps
"""

import os
import sys
import argparse
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings.apps_config import (
    OPTIONAL_APPS, DEFAULT_CONFIG, MINIMAL_CONFIG, 
    PRODUCTION_CONFIG, DEVELOPMENT_CONFIG, validate_config
)


def show_status():
    """Affiche le statut actuel des apps"""
    print("📦 Statut des Apps du Starter Django 2FA Auth API")
    print("=" * 60)
    
    # Apps de base (toujours activées)
    print("\n🔧 Apps de Base (toujours activées):")
    print("  ✅ core")
    print("  ✅ apps.authentication")
    print("  ✅ apps.users")
    
    # Apps optionnelles
    print("\n📦 Apps Optionnelles:")
    for app_name, app_config in OPTIONAL_APPS.items():
        status = "✅ Activée" if app_config['enabled'] else "❌ Désactivée"
        print(f"  {status} {app_name}")
        print(f"      📝 {app_config['description']}")
        if app_config['dependencies']:
            deps = [dep.split('.')[-1] for dep in app_config['dependencies']]
            print(f"      🔗 Dépendances: {', '.join(deps)}")
        print()


def show_configs():
    """Affiche les configurations disponibles"""
    print("⚙️  Configurations Disponibles:")
    print("=" * 40)
    
    configs = {
        'minimal': MINIMAL_CONFIG,
        'default': DEFAULT_CONFIG,
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
    }
    
    for name, config in configs.items():
        print(f"\n📋 {name.upper()}:")
        for app_name, enabled in config.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {app_name}")


def set_config(config_name):
    """Définit la configuration des apps"""
    configs = {
        'minimal': MINIMAL_CONFIG,
        'default': DEFAULT_CONFIG,
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
    }
    
    if config_name not in configs:
        print(f"❌ Configuration '{config_name}' non trouvée.")
        print("Configurations disponibles:", ', '.join(configs.keys()))
        return False
    
    config = configs[config_name]
    
    # Valider la configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        print("❌ Configuration invalide:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Mettre à jour les variables d'environnement
    os.environ['APPS_CONFIG_MODE'] = config_name
    
    print(f"✅ Configuration '{config_name}' appliquée.")
    print("📦 Apps activées:")
    for app_name, enabled in config.items():
        if enabled:
            print(f"  ✅ {app_name}")
    
    return True


def toggle_app(app_name, enable=None):
    """Active/désactive une app spécifique"""
    if app_name not in OPTIONAL_APPS:
        print(f"❌ App '{app_name}' non trouvée.")
        print("Apps disponibles:", ', '.join(OPTIONAL_APPS.keys()))
        return False
    
    # Déterminer l'état
    if enable is None:
        current_state = OPTIONAL_APPS[app_name]['enabled']
        enable = not current_state
    
    # Mettre à jour la variable d'environnement
    env_var = f'ENABLE_{app_name.upper()}'
    os.environ[env_var] = 'true' if enable else 'false'
    
    status = "activée" if enable else "désactivée"
    print(f"✅ App '{app_name}' {status}.")
    
    # Vérifier les dépendances
    app_config = OPTIONAL_APPS[app_name]
    if enable and app_config['dependencies']:
        print("🔗 Dépendances requises:")
        for dep in app_config['dependencies']:
            dep_name = dep.split('.')[-1]
            print(f"  - {dep_name}")
    
    return True


def show_usage():
    """Affiche les instructions d'utilisation"""
    print("""
🔧 Gestion des Apps - Starter Django 2FA Auth API

COMMANDES DISPONIBLES:

1. Voir le statut:
   python manage_apps.py status

2. Voir les configurations:
   python manage_apps.py configs

3. Appliquer une configuration:
   python manage_apps.py set-config <nom>
   Exemples:
   - python manage_apps.py set-config minimal
   - python manage_apps.py set-config default
   - python manage_apps.py set-config development
   - python manage_apps.py set-config production

4. Activer/désactiver une app:
   python manage_apps.py toggle <nom_app>
   python manage_apps.py enable <nom_app>
   python manage_apps.py disable <nom_app>

5. Afficher l'aide:
   python manage_apps.py help

EXEMPLES D'UTILISATION:

# Starter minimal (authentification + utilisateurs seulement)
python manage_apps.py set-config minimal

# Starter sans monitoring (pour développement rapide)
python manage_apps.py disable monitoring
python manage_apps.py disable analytics

# Starter sans notifications (pour tests)
python manage_apps.py disable notifications

# Réactiver toutes les apps
python manage_apps.py set-config default

VARIABLES D'ENVIRONNEMENT:

Vous pouvez aussi utiliser les variables d'environnement directement:

export APPS_CONFIG_MODE=minimal
export ENABLE_NOTIFICATIONS=false
export ENABLE_MONITORING=false

Puis redémarrer le serveur Django.
""")


def main():
    parser = argparse.ArgumentParser(description='Gestion des apps du starter Django 2FA Auth API')
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande status
    subparsers.add_parser('status', help='Afficher le statut des apps')
    
    # Commande configs
    subparsers.add_parser('configs', help='Afficher les configurations disponibles')
    
    # Commande set-config
    set_config_parser = subparsers.add_parser('set-config', help='Appliquer une configuration')
    set_config_parser.add_argument('config_name', help='Nom de la configuration')
    
    # Commande toggle
    toggle_parser = subparsers.add_parser('toggle', help='Activer/désactiver une app')
    toggle_parser.add_argument('app_name', help='Nom de l\'app')
    
    # Commande enable
    enable_parser = subparsers.add_parser('enable', help='Activer une app')
    enable_parser.add_argument('app_name', help='Nom de l\'app')
    
    # Commande disable
    disable_parser = subparsers.add_parser('disable', help='Désactiver une app')
    disable_parser.add_argument('app_name', help='Nom de l\'app')
    
    # Commande help
    subparsers.add_parser('help', help='Afficher l\'aide détaillée')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'status':
        show_status()
    elif args.command == 'configs':
        show_configs()
    elif args.command == 'set-config':
        set_config(args.config_name)
    elif args.command == 'toggle':
        toggle_app(args.app_name)
    elif args.command == 'enable':
        toggle_app(args.app_name, enable=True)
    elif args.command == 'disable':
        toggle_app(args.app_name, enable=False)
    elif args.command == 'help':
        show_usage()


if __name__ == '__main__':
    main()

