#!/usr/bin/env python
"""
Script pour configurer automatiquement le fichier .env
"""
import os
import secrets
import string

def generate_secret_key():
    """Génère une clé secrète Django sécurisée"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(chars) for _ in range(50))

def create_env_file():
    """Crée un fichier .env avec des valeurs par défaut"""
    
    print("🚀 Configuration du fichier .env")
    print("=" * 50)
    
    # Vérifier si .env existe déjà
    if os.path.exists('.env'):
        response = input("⚠️  Le fichier .env existe déjà. Voulez-vous le remplacer ? (y/N): ")
        if response.lower() != 'y':
            print("❌ Configuration annulée.")
            return
    
    # Générer une clé secrète
    secret_key = generate_secret_key()
    
    # Configuration par défaut
    env_content = f"""# ===========================================
# DJANGO 2FA AUTH API - Configuration
# ===========================================
# Généré automatiquement le {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# ===========================================
# DJANGO CORE
# ===========================================
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ===========================================
# EMAIL (SENDGRID)
# ===========================================
# Remplacez par votre vraie clé API SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key-here
FROM_EMAIL=noreply@yourdomain.com

# ===========================================
# SMS (TWILIO)
# ===========================================
# Remplacez par vos vrais identifiants Twilio
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# ===========================================
# SITE
# ===========================================
SITE_NAME=Django 2FA Auth API
SITE_URL=http://localhost:8000

# ===========================================
# ADMIN
# ===========================================
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=admin123

# ===========================================
# SÉCURITÉ
# ===========================================
RATE_LIMIT_ENABLED=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900

# ===========================================
# CORS
# ===========================================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
    
    # Écrire le fichier
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Fichier .env créé avec succès !")
        print("📝 N'oubliez pas de :")
        print("   1. Configurer votre clé API SendGrid")
        print("   2. Configurer vos identifiants Twilio")
        print("   3. Changer l'email FROM_EMAIL")
        print("   4. Modifier les identifiants admin")
        print("   5. Ne jamais commiter le fichier .env dans Git")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {str(e)}")

def main():
    """Fonction principale"""
    print("🔧 Configuration de l'environnement Django 2FA Auth API")
    print("=" * 60)
    
    create_env_file()
    
    print("\n📋 Prochaines étapes :")
    print("1. Éditez le fichier .env avec vos vraies valeurs")
    print("2. Activez votre environnement virtuel")
    print("3. Installez les dépendances : pip install -r requirements/development.txt")
    print("4. Appliquez les migrations : python manage.py migrate")
    print("5. Créez un superutilisateur : python manage.py createsuperuser")
    print("6. Lancez le serveur : python manage.py runserver")

if __name__ == "__main__":
    main()

