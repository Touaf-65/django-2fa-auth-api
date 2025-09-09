"""
Service de gestion du contenu multilingue
"""
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.internationalization.models import (
    Language, Content, ContentTranslation
)
from .translation_service import TranslationService

User = get_user_model()


class ContentService:
    """
    Service de gestion du contenu multilingue
    """
    
    def __init__(self):
        self.translation_service = TranslationService()
    
    def create_content(self, content_type: str, identifier: str, title: str,
                      description: str = '', source_language: Language = None,
                      created_by: User = None, tags: List[str] = None,
                      content_object=None) -> Content:
        """
        Crée un nouveau contenu multilingue
        
        Args:
            content_type: Type de contenu
            identifier: Identifiant unique
            title: Titre du contenu
            description: Description du contenu
            source_language: Langue source
            created_by: Utilisateur créateur
            tags: Tags optionnels
            content_object: Objet lié (optionnel)
        
        Returns:
            Content créé
        """
        if source_language is None:
            from .language_service import LanguageService
            language_service = LanguageService()
            source_language = language_service.get_default_language()
        
        content = Content.objects.create(
            content_type=content_type,
            identifier=identifier,
            title=title,
            description=description,
            source_language=source_language,
            created_by=created_by,
            tags=tags or []
        )
        
        # Lier l'objet si fourni
        if content_object:
            content.content_object_type = ContentType.objects.get_for_model(content_object)
            content.content_object_id = content_object.id
            content.save()
        
        return content
    
    def translate_content(self, content: Content, target_language: Language,
                         translated_title: str, translated_description: str = '',
                         translated_content: str = '', translated_by: User = None,
                         use_auto_translation: bool = True) -> ContentTranslation:
        """
        Traduit un contenu vers une langue cible
        
        Args:
            content: Contenu à traduire
            target_language: Langue cible
            translated_title: Titre traduit
            translated_description: Description traduite
            translated_content: Contenu traduit
            translated_by: Utilisateur traducteur
            use_auto_translation: Utiliser la traduction automatique
        
        Returns:
            ContentTranslation créée ou mise à jour
        """
        # Vérifier si la traduction existe déjà
        translation, created = ContentTranslation.objects.get_or_create(
            content=content,
            language=target_language,
            defaults={
                'translated_title': '',
                'translated_description': '',
                'translated_content': '',
                'status': 'draft',
                'translated_by': translated_by
            }
        )
        
        if use_auto_translation and target_language.auto_translate_enabled:
            # Traduction automatique du titre si non fourni
            if not translated_title:
                title_result = self.translation_service.auto_translation_service.translate_text(
                    text=content.title,
                    source_lang=content.source_language.code,
                    target_lang=target_language.code,
                    context='content'
                )
                if title_result['success']:
                    translated_title = title_result['translated_text']
            
            # Traduction automatique de la description si non fournie
            if not translated_description and content.description:
                desc_result = self.translation_service.auto_translation_service.translate_text(
                    text=content.description,
                    source_lang=content.source_language.code,
                    target_lang=target_language.code,
                    context='content'
                )
                if desc_result['success']:
                    translated_description = desc_result['translated_text']
            
            # Traduction automatique du contenu si non fourni
            if not translated_content and hasattr(content, 'content') and content.content:
                content_result = self.translation_service.auto_translation_service.translate_text(
                    text=content.content,
                    source_lang=content.source_language.code,
                    target_lang=target_language.code,
                    context='content'
                )
                if content_result['success']:
                    translated_content = content_result['translated_text']
        
        # Mettre à jour la traduction
        translation.translated_title = translated_title
        translation.translated_description = translated_description
        translation.translated_content = translated_content
        translation.translated_by = translated_by
        translation.translated_at = timezone.now()
        
        if use_auto_translation:
            translation.status = 'auto_translated'
        else:
            translation.status = 'human_translated'
        
        translation.save()
        return translation
    
    def get_content_translation(self, content: Content, language: Language) -> Optional[ContentTranslation]:
        """
        Récupère la traduction d'un contenu pour une langue
        
        Args:
            content: Contenu
            language: Langue cible
        
        Returns:
            ContentTranslation ou None
        """
        try:
            return ContentTranslation.objects.get(
                content=content,
                language=language,
                is_active=True
            )
        except ContentTranslation.DoesNotExist:
            return None
    
    def get_content_in_language(self, content: Content, language: Language) -> Dict:
        """
        Récupère un contenu dans une langue spécifique
        
        Args:
            content: Contenu
            language: Langue cible
        
        Returns:
            Dictionnaire avec le contenu traduit
        """
        # Si c'est la langue source, retourner le contenu original
        if content.source_language == language:
            return {
                'title': content.title,
                'description': content.description,
                'content': getattr(content, 'content', ''),
                'language': language.code,
                'is_original': True
            }
        
        # Chercher la traduction
        translation = self.get_content_translation(content, language)
        
        if translation:
            return {
                'title': translation.translated_title,
                'description': translation.translated_description,
                'content': translation.translated_content,
                'language': language.code,
                'is_original': False,
                'status': translation.status,
                'translated_at': translation.translated_at
            }
        
        # Fallback vers la langue source
        return {
            'title': content.title,
            'description': content.description,
            'content': getattr(content, 'content', ''),
            'language': content.source_language.code,
            'is_original': True,
            'fallback': True
        }
    
    def publish_content_translation(self, translation: ContentTranslation,
                                  published_by: User) -> ContentTranslation:
        """
        Publie une traduction de contenu
        
        Args:
            translation: Traduction à publier
            published_by: Utilisateur publiant
        
        Returns:
            ContentTranslation publiée
        """
        translation.status = 'published'
        translation.published_at = timezone.now()
        translation.reviewed_by = published_by
        translation.save()
        
        return translation
    
    def review_content_translation(self, translation: ContentTranslation,
                                 approved: bool, reviewed_by: User,
                                 notes: str = '') -> ContentTranslation:
        """
        Révision d'une traduction de contenu
        
        Args:
            translation: Traduction à réviser
            approved: Approuvée ou rejetée
            reviewed_by: Utilisateur révisant
            notes: Notes de révision
        
        Returns:
            ContentTranslation révisée
        """
        translation.status = 'approved' if approved else 'rejected'
        translation.reviewed_by = reviewed_by
        translation.reviewed_at = timezone.now()
        translation.notes = notes
        translation.save()
        
        return translation
    
    def get_content_stats(self, content_type: str = None) -> Dict:
        """
        Récupère les statistiques de contenu
        
        Args:
            content_type: Type de contenu spécifique (optionnel)
        
        Returns:
            Dictionnaire avec les statistiques
        """
        base_queryset = Content.objects.filter(is_active=True)
        
        if content_type:
            base_queryset = base_queryset.filter(content_type=content_type)
        
        stats = {
            'total_content': base_queryset.count(),
            'content_by_type': {},
            'translations_by_status': {},
            'languages_covered': set(),
            'recent_content': []
        }
        
        # Contenu par type
        for content in base_queryset:
            content_type = content.content_type
            if content_type not in stats['content_by_type']:
                stats['content_by_type'][content_type] = 0
            stats['content_by_type'][content_type] += 1
        
        # Traductions par statut
        translations = ContentTranslation.objects.filter(
            content__in=base_queryset,
            is_active=True
        )
        
        for translation in translations:
            status = translation.status
            if status not in stats['translations_by_status']:
                stats['translations_by_status'][status] = 0
            stats['translations_by_status'][status] += 1
            
            stats['languages_covered'].add(translation.language.code)
        
        # Contenu récent
        recent_content = base_queryset.order_by('-created_at')[:10]
        stats['recent_content'] = [
            {
                'id': content.id,
                'title': content.title,
                'content_type': content.content_type,
                'created_at': content.created_at,
                'available_languages': len(content.get_available_languages())
            }
            for content in recent_content
        ]
        
        stats['languages_covered'] = list(stats['languages_covered'])
        
        return stats
    
    def search_content(self, query: str, language: Language = None,
                      content_type: str = None, limit: int = 20) -> List[Dict]:
        """
        Recherche du contenu multilingue
        
        Args:
            query: Terme de recherche
            language: Langue de recherche
            content_type: Type de contenu
            limit: Limite de résultats
        
        Returns:
            Liste des résultats de recherche
        """
        from django.db.models import Q
        
        # Construire la requête de base
        base_query = Q(is_active=True)
        
        if content_type:
            base_query &= Q(content_type=content_type)
        
        # Recherche dans le contenu source
        source_query = base_query & (
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        
        results = []
        
        # Rechercher dans le contenu source
        for content in Content.objects.filter(source_query)[:limit]:
            result = {
                'content': content,
                'match_type': 'source',
                'language': content.source_language.code,
                'title': content.title,
                'description': content.description
            }
            results.append(result)
        
        # Rechercher dans les traductions si une langue est spécifiée
        if language:
            translation_query = Q(
                content__is_active=True,
                language=language,
                is_active=True
            ) & (
                Q(translated_title__icontains=query) |
                Q(translated_description__icontains=query) |
                Q(translated_content__icontains=query)
            )
            
            if content_type:
                translation_query &= Q(content__content_type=content_type)
            
            for translation in ContentTranslation.objects.filter(translation_query)[:limit]:
                result = {
                    'content': translation.content,
                    'match_type': 'translation',
                    'language': language.code,
                    'title': translation.translated_title,
                    'description': translation.translated_description,
                    'translation': translation
                }
                results.append(result)
        
        # Trier par pertinence (titre d'abord, puis description)
        results.sort(key=lambda x: (
            query.lower() in x['title'].lower(),
            query.lower() in x['description'].lower()
        ), reverse=True)
        
        return results[:limit]

