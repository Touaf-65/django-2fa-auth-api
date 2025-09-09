# 🌍 Internationalization App

## Vue d'ensemble

L'app **Internationalization** fournit un système complet d'internationalisation avec traduction automatique, gestion des langues et support multilingue pour les APIs.

## 🚀 Fonctionnalités

### ✅ Gestion des langues
- Support de multiples langues
- Configuration des langues par défaut
- Détection automatique de la langue
- Préférences de langue par utilisateur

### ✅ Traduction automatique
- **Google Translate** API
- **Microsoft Translator** API
- **DeepL** API
- **OpenAI** GPT pour traduction contextuelle
- Cache intelligent des traductions

### ✅ Gestion du contenu
- Contenu multilingue structuré
- Clés de traduction pour l'interface
- Traductions en temps réel
- Gestion des versions de traduction

### ✅ Services avancés
- Détection automatique de langue
- Middleware de traduction
- Cache des traductions
- Jobs de traduction asynchrones

## 📁 Structure

```
apps/internationalization/
├── models/
│   ├── language.py              # Langues supportées
│   ├── content.py              # Contenu à traduire
│   ├── content_translation.py  # Traductions
│   ├── translation_key.py      # Clés de traduction
│   ├── language_preference.py  # Préférences utilisateur
│   ├── translation_provider.py # Fournisseurs de traduction
│   ├── translation_job.py      # Jobs de traduction
│   └── translation_cache.py    # Cache des traductions
├── serializers/
│   ├── language_serializers.py # Sérialiseurs langues
│   ├── content_serializers.py  # Sérialiseurs contenu
│   └── translation_serializers.py # Sérialiseurs traduction
├── views/
│   ├── language_views.py       # Vues langues
│   ├── content_views.py        # Vues contenu
│   └── translation_views.py    # Vues traduction
├── services/
│   ├── auto_translation_service.py # Service traduction auto
│   ├── translation_cache_service.py # Service cache
│   └── language_detection_service.py # Service détection
├── middleware/
│   ├── language_detection_middleware.py # Détection langue
│   ├── translation_middleware.py # Traduction automatique
│   └── language_preference_middleware.py # Préférences
└── utils/
    ├── translation_utils.py    # Utilitaires traduction
    └── language_utils.py       # Utilitaires langue
```

## 🔧 Configuration

### Variables d'environnement requises

```env
# Fournisseurs de traduction
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
MICROSOFT_TRANSLATE_API_KEY=your_microsoft_translate_api_key
DEEPL_API_KEY=your_deepl_api_key
OPENAI_API_KEY=your_openai_api_key

# Configuration de l'app
DEFAULT_LANGUAGE=fr
SUPPORTED_LANGUAGES=fr,en,es,de,it,pt,ru,zh,ja,ko
FALLBACK_LANGUAGE=en

# Cache des traductions
TRANSLATION_CACHE_TTL=3600  # 1 heure en secondes
TRANSLATION_CACHE_MAX_SIZE=10000

# Détection de langue
LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD=0.8
AUTO_TRANSLATE_ENABLED=true
```

### Installation des dépendances

```bash
pip install googletrans==4.0.0rc1
pip install requests
pip install openai
```

## 📡 APIs disponibles

### 🌐 Gestion des langues

#### Lister les langues supportées
```http
GET /api/internationalization/languages/
```

**Réponse:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "code": "fr",
      "name": "Français",
      "native_name": "Français",
      "is_active": true,
      "is_default": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "code": "en",
      "name": "English",
      "native_name": "English",
      "is_active": true,
      "is_default": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Ajouter une nouvelle langue
```http
POST /api/internationalization/languages/
Content-Type: application/json

{
  "code": "es",
  "name": "Spanish",
  "native_name": "Español",
  "is_active": true
}
```

### 📝 Gestion du contenu

#### Créer du contenu à traduire
```http
POST /api/internationalization/content/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "identifier": "welcome_message",
  "original_text": "Bienvenue sur notre plateforme !",
  "language": "fr",
  "category": "ui",
  "context": "Page d'accueil"
}
```

#### Récupérer le contenu traduit
```http
GET /api/internationalization/content/{id}/
Accept-Language: en
```

**Réponse:**
```json
{
  "id": 1,
  "identifier": "welcome_message",
  "original_text": "Bienvenue sur notre plateforme !",
  "translated_text": "Welcome to our platform!",
  "source_language": "fr",
  "target_language": "en",
  "category": "ui",
  "context": "Page d'accueil",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 🔄 Traduction automatique

#### Traduire du texte
```http
POST /api/internationalization/auto-translate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "Bonjour le monde",
  "target_language": "en",
  "source_language": "fr",
  "provider": "google"
}
```

**Réponse:**
```json
{
  "original_text": "Bonjour le monde",
  "translated_text": "Hello world",
  "source_language": "fr",
  "target_language": "en",
  "provider": "google",
  "confidence": 0.95,
  "cached": false
}
```

#### Traduction en lot
```http
POST /api/internationalization/auto-translate/batch/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "texts": [
    "Bonjour",
    "Au revoir",
    "Merci"
  ],
  "target_language": "en",
  "source_language": "fr",
  "provider": "google"
}
```

### 🔍 Détection de langue

#### Détecter la langue d'un texte
```http
POST /api/internationalization/detect-language/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "Hello, how are you today?"
}
```

**Réponse:**
```json
{
  "text": "Hello, how are you today?",
  "detected_language": "en",
  "confidence": 0.95,
  "alternative_languages": [
    {
      "language": "en",
      "confidence": 0.95
    },
    {
      "language": "fr",
      "confidence": 0.02
    }
  ]
}
```

### 🔑 Clés de traduction

#### Créer une clé de traduction
```http
POST /api/internationalization/translation-keys/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "key": "user.profile.title",
  "default_text": "User Profile",
  "category": "ui",
  "description": "Titre de la page de profil utilisateur"
}
```

#### Récupérer les traductions d'une clé
```http
GET /api/internationalization/translation-keys/{id}/translations/
Accept-Language: fr
```

### 👤 Préférences utilisateur

#### Définir la langue préférée
```http
POST /api/internationalization/language-preferences/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "language": "fr",
  "auto_translate": true,
  "fallback_language": "en"
}
```

#### Récupérer les préférences
```http
GET /api/internationalization/language-preferences/
Authorization: Bearer <access_token>
```

## 🛠️ Utilisation dans le code

### Services de traduction

```python
from apps.internationalization.services import AutoTranslationService

# Service de traduction automatique
translation_service = AutoTranslationService()

# Traduction simple
result = translation_service.translate(
    text="Bonjour le monde",
    target_language="en",
    source_language="fr",
    provider="google"
)
print(result.translated_text)  # "Hello world"

# Traduction avec cache
result = translation_service.translate_with_cache(
    text="Bonjour le monde",
    target_language="en"
)
```

### Service de détection de langue

```python
from apps.internationalization.services import LanguageDetectionService

detection_service = LanguageDetectionService()

# Détecter la langue
result = detection_service.detect_language("Hello world")
print(result.language)  # "en"
print(result.confidence)  # 0.95
```

### Service de cache

```python
from apps.internationalization.services import TranslationCacheService

cache_service = TranslationCacheService()

# Mettre en cache une traduction
cache_service.set_translation(
    text="Bonjour",
    target_language="en",
    translated_text="Hello",
    provider="google"
)

# Récupérer du cache
cached = cache_service.get_translation("Bonjour", "en")
if cached:
    print(cached.translated_text)  # "Hello"
```

### Middleware de traduction

```python
# Le middleware traduit automatiquement les réponses
# selon la langue de l'utilisateur

# Dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'apps.internationalization.middleware.LanguageDetectionMiddleware',
    'apps.internationalization.middleware.TranslationMiddleware',
    'apps.internationalization.middleware.LanguagePreferenceMiddleware',
]
```

### Utilitaires de traduction

```python
from apps.internationalization.utils import get_translated_text

# Récupérer du texte traduit
text = get_translated_text(
    identifier="welcome_message",
    language="en",
    fallback="Welcome!"
)
```

## 🔧 Configuration des fournisseurs

### Google Translate

```python
# Configuration
GOOGLE_TRANSLATE_API_KEY = "your_api_key"

# Utilisation
from apps.internationalization.services import AutoTranslationService

service = AutoTranslationService()
result = service.translate(
    text="Hello",
    target_language="fr",
    provider="google"
)
```

### Microsoft Translator

```python
# Configuration
MICROSOFT_TRANSLATE_API_KEY = "your_api_key"
MICROSOFT_TRANSLATE_REGION = "your_region"

# Utilisation
result = service.translate(
    text="Hello",
    target_language="fr",
    provider="microsoft"
)
```

### DeepL

```python
# Configuration
DEEPL_API_KEY = "your_api_key"

# Utilisation
result = service.translate(
    text="Hello",
    target_language="fr",
    provider="deepl"
)
```

### OpenAI

```python
# Configuration
OPENAI_API_KEY = "your_api_key"
OPENAI_MODEL = "gpt-3.5-turbo"

# Utilisation
result = service.translate(
    text="Hello",
    target_language="fr",
    provider="openai"
)
```

## 🌐 Intégration frontend

### React avec react-i18next

```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Configuration
i18n
  .use(initReactI18next)
  .init({
    lng: 'fr',
    fallbackLng: 'en',
    resources: {
      fr: {
        translation: {
          welcome: "Bienvenue"
        }
      },
      en: {
        translation: {
          welcome: "Welcome"
        }
      }
    }
  });

// Utilisation
import { useTranslation } from 'react-i18next';

function App() {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <button onClick={() => i18n.changeLanguage('en')}>
        English
      </button>
    </div>
  );
}
```

### Vue avec vue-i18n

```javascript
import { createI18n } from 'vue-i18n';

const i18n = createI18n({
  locale: 'fr',
  fallbackLocale: 'en',
  messages: {
    fr: {
      welcome: 'Bienvenue'
    },
    en: {
      welcome: 'Welcome'
    }
  }
});

// Utilisation
<template>
  <div>
    <h1>{{ $t('welcome') }}</h1>
    <button @click="$i18n.locale = 'en'">English</button>
  </div>
</template>
```

## 🧪 Tests

### Exécuter les tests

```bash
# Tests unitaires
python manage.py test apps.internationalization

# Tests avec couverture
coverage run --source='apps.internationalization' manage.py test apps.internationalization
coverage report
```

### Exemples de tests

```python
from django.test import TestCase
from apps.internationalization.services import AutoTranslationService

class AutoTranslationServiceTestCase(TestCase):
    def setUp(self):
        self.service = AutoTranslationService()
    
    def test_translate_text(self):
        result = self.service.translate(
            text="Hello",
            target_language="fr",
            provider="google"
        )
        
        self.assertEqual(result.original_text, "Hello")
        self.assertEqual(result.target_language, "fr")
        self.assertIsNotNone(result.translated_text)
    
    def test_translation_cache(self):
        # Premier appel
        result1 = self.service.translate_with_cache(
            text="Hello",
            target_language="fr"
        )
        
        # Deuxième appel (devrait être en cache)
        result2 = self.service.translate_with_cache(
            text="Hello",
            target_language="fr"
        )
        
        self.assertTrue(result2.cached)
```

## 📊 Monitoring et analytics

### Métriques disponibles

```python
from apps.internationalization.models import TranslationJob

# Statistiques de traduction
stats = {
    'total_translations': TranslationJob.objects.count(),
    'translations_by_provider': TranslationJob.objects.values('provider').annotate(count=Count('id')),
    'translations_by_language': TranslationJob.objects.values('target_language').annotate(count=Count('id')),
    'cache_hit_rate': cache_service.get_hit_rate(),
    'average_translation_time': TranslationJob.objects.aggregate(avg_time=Avg('processing_time'))
}
```

### Logs de traduction

```python
import logging

# Activer les logs de traduction
logging.getLogger('apps.internationalization').setLevel(logging.DEBUG)

# Les logs incluent:
# - Requêtes de traduction
# - Utilisation du cache
# - Erreurs de traduction
# - Performance des fournisseurs
```

## 🐛 Dépannage

### Problèmes courants

1. **Erreur API** : Vérifiez les clés API des fournisseurs
2. **Traduction lente** : Activez le cache des traductions
3. **Langue non détectée** : Ajustez le seuil de confiance
4. **Cache plein** : Configurez la taille maximale du cache

### Configuration de debug

```python
# settings.py
DEBUG_TRANSLATION = True
TRANSLATION_LOG_LEVEL = 'DEBUG'
TRANSLATION_CACHE_DEBUG = True
```

## 📚 Ressources

- [Google Translate API](https://cloud.google.com/translate/docs)
- [Microsoft Translator](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/)
- [DeepL API](https://www.deepl.com/docs-api)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [react-i18next](https://react.i18next.com/)
- [vue-i18n](https://vue-i18n.intlify.dev/)

---

*Dernière mise à jour: Septembre 2024*
