# 👥 Users App

## Vue d'ensemble

L'app **Users** fournit une gestion complète des profils utilisateur avec préférences, avatars, historique des connexions et statistiques utilisateur.

## 🚀 Fonctionnalités

### ✅ Profils utilisateur étendus
- Informations personnelles complètes
- Gestion des avatars
- Préférences utilisateur
- Paramètres de compte

### ✅ Historique et statistiques
- Historique des connexions
- Statistiques d'activité
- Métriques d'utilisation
- Rapports d'activité

### ✅ Gestion des préférences
- Préférences de langue
- Préférences de notification
- Préférences d'affichage
- Paramètres de confidentialité

### ✅ Gestion des avatars
- Upload d'images
- Redimensionnement automatique
- Formats supportés (JPEG, PNG, WebP)
- Optimisation des images

## 📁 Structure

```
apps/users/
├── models/
│   ├── user_profile.py        # Profil utilisateur étendu
│   ├── user_preference.py     # Préférences utilisateur
│   ├── user_avatar.py        # Gestion des avatars
│   ├── login_history.py      # Historique des connexions
│   └── user_stats.py         # Statistiques utilisateur
├── serializers/
│   ├── profile_serializers.py # Sérialiseurs profil
│   ├── preference_serializers.py # Sérialiseurs préférences
│   └── stats_serializers.py   # Sérialiseurs statistiques
├── views/
│   ├── profile_views.py       # Vues profil
│   ├── preference_views.py    # Vues préférences
│   ├── avatar_views.py       # Vues avatars
│   └── stats_views.py        # Vues statistiques
├── services/
│   ├── profile_service.py     # Service profil
│   ├── avatar_service.py     # Service avatars
│   └── stats_service.py      # Service statistiques
└── utils/
    ├── image_utils.py        # Utilitaires images
    └── profile_utils.py      # Utilitaires profil
```

## 🔧 Configuration

### Variables d'environnement

```env
# Configuration des utilisateurs
USERS_ENABLED=true
AVATAR_MAX_SIZE=5MB
AVATAR_ALLOWED_FORMATS=jpg,jpeg,png,webp
AVATAR_DEFAULT_SIZE=200x200

# Configuration des préférences
DEFAULT_LANGUAGE=fr
DEFAULT_TIMEZONE=Europe/Paris
DEFAULT_THEME=light

# Configuration des statistiques
STATS_RETENTION_DAYS=365
STATS_AGGREGATION_INTERVAL=24  # hours
```

### Dépendances requises

```bash
pip install pillow python-dateutil
```

## 📡 APIs disponibles

### 👤 Gestion du profil

#### Récupérer le profil utilisateur
```http
GET /api/users/profile/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Développeur passionné",
  "location": "Paris, France",
  "website": "https://johndoe.com",
  "birth_date": "1990-01-01",
  "avatar": {
    "url": "https://example.com/avatars/user123.jpg",
    "thumbnail": "https://example.com/avatars/user123_thumb.jpg"
  },
  "preferences": {
    "language": "fr",
    "timezone": "Europe/Paris",
    "theme": "light",
    "notifications": {
      "email": true,
      "push": true,
      "sms": false
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Modifier le profil
```http
PUT /api/users/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Développeur passionné par les nouvelles technologies",
  "location": "Paris, France",
  "website": "https://johndoe.com",
  "birth_date": "1990-01-01"
}
```

#### Récupérer le profil d'un autre utilisateur
```http
GET /api/users/profile/{user_id}/
Authorization: Bearer <access_token>
```

### 🖼️ Gestion des avatars

#### Uploader un avatar
```http
POST /api/users/avatar/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

avatar: [fichier image]
```

**Réponse:**
```json
{
  "id": 1,
  "user": 123,
  "image": "https://example.com/avatars/user123.jpg",
  "thumbnail": "https://example.com/avatars/user123_thumb.jpg",
  "size": 1024000,
  "width": 500,
  "height": 500,
  "format": "jpeg",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Supprimer l'avatar
```http
DELETE /api/users/avatar/
Authorization: Bearer <access_token>
```

#### Récupérer l'avatar
```http
GET /api/users/avatar/
Authorization: Bearer <access_token>
```

### ⚙️ Gestion des préférences

#### Récupérer les préférences
```http
GET /api/users/preferences/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "id": 1,
  "user": 123,
  "language": "fr",
  "timezone": "Europe/Paris",
  "theme": "light",
  "date_format": "DD/MM/YYYY",
  "time_format": "24h",
  "currency": "EUR",
  "notifications": {
    "email": true,
    "push": true,
    "sms": false,
    "marketing": false
  },
  "privacy": {
    "profile_visibility": "public",
    "show_email": false,
    "show_phone": false,
    "show_location": true
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Modifier les préférences
```http
PUT /api/users/preferences/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "language": "en",
  "timezone": "America/New_York",
  "theme": "dark",
  "notifications": {
    "email": true,
    "push": false,
    "sms": false,
    "marketing": false
  },
  "privacy": {
    "profile_visibility": "private",
    "show_email": false,
    "show_phone": false,
    "show_location": false
  }
}
```

### 📊 Historique des connexions

#### Récupérer l'historique des connexions
```http
GET /api/users/login-history/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "user": 123,
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "location": {
        "country": "France",
        "city": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522
      },
      "login_method": "email",
      "success": true,
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### Récupérer les connexions récentes
```http
GET /api/users/login-history/recent/
Authorization: Bearer <access_token>
```

### 📈 Statistiques utilisateur

#### Récupérer les statistiques
```http
GET /api/users/stats/
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "user_id": 123,
  "total_logins": 150,
  "last_login": "2024-01-01T10:00:00Z",
  "account_age_days": 365,
  "activity_score": 85,
  "login_frequency": {
    "daily": 5,
    "weekly": 35,
    "monthly": 150
  },
  "device_usage": {
    "desktop": 60,
    "mobile": 35,
    "tablet": 5
  },
  "location_stats": {
    "most_common_country": "France",
    "most_common_city": "Paris",
    "total_locations": 3
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Récupérer les statistiques d'activité
```http
GET /api/users/stats/activity/?period=30d
Authorization: Bearer <access_token>
```

**Réponse:**
```json
{
  "period": "30d",
  "total_logins": 45,
  "average_daily_logins": 1.5,
  "most_active_day": "Monday",
  "most_active_hour": 14,
  "activity_by_day": [
    {"date": "2024-01-01", "logins": 2},
    {"date": "2024-01-02", "logins": 1},
    {"date": "2024-01-03", "logins": 3}
  ],
  "activity_by_hour": [
    {"hour": 9, "logins": 5},
    {"hour": 14, "logins": 15},
    {"hour": 18, "logins": 8}
  ]
}
```

## 🛠️ Utilisation dans le code

### Service de profil

```python
from apps.users.services import ProfileService

profile_service = ProfileService()

# Récupérer le profil
profile = profile_service.get_profile(user)

# Modifier le profil
updated_profile = profile_service.update_profile(
    user=user,
    data={
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Nouvelle bio"
    }
)

# Récupérer le profil public
public_profile = profile_service.get_public_profile(user)
```

### Service d'avatar

```python
from apps.users.services import AvatarService

avatar_service = AvatarService()

# Uploader un avatar
avatar = avatar_service.upload_avatar(
    user=user,
    image_file=request.FILES['avatar']
)

# Redimensionner l'avatar
resized_avatar = avatar_service.resize_avatar(
    avatar=avatar,
    size=(200, 200)
)

# Supprimer l'avatar
avatar_service.delete_avatar(user)
```

### Service de statistiques

```python
from apps.users.services import StatsService

stats_service = StatsService()

# Récupérer les statistiques
stats = stats_service.get_user_stats(user)

# Calculer le score d'activité
activity_score = stats_service.calculate_activity_score(user)

# Récupérer l'historique d'activité
activity_history = stats_service.get_activity_history(
    user=user,
    period="30d"
)
```

### Décorateurs de profil

```python
from apps.users.decorators import profile_required, public_profile_only

@profile_required
def view_profile(request, user_id):
    """Vue nécessitant un profil complet"""
    user = get_object_or_404(User, id=user_id)
    return Response(ProfileSerializer(user.profile).data)

@public_profile_only
def view_public_profile(request, user_id):
    """Vue pour profil public uniquement"""
    user = get_object_or_404(User, id=user_id)
    return Response(PublicProfileSerializer(user.profile).data)
```

### Signaux de profil

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

## 🔧 Configuration avancée

### Configuration des avatars

```python
# settings.py
AVATAR_SETTINGS = {
    'MAX_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'webp'],
    'DEFAULT_SIZE': (200, 200),
    'THUMBNAIL_SIZE': (50, 50),
    'QUALITY': 85,
    'STORAGE_PATH': 'avatars/',
    'DEFAULT_AVATAR': 'default_avatar.png'
}
```

### Configuration des préférences

```python
# Préférences par défaut
DEFAULT_USER_PREFERENCES = {
    'language': 'fr',
    'timezone': 'Europe/Paris',
    'theme': 'light',
    'date_format': 'DD/MM/YYYY',
    'time_format': '24h',
    'currency': 'EUR',
    'notifications': {
        'email': True,
        'push': True,
        'sms': False,
        'marketing': False
    },
    'privacy': {
        'profile_visibility': 'public',
        'show_email': False,
        'show_phone': False,
        'show_location': True
    }
}
```

### Configuration des statistiques

```python
# Configuration des statistiques
STATS_CONFIG = {
    'RETENTION_DAYS': 365,
    'AGGREGATION_INTERVAL': 24,  # hours
    'ACTIVITY_SCORE_WEIGHTS': {
        'login_frequency': 0.4,
        'session_duration': 0.3,
        'feature_usage': 0.3
    },
    'LOCATION_DETECTION': True,
    'DEVICE_TRACKING': True
}
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.users

# Tests avec couverture
coverage run --source='apps.users' manage.py test apps.users
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.services import ProfileService, AvatarService

User = get_user_model()

class ProfileServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.profile_service = ProfileService()
    
    def test_get_profile(self):
        profile = self.profile_service.get_profile(self.user)
        
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.created_at)
    
    def test_update_profile(self):
        updated_profile = self.profile_service.update_profile(
            user=self.user,
            data={
                'first_name': 'John',
                'last_name': 'Doe',
                'bio': 'Test bio'
            }
        )
        
        self.assertEqual(updated_profile.first_name, 'John')
        self.assertEqual(updated_profile.last_name, 'Doe')
        self.assertEqual(updated_profile.bio, 'Test bio')

class AvatarServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.avatar_service = AvatarService()
    
    def test_upload_avatar(self):
        # Créer un fichier image de test
        from PIL import Image
        import io
        
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        
        avatar = self.avatar_service.upload_avatar(
            user=self.user,
            image_file=image_file
        )
        
        self.assertEqual(avatar.user, self.user)
        self.assertIsNotNone(avatar.image)
        self.assertEqual(avatar.width, 100)
        self.assertEqual(avatar.height, 100)
```

## 📊 Intégration avec d'autres apps

### Intégration avec l'app Authentication

```python
# Mise à jour automatique du profil lors de la connexion
from apps.authentication.signals import user_logged_in
from apps.users.services import StatsService

@receiver(user_logged_in)
def update_login_stats(sender, user, request, **kwargs):
    stats_service = StatsService()
    stats_service.record_login(
        user=user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
```

### Intégration avec l'app Notifications

```python
# Notifications basées sur les préférences utilisateur
from apps.notifications.services import NotificationService
from apps.users.models import UserPreference

def send_notification_to_user(user, template, context):
    preferences = UserPreference.objects.get(user=user)
    notification_service = NotificationService()
    
    if preferences.notifications.get('email', True):
        notification_service.send_email(
            template=template,
            recipient=user.email,
            context=context
        )
    
    if preferences.notifications.get('push', True):
        notification_service.send_push(
            template=template,
            recipient=user.device_token,
            context=context
        )
```

## 🐛 Dépannage

### Problèmes courants

1. **Avatar non uploadé** : Vérifiez les permissions de fichier et la taille
2. **Préférences non sauvegardées** : Vérifiez la validation des données
3. **Statistiques incorrectes** : Vérifiez la configuration des statistiques
4. **Performance lente** : Optimisez les requêtes et activez le cache

### Configuration de debug

```python
# settings.py
DEBUG_USERS = True
AVATAR_DEBUG = True
STATS_DEBUG = True
```

## 📚 Ressources

- [Django User Model](https://docs.djangoproject.com/en/stable/topics/auth/customizing/)
- [Pillow (PIL)](https://pillow.readthedocs.io/)
- [Django File Uploads](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)

---

*Dernière mise à jour: Septembre 2024*
