# 🔔 Notifications App

## Vue d'ensemble

L'app **Notifications** fournit un système de notifications multicanaux complet avec support email, SMS, push, webhook et planification des notifications.

## 🚀 Fonctionnalités

### ✅ Notifications multicanaux
- **Email** avec templates personnalisables
- **SMS** via Twilio et autres fournisseurs
- **Push** via Firebase et autres services
- **Webhook** pour intégrations externes

### ✅ Templates personnalisables
- Templates HTML/text pour emails
- Templates SMS avec variables
- Templates push avec actions
- Variables dynamiques et contexte

### ✅ Planification des notifications
- Envoi immédiat ou différé
- Planification récurrente
- Gestion des fuseaux horaires
- Annulation et modification

### ✅ Gestion avancée
- Historique des notifications
- Statistiques et analytics
- Gestion des bounces et erreurs
- Préférences utilisateur

## 📁 Structure

```
apps/notifications/
├── models/
│   ├── notification_template.py    # Templates de notifications
│   ├── email_notification.py      # Notifications email
│   ├── sms_notification.py        # Notifications SMS
│   ├── push_notification.py       # Notifications push
│   ├── webhook_notification.py    # Notifications webhook
│   ├── notification_schedule.py   # Planification
│   └── notification_history.py    # Historique
├── serializers/
│   ├── template_serializers.py    # Sérialiseurs templates
│   ├── notification_serializers.py # Sérialiseurs notifications
│   └── schedule_serializers.py    # Sérialiseurs planification
├── views/
│   ├── template_views.py          # Vues templates
│   ├── notification_views.py      # Vues notifications
│   └── schedule_views.py          # Vues planification
├── services/
│   ├── email_service.py           # Service email
│   ├── sms_service.py            # Service SMS
│   ├── push_service.py           # Service push
│   ├── webhook_service.py        # Service webhook
│   └── notification_service.py   # Service principal
├── providers/
│   ├── email_providers.py        # Fournisseurs email
│   ├── sms_providers.py          # Fournisseurs SMS
│   └── push_providers.py         # Fournisseurs push
└── utils/
    ├── template_utils.py         # Utilitaires templates
    └── notification_utils.py     # Utilitaires notifications
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration des notifications
NOTIFICATIONS_ENABLED=true
NOTIFICATION_QUEUE_ENABLED=true
NOTIFICATION_RETRY_COUNT=3
NOTIFICATION_RETRY_DELAY=60  # seconds

# Configuration email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_FROM_NAME=Your App Name
EMAIL_FROM_ADDRESS=noreply@yourapp.com

# Configuration SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Configuration Push (Firebase)
FIREBASE_SERVER_KEY=your_firebase_server_key
FIREBASE_PROJECT_ID=your_firebase_project_id

# Configuration Webhook
WEBHOOK_TIMEOUT=30  # seconds
WEBHOOK_RETRY_COUNT=3
WEBHOOK_RETRY_DELAY=60  # seconds
```

### Dépendances requises

```bash
pip install twilio firebase-admin requests celery
```

## 📡 APIs disponibles

### 📧 Gestion des templates

#### Lister les templates
```http
GET /api/notifications/templates/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "welcome_email",
      "type": "email",
      "subject": "Bienvenue sur {{app_name}}",
      "content": "<h1>Bienvenue {{user_name}}!</h1><p>Merci de vous être inscrit sur {{app_name}}.</p>",
      "variables": ["app_name", "user_name"],
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Créer un template
```http
POST /api/notifications/templates/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "password_reset_email",
  "type": "email",
  "subject": "Réinitialisation de votre mot de passe",
  "content": "<h1>Réinitialisation de mot de passe</h1><p>Bonjour {{user_name}},</p><p>Cliquez sur le lien suivant pour réinitialiser votre mot de passe : <a href=\"{{reset_link}}\">Réinitialiser</a></p>",
  "variables": ["user_name", "reset_link"],
  "is_active": true
}
```

#### Tester un template
```http
POST /api/notifications/templates/{id}/test/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "context": {
    "user_name": "John Doe",
    "app_name": "MyApp",
    "reset_link": "https://app.com/reset?token=abc123"
  },
  "test_email": "test@example.com"
}
```

### 📨 Envoi de notifications

#### Envoyer une notification email
```http
POST /api/notifications/send/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "email",
  "template": "welcome_email",
  "recipient": "user@example.com",
  "context": {
    "user_name": "John Doe",
    "app_name": "MyApp"
  },
  "priority": "normal"
}
```

#### Envoyer une notification SMS
```http
POST /api/notifications/send/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "sms",
  "template": "verification_sms",
  "recipient": "+1234567890",
  "context": {
    "verification_code": "123456"
  }
}
```

#### Envoyer une notification push
```http
POST /api/notifications/send/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "push",
  "template": "new_message_push",
  "recipient": "user_device_token",
  "context": {
    "sender_name": "Jane Doe",
    "message_preview": "Hello, how are you?"
  },
  "data": {
    "message_id": 123,
    "action": "open_message"
  }
}
```

#### Envoyer une notification webhook
```http
POST /api/notifications/send/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "webhook",
  "template": "user_registration_webhook",
  "recipient": "https://external-api.com/webhook",
  "context": {
    "user_id": 123,
    "user_email": "user@example.com",
    "registration_date": "2024-01-01T00:00:00Z"
  },
  "headers": {
    "Authorization": "Bearer webhook_token"
  }
}
```

### 📅 Planification des notifications

#### Planifier une notification
```http
POST /api/notifications/schedule/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "email",
  "template": "reminder_email",
  "recipient": "user@example.com",
  "context": {
    "user_name": "John Doe",
    "reminder_text": "N'oubliez pas votre rendez-vous demain"
  },
  "scheduled_at": "2024-01-02T09:00:00Z",
  "timezone": "Europe/Paris"
}
```

#### Planifier une notification récurrente
```http
POST /api/notifications/schedule/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "email",
  "template": "weekly_report",
  "recipient": "admin@example.com",
  "context": {
    "report_period": "weekly"
  },
  "recurrence": {
    "frequency": "weekly",
    "day_of_week": 1,  # Lundi
    "time": "09:00",
    "timezone": "Europe/Paris"
  }
}
```

#### Lister les notifications planifiées
```http
GET /api/notifications/schedule/
Authorization: Bearer <access_token>
```

#### Annuler une notification planifiée
```http
DELETE /api/notifications/schedule/{id}/
Authorization: Bearer <access_token>
```

### 📊 Historique et statistiques

#### Lister l'historique des notifications
```http
GET /api/notifications/history/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "type": "email",
      "template": "welcome_email",
      "recipient": "user@example.com",
      "status": "sent",
      "sent_at": "2024-01-01T10:00:00Z",
      "delivered_at": "2024-01-01T10:00:05Z",
      "opened_at": "2024-01-01T10:15:00Z",
      "clicked_at": "2024-01-01T10:16:00Z"
    }
  ]
}
```

#### Statistiques des notifications
```http
GET /api/notifications/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "total_sent": 10000,
  "total_delivered": 9800,
  "total_opened": 7500,
  "total_clicked": 2500,
  "delivery_rate": 98.0,
  "open_rate": 76.5,
  "click_rate": 25.5,
  "notifications_by_type": {
    "email": 8000,
    "sms": 1500,
    "push": 500
  },
  "notifications_by_status": {
    "sent": 10000,
    "delivered": 9800,
    "failed": 200,
    "bounced": 50
  }
}
```

## 🛠️ Utilisation dans le code

### Service de notifications

```python
from apps.notifications.services import NotificationService

notification_service = NotificationService()

# Envoyer une notification email
notification_service.send_email(
    template="welcome_email",
    recipient="user@example.com",
    context={
        "user_name": "John Doe",
        "app_name": "MyApp"
    }
)

# Envoyer une notification SMS
notification_service.send_sms(
    template="verification_sms",
    recipient="+1234567890",
    context={
        "verification_code": "123456"
    }
)

# Envoyer une notification push
notification_service.send_push(
    template="new_message_push",
    recipient="user_device_token",
    context={
        "sender_name": "Jane Doe",
        "message_preview": "Hello!"
    }
)
```

### Service de templates

```python
from apps.notifications.services import TemplateService

template_service = TemplateService()

# Créer un template
template = template_service.create_template(
    name="welcome_email",
    type="email",
    subject="Bienvenue sur {{app_name}}",
    content="<h1>Bienvenue {{user_name}}!</h1>",
    variables=["app_name", "user_name"]
)

# Rendre un template avec contexte
rendered = template_service.render_template(
    template=template,
    context={
        "app_name": "MyApp",
        "user_name": "John Doe"
    }
)
```

### Service de planification

```python
from apps.notifications.services import ScheduleService

schedule_service = ScheduleService()

# Planifier une notification
scheduled = schedule_service.schedule_notification(
    type="email",
    template="reminder_email",
    recipient="user@example.com",
    context={"user_name": "John Doe"},
    scheduled_at=datetime.now() + timedelta(hours=24)
)

# Planifier une notification récurrente
recurring = schedule_service.schedule_recurring_notification(
    type="email",
    template="weekly_report",
    recipient="admin@example.com",
    context={"report_period": "weekly"},
    frequency="weekly",
    day_of_week=1,
    time="09:00"
)
```

### Décorateurs de notifications

```python
from apps.notifications.decorators import send_notification

@send_notification('welcome_email')
def create_user(request):
    """Création d'utilisateur avec notification automatique"""
    user = User.objects.create(**request.data)
    
    # La notification est envoyée automatiquement
    # avec le contexte de l'utilisateur créé
    
    return Response(UserSerializer(user).data)
```

### Signaux de notifications

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.notifications.services import NotificationService

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    if created:
        notification_service = NotificationService()
        notification_service.send_email(
            template="welcome_email",
            recipient=instance.email,
            context={
                "user_name": instance.get_full_name(),
                "app_name": "MyApp"
            }
        )
```

## 🔧 Configuration des fournisseurs

### Configuration email

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'noreply@yourapp.com'
```

### Configuration SMS (Twilio)

```python
# Configuration Twilio
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_phone_number'

# Utilisation
from apps.notifications.providers import TwilioSMSProvider

sms_provider = TwilioSMSProvider()
sms_provider.send_sms(
    to="+1234567890",
    body="Votre code de vérification est : 123456"
)
```

### Configuration Push (Firebase)

```python
# Configuration Firebase
FIREBASE_SERVER_KEY = 'your_server_key'
FIREBASE_PROJECT_ID = 'your_project_id'

# Utilisation
from apps.notifications.providers import FirebasePushProvider

push_provider = FirebasePushProvider()
push_provider.send_push(
    device_token="user_device_token",
    title="Nouveau message",
    body="Vous avez reçu un nouveau message",
    data={"message_id": 123}
)
```

### Configuration Webhook

```python
# Configuration webhook
WEBHOOK_TIMEOUT = 30
WEBHOOK_RETRY_COUNT = 3
WEBHOOK_RETRY_DELAY = 60

# Utilisation
from apps.notifications.providers import WebhookProvider

webhook_provider = WebhookProvider()
webhook_provider.send_webhook(
    url="https://external-api.com/webhook",
    data={"event": "user_registered", "user_id": 123},
    headers={"Authorization": "Bearer token"}
)
```

## 📊 Templates disponibles

### Template email de bienvenue

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bienvenue sur {{app_name}}</title>
</head>
<body>
    <h1>Bienvenue {{user_name}}!</h1>
    <p>Merci de vous être inscrit sur {{app_name}}.</p>
    <p>Votre compte a été créé avec succès.</p>
    <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
    <p>Cordialement,<br>L'équipe {{app_name}}</p>
</body>
</html>
```

### Template SMS de vérification

```
Votre code de vérification {{app_name}} est : {{verification_code}}
Ce code expire dans {{expiry_minutes}} minutes.
```

### Template push de nouveau message

```json
{
  "title": "Nouveau message de {{sender_name}}",
  "body": "{{message_preview}}",
  "data": {
    "message_id": "{{message_id}}",
    "action": "open_message"
  }
}
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.notifications

# Tests avec couverture
coverage run --source='apps.notifications' manage.py test apps.notifications
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.notifications.services import NotificationService
from apps.notifications.models import NotificationTemplate

class NotificationServiceTestCase(TestCase):
    def setUp(self):
        self.notification_service = NotificationService()
        self.template = NotificationTemplate.objects.create(
            name="test_email",
            type="email",
            subject="Test Subject",
            content="Test content for {{user_name}}",
            variables=["user_name"]
        )
    
    def test_send_email(self):
        result = self.notification_service.send_email(
            template="test_email",
            recipient="test@example.com",
            context={"user_name": "John Doe"}
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.recipient, "test@example.com")
    
    def test_template_rendering(self):
        rendered = self.notification_service.render_template(
            template=self.template,
            context={"user_name": "John Doe"}
        )
        
        self.assertIn("John Doe", rendered.content)
        self.assertEqual(rendered.subject, "Test Subject")
```

## 📊 Monitoring et analytics

### Métriques disponibles

```python
from apps.notifications.models import NotificationHistory

# Statistiques des notifications
stats = {
    'total_sent': NotificationHistory.objects.count(),
    'delivery_rate': NotificationHistory.objects.filter(status='delivered').count() / NotificationHistory.objects.count() * 100,
    'open_rate': NotificationHistory.objects.filter(opened_at__isnull=False).count() / NotificationHistory.objects.filter(type='email').count() * 100,
    'click_rate': NotificationHistory.objects.filter(clicked_at__isnull=False).count() / NotificationHistory.objects.filter(type='email').count() * 100,
}
```

### Logs de notifications

```python
import logging

# Activer les logs de notifications
logging.getLogger('apps.notifications').setLevel(logging.INFO)

# Les logs incluent:
# - Envoi de notifications
# - Erreurs de livraison
# - Statistiques de performance
# - Bounces et erreurs
```

## 🐛 Dépannage

### Problèmes courants

1. **Email non envoyé** : Vérifiez la configuration SMTP
2. **SMS non envoyé** : Vérifiez les credentials Twilio
3. **Push non envoyé** : Vérifiez la configuration Firebase
4. **Webhook échoué** : Vérifiez l'URL et les headers

### Configuration de debug

```python
# settings.py
DEBUG_NOTIFICATIONS = True
NOTIFICATION_LOG_LEVEL = 'DEBUG'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Pour les tests
```

## 📚 Ressources

- [Django Email](https://docs.djangoproject.com/en/stable/topics/email/)
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Celery](https://docs.celeryproject.org/) - Pour les tâches asynchrones

---

*Dernière mise à jour: Septembre 2024*
