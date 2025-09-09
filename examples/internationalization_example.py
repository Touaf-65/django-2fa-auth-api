"""
Exemple d'utilisation de l'app Internationalization
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.internationalization.services import LanguageService, TranslationService, ContentService
from apps.internationalization.models import Language, TranslationKey, Content
from django.contrib.auth import get_user_model

User = get_user_model()


def example_language_management():
    """Exemple de gestion des langues"""
    print("🌍 === Gestion des Langues ===")
    
    language_service = LanguageService()
    
    # Initialiser les langues par défaut
    print("1. Initialisation des langues par défaut...")
    languages = language_service.initialize_default_languages()
    print(f"   {len(languages)} langues créées")
    
    # Récupérer la langue par défaut
    default_language = language_service.get_default_language()
    print(f"2. Langue par défaut: {default_language.name} ({default_language.code})")
    
    # Récupérer toutes les langues actives
    active_languages = language_service.get_active_languages()
    print(f"3. Langues actives: {len(active_languages)}")
    for lang in active_languages[:5]:  # Afficher les 5 premières
        print(f"   - {lang.display_name} ({lang.code})")
    
    # Statistiques des langues
    stats = language_service.get_language_stats()
    print(f"4. Statistiques: {stats['total_languages']} langues total")


def example_translation_management():
    """Exemple de gestion des traductions"""
    print("\n🔄 === Gestion des Traductions ===")
    
    translation_service = TranslationService()
    
    # Récupérer les langues
    english = Language.objects.get(code='en')
    french = Language.objects.get(code='fr')
    spanish = Language.objects.get(code='es')
    
    # Créer une clé de traduction
    print("1. Création d'une clé de traduction...")
    translation_key = translation_service.create_translation_key(
        key="welcome_message",
        source_text="Welcome to our amazing platform!",
        source_language=english,
        context="ui",
        description="Message de bienvenue principal"
    )
    print(f"   Clé créée: {translation_key.key}")
    
    # Traduire vers le français
    print("2. Traduction vers le français...")
    french_translation = translation_service.translate_key(
        translation_key=translation_key,
        target_language=french,
        use_auto_translation=True
    )
    print(f"   Traduction: {french_translation.translated_text}")
    print(f"   Statut: {french_translation.status}")
    print(f"   Confiance: {french_translation.confidence_score}")
    
    # Traduire vers l'espagnol
    print("3. Traduction vers l'espagnol...")
    spanish_translation = translation_service.translate_key(
        translation_key=translation_key,
        target_language=spanish,
        use_auto_translation=True
    )
    print(f"   Traduction: {spanish_translation.translated_text}")
    
    # Récupérer une traduction
    print("4. Récupération d'une traduction...")
    retrieved_translation = translation_service.get_translation("welcome_message", french)
    print(f"   Traduction récupérée: {retrieved_translation}")
    
    # Statistiques
    stats = translation_service.get_translation_stats()
    print(f"5. Statistiques: {stats['total_translations']} traductions total")


def example_content_management():
    """Exemple de gestion du contenu multilingue"""
    print("\n📄 === Gestion du Contenu Multilingue ===")
    
    content_service = ContentService()
    
    # Récupérer les langues
    english = Language.objects.get(code='en')
    french = Language.objects.get(code='fr')
    
    # Créer du contenu
    print("1. Création de contenu...")
    content = content_service.create_content(
        content_type="page",
        identifier="about_us",
        title="About Our Company",
        description="Learn more about our innovative solutions",
        source_language=english,
        tags=["company", "information"]
    )
    print(f"   Contenu créé: {content.title}")
    
    # Traduire le contenu
    print("2. Traduction du contenu...")
    content_translation = content_service.translate_content(
        content=content,
        target_language=french,
        use_auto_translation=True
    )
    print(f"   Titre traduit: {content_translation.translated_title}")
    print(f"   Description traduite: {content_translation.translated_description}")
    
    # Récupérer le contenu dans une langue
    print("3. Récupération du contenu en français...")
    content_in_french = content_service.get_content_in_language(content, french)
    print(f"   Titre: {content_in_french['title']}")
    print(f"   Langue: {content_in_french['language']}")
    print(f"   Original: {content_in_french['is_original']}")
    
    # Recherche multilingue
    print("4. Recherche multilingue...")
    search_results = content_service.search_content(
        query="company",
        language=french,
        limit=5
    )
    print(f"   Résultats trouvés: {len(search_results)}")
    for result in search_results:
        print(f"   - {result['title']} ({result['match_type']})")


def example_auto_translation():
    """Exemple de traduction automatique"""
    print("\n🤖 === Traduction Automatique ===")
    
    from apps.internationalization.services import AutoTranslationService
    
    auto_service = AutoTranslationService()
    
    # Test de traduction
    print("1. Test de traduction automatique...")
    result = auto_service.translate_text(
        text="Hello, how are you today?",
        source_lang="en",
        target_lang="fr",
        provider="mock"  # Utiliser le fournisseur mock pour les tests
    )
    
    if result['success']:
        print(f"   Texte original: {result['text']}")
        print(f"   Traduction: {result['translated_text']}")
        print(f"   Fournisseur: {result['provider']}")
        print(f"   Confiance: {result['confidence']}")
    else:
        print(f"   Erreur: {result['error']}")
    
    # Test de traduction en lot
    print("2. Test de traduction en lot...")
    texts = [
        "Welcome to our platform",
        "Thank you for your visit",
        "Have a great day"
    ]
    
    batch_results = auto_service.translate_batch(
        texts=texts,
        source_lang="en",
        target_lang="es",
        provider="mock"
    )
    
    for i, result in enumerate(batch_results):
        if result['success']:
            print(f"   {i+1}. {result['text']} -> {result['translated_text']}")
        else:
            print(f"   {i+1}. Erreur: {result['error']}")


def example_user_preferences():
    """Exemple de gestion des préférences utilisateur"""
    print("\n👤 === Préférences Utilisateur ===")
    
    language_service = LanguageService()
    
    # Récupérer les langues
    english = Language.objects.get(code='en')
    french = Language.objects.get(code='fr')
    spanish = Language.objects.get(code='es')
    
    # Créer un utilisateur de test (si nécessaire)
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123'
        )
        print("   Utilisateur de test créé")
    
    # Définir les préférences de langue
    print("1. Définition des préférences de langue...")
    preference = language_service.set_user_language_preference(
        user=user,
        primary_language=french,
        secondary_languages=[english, spanish],
        auto_detect=True,
        auto_translate=True
    )
    print(f"   Langue primaire: {preference.primary_language.name}")
    print(f"   Langues secondaires: {[lang.name for lang in preference.secondary_languages.all()]}")
    
    # Récupérer la langue préférée
    print("2. Récupération de la langue préférée...")
    preferred_language = language_service.get_user_preferred_language(user)
    print(f"   Langue préférée: {preferred_language.name}")
    
    # Mettre à jour les statistiques
    print("3. Mise à jour des statistiques...")
    language_service.update_language_usage(french)
    print("   Statistiques mises à jour")


def main():
    """Fonction principale d'exemple"""
    print("🚀 === Exemple d'utilisation de l'app Internationalization ===\n")
    
    try:
        # Exécuter les exemples
        example_language_management()
        example_translation_management()
        example_content_management()
        example_auto_translation()
        example_user_preferences()
        
        print("\n✅ === Tous les exemples ont été exécutés avec succès ! ===")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

