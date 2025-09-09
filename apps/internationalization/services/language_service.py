"""
Service de gestion des langues
"""
from typing import List, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.internationalization.models import Language, LanguagePreference

User = get_user_model()


class LanguageService:
    """
    Service de gestion des langues et préférences utilisateur
    """
    
    def __init__(self):
        self.default_language_code = 'en'
    
    def get_or_create_default_language(self) -> Language:
        """
        Récupère ou crée la langue par défaut
        
        Returns:
            Language par défaut
        """
        language, created = Language.objects.get_or_create(
            code=self.default_language_code,
            defaults={
                'name': 'English',
                'native_name': 'English',
                'is_default': True,
                'is_active': True,
                'flag_emoji': '🇺🇸',
                'country_code': 'US',
                'region': 'North America'
            }
        )
        
        if created:
            # S'assurer qu'une seule langue est par défaut
            Language.objects.filter(is_default=True).exclude(id=language.id).update(is_default=False)
        
        return language
    
    def create_language(self, code: str, name: str, native_name: str,
                       flag_emoji: str = '', country_code: str = '',
                       region: str = '', is_rtl: bool = False) -> Language:
        """
        Crée une nouvelle langue
        
        Args:
            code: Code de la langue (ISO 639-1)
            name: Nom de la langue en anglais
            native_name: Nom natif de la langue
            flag_emoji: Emoji du drapeau
            country_code: Code du pays
            region: Région
            is_rtl: Langue de droite à gauche
        
        Returns:
            Language créée
        """
        language = Language.objects.create(
            code=code,
            name=name,
            native_name=native_name,
            flag_emoji=flag_emoji,
            country_code=country_code,
            region=region,
            is_rtl=is_rtl,
            is_active=True
        )
        
        return language
    
    def get_active_languages(self) -> List[Language]:
        """
        Récupère toutes les langues actives
        
        Returns:
            Liste des langues actives
        """
        return list(Language.objects.filter(is_active=True).order_by('name'))
    
    def get_default_language(self) -> Optional[Language]:
        """
        Récupère la langue par défaut
        
        Returns:
            Language par défaut ou None
        """
        try:
            return Language.objects.get(is_default=True, is_active=True)
        except Language.DoesNotExist:
            return self.get_or_create_default_language()
    
    def detect_user_language(self, request) -> Language:
        """
        Détecte la langue préférée de l'utilisateur
        
        Args:
            request: Requête HTTP
        
        Returns:
            Language détectée
        """
        # 1. Vérifier les paramètres de l'utilisateur connecté
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                preference = request.user.language_preference
                return preference.primary_language
            except LanguagePreference.DoesNotExist:
                pass
        
        # 2. Vérifier les paramètres de session
        session_language = request.session.get('language')
        if session_language:
            try:
                return Language.objects.get(code=session_language, is_active=True)
            except Language.DoesNotExist:
                pass
        
        # 3. Vérifier les paramètres de requête
        query_language = request.GET.get('lang') or request.GET.get('language')
        if query_language:
            try:
                return Language.objects.get(code=query_language, is_active=True)
            except Language.DoesNotExist:
                pass
        
        # 4. Vérifier les en-têtes HTTP
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_language:
            detected_language = self._parse_accept_language(accept_language)
            if detected_language:
                return detected_language
        
        # 5. Fallback vers la langue par défaut
        return self.get_default_language()
    
    def _parse_accept_language(self, accept_language: str) -> Optional[Language]:
        """
        Parse l'en-tête Accept-Language
        
        Args:
            accept_language: Valeur de l'en-tête Accept-Language
        
        Returns:
            Language détectée ou None
        """
        # Parse simple des langues acceptées
        languages = []
        for lang in accept_language.split(','):
            lang = lang.strip().split(';')[0].split('-')[0].lower()
            if len(lang) == 2:  # Code ISO 639-1
                languages.append(lang)
        
        # Chercher la première langue supportée
        for lang_code in languages:
            try:
                return Language.objects.get(code=lang_code, is_active=True)
            except Language.DoesNotExist:
                continue
        
        return None
    
    def set_user_language_preference(self, user: User, primary_language: Language,
                                   secondary_languages: List[Language] = None,
                                   auto_detect: bool = True,
                                   auto_translate: bool = True) -> LanguagePreference:
        """
        Définit les préférences de langue d'un utilisateur
        
        Args:
            user: Utilisateur
            primary_language: Langue primaire
            secondary_languages: Langues secondaires
            auto_detect: Détection automatique
            auto_translate: Traduction automatique
        
        Returns:
            LanguagePreference créée ou mise à jour
        """
        preference, created = LanguagePreference.objects.get_or_create(
            user=user,
            defaults={
                'primary_language': primary_language,
                'auto_detect_language': auto_detect,
                'auto_translate_enabled': auto_translate
            }
        )
        
        if not created:
            preference.primary_language = primary_language
            preference.auto_detect_language = auto_detect
            preference.auto_translate_enabled = auto_translate
            preference.save()
        
        if secondary_languages:
            preference.secondary_languages.set(secondary_languages)
        
        return preference
    
    def get_user_language_preference(self, user: User) -> Optional[LanguagePreference]:
        """
        Récupère les préférences de langue d'un utilisateur
        
        Args:
            user: Utilisateur
        
        Returns:
            LanguagePreference ou None
        """
        try:
            return user.language_preference
        except LanguagePreference.DoesNotExist:
            return None
    
    def get_user_preferred_language(self, user: User, 
                                  available_languages: List[Language] = None) -> Language:
        """
        Récupère la langue préférée d'un utilisateur
        
        Args:
            user: Utilisateur
            available_languages: Langues disponibles (optionnel)
        
        Returns:
            Language préférée
        """
        preference = self.get_user_language_preference(user)
        
        if preference:
            return preference.get_preferred_language(available_languages)
        
        # Fallback vers la langue par défaut
        return self.get_default_language()
    
    def update_language_usage(self, language: Language) -> None:
        """
        Met à jour les statistiques d'utilisation d'une langue
        
        Args:
            language: Langue à mettre à jour
        """
        language.translation_count += 1
        language.last_used = timezone.now()
        language.save()
    
    def get_language_stats(self) -> dict:
        """
        Récupère les statistiques des langues
        
        Returns:
            Dictionnaire avec les statistiques
        """
        from apps.internationalization.models import Translation
        
        stats = {
            'total_languages': Language.objects.filter(is_active=True).count(),
            'default_language': self.get_default_language(),
            'languages_with_translations': {},
            'most_used_languages': [],
            'recent_languages': []
        }
        
        # Langues avec traductions
        for language in Language.objects.filter(is_active=True):
            translation_count = Translation.objects.filter(
                language=language,
                is_active=True
            ).count()
            
            if translation_count > 0:
                stats['languages_with_translations'][language.code] = {
                    'name': language.name,
                    'translation_count': translation_count
                }
        
        # Langues les plus utilisées
        most_used = Language.objects.filter(
            is_active=True,
            translation_count__gt=0
        ).order_by('-translation_count')[:10]
        
        stats['most_used_languages'] = [
            {
                'code': lang.code,
                'name': lang.name,
                'translation_count': lang.translation_count
            }
            for lang in most_used
        ]
        
        # Langues récemment utilisées
        recent = Language.objects.filter(
            is_active=True,
            last_used__isnull=False
        ).order_by('-last_used')[:5]
        
        stats['recent_languages'] = [
            {
                'code': lang.code,
                'name': lang.name,
                'last_used': lang.last_used
            }
            for lang in recent
        ]
        
        return stats
    
    def initialize_default_languages(self) -> List[Language]:
        """
        Initialise les langues par défaut du système
        
        Returns:
            Liste des langues créées
        """
        default_languages = [
            {
                'code': 'en',
                'name': 'English',
                'native_name': 'English',
                'flag_emoji': '🇺🇸',
                'country_code': 'US',
                'region': 'North America',
                'is_default': True
            },
            {
                'code': 'fr',
                'name': 'French',
                'native_name': 'Français',
                'flag_emoji': '🇫🇷',
                'country_code': 'FR',
                'region': 'Europe'
            },
            {
                'code': 'es',
                'name': 'Spanish',
                'native_name': 'Español',
                'flag_emoji': '🇪🇸',
                'country_code': 'ES',
                'region': 'Europe'
            },
            {
                'code': 'de',
                'name': 'German',
                'native_name': 'Deutsch',
                'flag_emoji': '🇩🇪',
                'country_code': 'DE',
                'region': 'Europe'
            },
            {
                'code': 'it',
                'name': 'Italian',
                'native_name': 'Italiano',
                'flag_emoji': '🇮🇹',
                'country_code': 'IT',
                'region': 'Europe'
            },
            {
                'code': 'pt',
                'name': 'Portuguese',
                'native_name': 'Português',
                'flag_emoji': '🇵🇹',
                'country_code': 'PT',
                'region': 'Europe'
            },
            {
                'code': 'ru',
                'name': 'Russian',
                'native_name': 'Русский',
                'flag_emoji': '🇷🇺',
                'country_code': 'RU',
                'region': 'Europe'
            },
            {
                'code': 'zh',
                'name': 'Chinese',
                'native_name': '中文',
                'flag_emoji': '🇨🇳',
                'country_code': 'CN',
                'region': 'Asia'
            },
            {
                'code': 'ja',
                'name': 'Japanese',
                'native_name': '日本語',
                'flag_emoji': '🇯🇵',
                'country_code': 'JP',
                'region': 'Asia'
            },
            {
                'code': 'ko',
                'name': 'Korean',
                'native_name': '한국어',
                'flag_emoji': '🇰🇷',
                'country_code': 'KR',
                'region': 'Asia'
            },
            {
                'code': 'ar',
                'name': 'Arabic',
                'native_name': 'العربية',
                'flag_emoji': '🇸🇦',
                'country_code': 'SA',
                'region': 'Middle East',
                'is_rtl': True
            }
        ]
        
        created_languages = []
        
        with transaction.atomic():
            for lang_data in default_languages:
                language, created = Language.objects.get_or_create(
                    code=lang_data['code'],
                    defaults=lang_data
                )
                
                if created:
                    created_languages.append(language)
        
        return created_languages

