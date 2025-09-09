# 🌍 App Internationalization - Traductions Automatiques

## Vue d'ensemble

L'app **Internationalization** est un système complet de gestion multilingue avec traductions automatiques pour le starter Django 2FA Auth API. Elle permet de gérer facilement le contenu multilingue, les traductions automatiques via plusieurs fournisseurs, et la détection automatique de la langue des utilisateurs.

## 🚀 Fonctionnalités Principales

### 1. **Gestion des Langues**
- Support de 30+ langues avec codes ISO 639-1
- Détection automatique de la langue utilisateur
- Préférences de langue personnalisables
- Support des langues RTL (Right-to-Left)
- Métadonnées complètes (drapeaux, régions, etc.)

### 2. **Traductions Automatiques**
- **Google Translate** : Traduction de haute qualité
- **Microsoft Translator** : Intégration Azure Cognitive Services
- **DeepL** : Traduction premium européenne
- **OpenAI GPT** : Traduction et évaluation de qualité
- **Mode Mock** : Pour les tests et développement
- Cache intelligent des traductions
- Évaluation automatique de la qualité

### 3. **Gestion du Contenu Multilingue**
- Contenu générique multilingue
- Traductions de pages, articles, produits
- Templates d'emails et notifications multilingues
- SEO multilingue (meta titles, descriptions, slugs)
- Recherche multilingue intelligente

### 4. **Système de Clés de Traduction**
- Clés de traduction réutilisables
- Contexte de traduction (UI, email, notification, etc.)
- Système de priorités
- Statistiques d'utilisation
- Tags et métadonnées

### 5. **Workflow de Traduction**
- Demandes de traduction en lot
- Révision humaine des traductions automatiques
- Système d'approbation
- Suivi des statuts (pending, auto_translated, human_translated, reviewed, approved)
- Notes et commentaires

## 🏗️ Architecture

### Modèles Principaux

#### **Language**
```python
- code: Code ISO 639-1 (en, fr, es, etc.)
- name: Nom en anglais
- native_name: Nom natif
- is_active: Langue active
- is_default: Langue par défaut
- is_rtl: Langue de droite à gauche
- flag_emoji: Emoji du drapeau
- auto_translate_enabled: Traduction automatique activée
- translation_quality: Qualité de traduction
```

#### **TranslationKey**
```python
- key: Clé unique de traduction
- source_text: Texte source
- source_language: Langue source
- context: Contexte (ui, email, notification, etc.)
- tags: Tags de classification
- priority: Priorité (high, medium, low)
```

#### **Translation**
```python
- translation_key: Clé traduite
- language: Langue cible
- translated_text: Texte traduit
- status: Statut de la traduction
- confidence_score: Score de confiance (0-1)
- translation_service: Service utilisé
- translated_by: Traducteur
- reviewed_by: Réviseur
```

#### **Content & ContentTranslation**
```python
- content_type: Type de contenu (page, article, product, etc.)
- identifier: Identifiant unique
- title/description: Contenu source
- translated_title/description: Contenu traduit
- meta_title/meta_description: SEO
- slug: URL-friendly
```

### Services

#### **AutoTranslationService**
- Gestion des fournisseurs de traduction
- Cache intelligent
- Traduction en lot
- Évaluation de qualité

#### **TranslationService**
- Gestion des clés de traduction
- Workflow de traduction
- Statistiques et rapports

#### **LanguageService**
- Détection de langue
- Préférences utilisateur
- Initialisation des langues par défaut

#### **ContentService**
- Gestion du contenu multilingue
- Recherche intelligente
- Publication et révision

### Middleware

#### **LanguageMiddleware**
- Détection automatique de la langue
- En-têtes HTTP (Accept-Language)
- Session et paramètres utilisateur
- Mise à jour des statistiques

## 🔧 Configuration

### Variables d'Environnement

```bash
# Configuration des apps
APPS_CONFIG_MODE=default
ENABLE_INTERNATIONALIZATION=true

# Fournisseurs de traduction
DEFAULT_TRANSLATION_PROVIDER=mock  # mock, google, microsoft, deepl, openai

# Google Translate
GOOGLE_TRANSLATE_API_KEY=your_api_key

# Microsoft Translator
MICROSOFT_TRANSLATE_API_KEY=your_api_key
MICROSOFT_TRANSLATE_REGION=global

# DeepL
DEEPL_API_KEY=your_api_key

# OpenAI
OPENAI_API_KEY=your_api_key
```

### Configuration des Apps

L'app est configurée dans `config/settings/apps_config.py` :

```python
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
```

## 📡 API Endpoints

### Langues
- `GET /api/internationalization/languages/` - Liste des langues
- `GET /api/internationalization/languages/default/` - Langue par défaut
- `POST /api/internationalization/languages/initialize_defaults/` - Initialiser les langues
- `GET /api/internationalization/language-stats/` - Statistiques des langues

### Préférences de Langue
- `GET /api/internationalization/language-preferences/my_preferences/` - Mes préférences
- `POST /api/internationalization/language-preferences/set_preferences/` - Définir préférences
- `POST /api/internationalization/language-preferences/detect_language/` - Détecter langue

### Traductions
- `GET /api/internationalization/translation-keys/` - Clés de traduction
- `POST /api/internationalization/translation-keys/{id}/translate/` - Traduire une clé
- `GET /api/internationalization/translations/` - Traductions
- `POST /api/internationalization/translations/{id}/review/` - Réviser traduction
- `GET /api/internationalization/translation-stats/` - Statistiques

### Contenu Multilingue
- `GET /api/internationalization/content/` - Contenu
- `GET /api/internationalization/content/{id}/get_in_language/` - Contenu en langue
- `POST /api/internationalization/content/{id}/translate/` - Traduire contenu
- `GET /api/internationalization/content-search/` - Recherche multilingue

### Traduction Automatique
- `POST /api/internationalization/auto-translate/` - Traduction directe

## 🚀 Utilisation

### 1. Initialisation

```python
# Initialiser les langues par défaut
from apps.internationalization.services import LanguageService

language_service = LanguageService()
languages = language_service.initialize_default_languages()
```

### 2. Détection de Langue

```python
# Le middleware détecte automatiquement la langue
# Accès via request.language et request.language_code
def my_view(request):
    language = request.language
    print(f"Langue détectée: {language.name}")
```

### 3. Traduction de Contenu

```python
from apps.internationalization.services import TranslationService

# Créer une clé de traduction
translation_service = TranslationService()
key = translation_service.create_translation_key(
    key="welcome_message",
    source_text="Welcome to our platform!",
    source_language=english_language,
    context="ui"
)

# Traduire vers une autre langue
translation = translation_service.translate_key(
    translation_key=key,
    target_language=french_language,
    use_auto_translation=True
)
```

### 4. Contenu Multilingue

```python
from apps.internationalization.services import ContentService

# Créer du contenu
content_service = ContentService()
content = content_service.create_content(
    content_type="page",
    identifier="about_us",
    title="About Us",
    description="Learn more about our company",
    source_language=english_language
)

# Traduire le contenu
translation = content_service.translate_content(
    content=content,
    target_language=french_language,
    use_auto_translation=True
)
```

### 5. Recherche Multilingue

```python
# Rechercher du contenu
results = content_service.search_content(
    query="welcome",
    language=french_language,
    content_type="page"
)
```

## 🔧 Configuration des Fournisseurs

### Google Translate
```python
# settings.py
GOOGLE_TRANSLATE_API_KEY = "your_api_key"
DEFAULT_TRANSLATION_PROVIDER = "google"
```

### Microsoft Translator
```python
# settings.py
MICROSOFT_TRANSLATE_API_KEY = "your_api_key"
MICROSOFT_TRANSLATE_REGION = "global"
DEFAULT_TRANSLATION_PROVIDER = "microsoft"
```

### DeepL
```python
# settings.py
DEEPL_API_KEY = "your_api_key"
DEFAULT_TRANSLATION_PROVIDER = "deepl"
```

### OpenAI
```python
# settings.py
OPENAI_API_KEY = "your_api_key"
DEFAULT_TRANSLATION_PROVIDER = "openai"
```

## 📊 Statistiques et Monitoring

L'app fournit des statistiques complètes :
- Nombre de traductions par langue
- Qualité des traductions automatiques
- Langues les plus utilisées
- Contenu le plus traduit
- Performance des fournisseurs

## 🎯 Cas d'Usage

1. **E-commerce Multilingue** : Produits, catégories, descriptions
2. **Blog/News Multilingue** : Articles, pages, contenu
3. **Application SaaS** : Interface utilisateur, emails, notifications
4. **Documentation** : Guides, FAQ, aide contextuelle
5. **Marketing** : Landing pages, campagnes, contenu SEO

## 🔒 Sécurité

- Validation des entrées utilisateur
- Sanitisation du contenu traduit
- Gestion des erreurs de traduction
- Cache sécurisé des traductions
- Permissions granulaires

## 🚀 Performance

- Cache intelligent des traductions
- Traduction en lot
- Indexation optimisée
- Lazy loading des traductions
- Compression des réponses

## 📈 Évolutivité

- Support de nouveaux fournisseurs
- Plugins de traduction personnalisés
- Intégration avec des services externes
- API extensible
- Monitoring et alertes

---

**L'app Internationalization transforme votre application Django en une plateforme véritablement multilingue avec des traductions automatiques de qualité professionnelle !** 🌍✨

