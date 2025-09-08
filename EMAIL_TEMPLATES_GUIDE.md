# 📧 Guide des Templates d'Email

Ce guide explique comment utiliser et personnaliser les templates d'email de votre API Django 2FA Auth.

## 🎯 Templates Disponibles

### 1. **Email de Bienvenue** (`welcome.html`)
- **Déclencheur** : Inscription d'un nouvel utilisateur
- **Contenu** : Message de bienvenue, informations du compte, lien pour activer la 2FA
- **Couleur** : Vert (#28a745)

### 2. **Email de Connexion** (`login_success.html`)
- **Déclencheur** : Connexion réussie
- **Contenu** : Détails de la connexion, adresse IP, navigateur, localisation
- **Couleur** : Vert (#28a745)

### 3. **Email de Réinitialisation** (`password_reset.html`)
- **Déclencheur** : Demande de réinitialisation de mot de passe
- **Contenu** : Code de réinitialisation, instructions, délai d'expiration
- **Couleur** : Jaune (#ffc107)

### 4. **Email de Changement** (`password_changed.html`)
- **Déclencheur** : Changement de mot de passe
- **Contenu** : Confirmation du changement, détails de sécurité
- **Couleur** : Vert (#28a745)

### 5. **Email de Profil** (`profile_updated.html`)
- **Déclencheur** : Mise à jour du profil utilisateur
- **Contenu** : Détails des modifications, résumé des changements
- **Couleur** : Bleu (#17a2b8)

### 6. **Email d'Alerte** (`security_alert.html`)
- **Déclencheur** : Activité suspecte détectée
- **Contenu** : Type d'alerte, actions recommandées, mesures de sécurité
- **Couleur** : Rouge (#dc3545)

### 7. **Email 2FA** (`2fa_enabled.html`)
- **Déclencheur** : Activation de l'authentification à deux facteurs
- **Contenu** : Codes de récupération, instructions d'utilisation
- **Couleur** : Vert (#28a745)

## 🚀 Utilisation

### Envoi Automatique
Les emails sont envoyés automatiquement via les signaux Django :

```python
# Dans apps/authentication/signals.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Envoi automatique de l'email de bienvenue
        email_service.send_welcome_email(instance)
```

### Envoi Manuel
```python
from apps.notifications.services.template_email_service import TemplateEmailService

email_service = TemplateEmailService()

# Email de bienvenue
email_service.send_welcome_email(user)

# Email de connexion
email_service.send_login_success_email(
    user=user,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    login_time=datetime.now()
)

# Email de réinitialisation
email_service.send_password_reset_email(
    user=user,
    reset_code="123456",
    ip_address="192.168.1.100",
    expiry_minutes=30
)
```

## 🎨 Personnalisation

### Variables Disponibles
Chaque template a accès aux variables suivantes :

```python
context = {
    'user': user,                    # Objet utilisateur Django
    'site_name': 'Django 2FA Auth API',
    'site_url': 'http://localhost:8000',
    'current_year': 2025,
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
    'login_time': datetime.now(),
    # Variables spécifiques selon le template
}
```

### Modification des Templates
1. **Éditez le fichier HTML** dans `apps/notifications/templates/emails/`
2. **Modifiez les styles CSS** dans la section `<style>`
3. **Ajoutez de nouvelles variables** dans le contexte
4. **Testez** avec le script `test_email_direct.py`

### Exemple de Personnalisation
```html
<!-- Dans welcome.html -->
<h1 class="welcome-title">🎉 Bienvenue {{ user.first_name }} !</h1>

<div class="highlight">
    <strong>📧 Email :</strong> {{ user.email }}<br>
    <strong>👤 Nom d'utilisateur :</strong> {{ user.username }}<br>
    <strong>📅 Date d'inscription :</strong> {{ user.date_joined|date:"d/m/Y à H:i" }}
</div>
```

## 🔧 Configuration

### Mode Console (Développement)
```python
# Dans config/settings/development.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Mode SendGrid (Production)
```python
# Dans config/settings/development.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
```

### Variables d'Environnement
```env
# Dans votre fichier .env
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
SITE_NAME=Django 2FA Auth API
SITE_URL=http://localhost:8000
```

## 🧪 Tests

### Test Automatique
```bash
python test_email_direct.py
```

### Test Manuel
```python
from apps.notifications.services.template_email_service import TemplateEmailService
from apps.authentication.models import User

# Récupérer un utilisateur
user = User.objects.first()

# Tester l'envoi
email_service = TemplateEmailService()
success = email_service.send_welcome_email(user)
print(f"Email envoyé: {success}")
```

## 📊 Monitoring

### Logs
Les envois d'emails sont loggés :
```python
logger.info(f"Email envoyé avec succès à {to_email}")
logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
```

### Base de Données
Chaque email est enregistré dans la table `notifications_notification` :
- Statut : `pending`, `sent`, `failed`
- Contenu HTML et texte
- Métadonnées (IP, user agent, etc.)

## 🚨 Dépannage

### Erreur "Template not found"
- Vérifiez que le fichier existe dans `apps/notifications/templates/emails/`
- Vérifiez la configuration `TEMPLATES` dans `settings.py`

### Erreur "Unauthenticated senders not allowed"
- Configurez votre clé API SendGrid
- Vérifiez que l'email FROM_EMAIL est vérifié

### Erreur "User is required"
- Assurez-vous de passer l'utilisateur dans le contexte
- Vérifiez que l'utilisateur existe dans la base de données

## 📈 Améliorations Futures

### Fonctionnalités à Ajouter
- [ ] Géolocalisation automatique des IP
- [ ] Templates multilingues
- [ ] A/B testing des templates
- [ ] Analytics des emails ouverts
- [ ] Templates personnalisables par utilisateur
- [ ] Intégration avec d'autres services (Mailgun, Amazon SES)

### Optimisations
- [ ] Cache des templates rendus
- [ ] Envoi asynchrone avec Celery
- [ ] Compression des images
- [ ] Optimisation mobile

---

**🎉 Vos templates d'email sont maintenant prêts à être utilisés en production !**



