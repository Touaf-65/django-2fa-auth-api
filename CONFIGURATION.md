# 🔧 Configuration de l'Environnement

Ce guide vous explique comment configurer votre environnement pour le projet Django 2FA Auth API.

## 📁 Fichiers de Configuration

### 1. **env_template.txt** - Configuration Complète
Fichier de référence avec toutes les options disponibles. Utilisez-le comme modèle pour une configuration complète.

### 2. **env_minimal.txt** - Configuration Minimale
Configuration de base pour commencer rapidement avec les fonctionnalités essentielles.

### 3. **setup_env.py** - Script Automatique
Script Python qui génère automatiquement un fichier `.env` avec des valeurs par défaut sécurisées.

## 🚀 Configuration Rapide

### Option 1 : Script Automatique (Recommandé)
```bash
python setup_env.py
```

### Option 2 : Configuration Manuelle
```bash
# Copiez le fichier minimal
cp env_minimal.txt .env

# Ou copiez le fichier complet
cp env_template.txt .env
```

## 🔑 Variables Obligatoires

### Pour le Fonctionnement de Base
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Pour les Emails Réels (SendGrid)
```env
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

### Pour les SMS Réels (Twilio)
```env
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
```

## 📧 Configuration SendGrid

1. **Créez un compte** sur [SendGrid](https://sendgrid.com/)
2. **Générez une clé API** :
   - Allez dans Settings → API Keys
   - Créez une nouvelle clé avec les permissions "Mail Send"
3. **Ajoutez la clé** dans votre fichier `.env` :
   ```env
   SENDGRID_API_KEY=SG.your-actual-api-key-here
   FROM_EMAIL=noreply@yourdomain.com
   ```

## 📱 Configuration Twilio

1. **Créez un compte** sur [Twilio](https://www.twilio.com/)
2. **Récupérez vos identifiants** :
   - Account SID et Auth Token depuis le Dashboard
   - Numéro de téléphone depuis Phone Numbers → Manage → Active numbers
3. **Ajoutez les identifiants** dans votre fichier `.env` :
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your-auth-token-here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## 🔒 Sécurité

### ⚠️ Important
- **Ne jamais commiter** le fichier `.env` dans Git
- **Générez des clés uniques** pour la production
- **Utilisez des mots de passe forts**
- **Changez les valeurs par défaut** avant la mise en production

### 🔐 Clés Secrètes
Le script `setup_env.py` génère automatiquement une clé secrète Django sécurisée. Pour la production, utilisez :
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🌍 Environnements

### Développement
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SECURE_SSL_REDIRECT=True
```

## 🧪 Test de Configuration

Après avoir configuré votre `.env`, testez la configuration :

```bash
# Vérifiez la configuration Django
python manage.py check

# Testez l'envoi d'emails
python test_email_direct.py

# Testez l'API complète
python test_api_complete.py
```

## 📊 Monitoring

### Logs
Les logs sont configurés pour afficher les informations importantes :
- Erreurs d'envoi d'emails
- Tentatives de connexion échouées
- Activités de sécurité

### Sentry (Optionnel)
Pour le monitoring d'erreurs en production :
```env
SENTRY_DSN=your-sentry-dsn-here
```

## 🆘 Dépannage

### Erreur "ModuleNotFoundError: No module named 'decouple'"
```bash
pip install python-decouple
```

### Erreur "Unauthenticated senders not allowed"
- Vérifiez votre clé API SendGrid
- Assurez-vous que l'email FROM_EMAIL est vérifié dans SendGrid

### Erreur "Invalid phone number"
- Vérifiez le format du numéro Twilio (+1234567890)
- Assurez-vous que le numéro est actif dans votre compte Twilio

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs Django
2. Consultez la documentation des services externes
3. Testez avec les scripts fournis
4. Vérifiez la configuration de votre `.env`

---

**🎉 Une fois configuré, votre API Django 2FA Auth sera prête à envoyer des emails et SMS réels !**



