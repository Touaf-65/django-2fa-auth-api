"""
Service principal de gestion des traductions
"""
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.internationalization.models import (
    Language, Translation, TranslationKey, TranslationRequest
)
from .auto_translation_service import AutoTranslationService

User = get_user_model()


class TranslationService:
    """
    Service principal pour la gestion des traductions
    """
    
    def __init__(self):
        self.auto_translation_service = AutoTranslationService()
    
    def create_translation_key(self, key: str, source_text: str, 
                              source_language: Language, context: str = 'ui',
                              description: str = '', tags: List[str] = None,
                              created_by: User = None) -> TranslationKey:
        """
        Crée une nouvelle clé de traduction
        
        Args:
            key: Clé unique de traduction
            source_text: Texte source
            source_language: Langue source
            context: Contexte de la traduction
            description: Description optionnelle
            tags: Tags optionnels
            created_by: Utilisateur créateur
        
        Returns:
            TranslationKey créée
        """
        translation_key, created = TranslationKey.objects.get_or_create(
            key=key,
            defaults={
                'source_text': source_text,
                'source_language': source_language,
                'context': context,
                'description': description,
                'tags': tags or [],
                'created_by': created_by
            }
        )
        
        if not created:
            # Mettre à jour si la clé existe déjà
            translation_key.source_text = source_text
            translation_key.context = context
            translation_key.description = description
            translation_key.tags = tags or []
            translation_key.save()
        
        return translation_key
    
    def translate_key(self, translation_key: TranslationKey, target_language: Language,
                     translated_by: User = None, use_auto_translation: bool = True,
                     provider: str = None) -> Translation:
        """
        Traduit une clé de traduction vers une langue cible
        
        Args:
            translation_key: Clé à traduire
            target_language: Langue cible
            translated_by: Utilisateur traducteur
            use_auto_translation: Utiliser la traduction automatique
            provider: Fournisseur de traduction automatique
        
        Returns:
            Translation créée ou mise à jour
        """
        # Vérifier si la traduction existe déjà
        translation, created = Translation.objects.get_or_create(
            translation_key=translation_key,
            language=target_language,
            defaults={
                'translated_text': '',
                'status': 'pending',
                'translated_by': translated_by
            }
        )
        
        if use_auto_translation and target_language.auto_translate_enabled:
            # Effectuer la traduction automatique
            result = self.auto_translation_service.translate_text(
                text=translation_key.source_text,
                source_lang=translation_key.source_language.code,
                target_lang=target_language.code,
                provider=provider,
                context=translation_key.context
            )
            
            if result['success']:
                translation.translated_text = result['translated_text']
                translation.status = 'auto_translated'
                translation.confidence_score = result.get('confidence', 0.8)
                translation.translation_service = result.get('provider', 'unknown')
                translation.translated_at = timezone.now()
                
                # Évaluer la qualité si possible
                if result.get('confidence', 0) < 0.7:
                    quality_score = self.auto_translation_service.get_translation_quality(
                        translation_key.source_text,
                        result['translated_text'],
                        translation_key.source_language.code,
                        target_language.code
                    )
                    translation.confidence_score = quality_score
            else:
                translation.status = 'pending'
                translation.notes = f"Erreur de traduction automatique: {result.get('error', 'Inconnue')}"
        
        if translated_by:
            translation.translated_by = translated_by
            if not use_auto_translation:
                translation.status = 'human_translated'
                translation.translated_at = timezone.now()
        
        translation.save()
        return translation
    
    def create_translation_request(self, source_text: str, source_language: Language,
                                  target_languages: List[Language], requested_by: User,
                                  context: str = 'ui', priority: str = 'medium',
                                  use_auto_translation: bool = True,
                                  require_human_review: bool = False) -> TranslationRequest:
        """
        Crée une demande de traduction
        
        Args:
            source_text: Texte à traduire
            source_language: Langue source
            target_languages: Langues cibles
            requested_by: Utilisateur demandeur
            context: Contexte de la traduction
            priority: Priorité de la demande
            use_auto_translation: Utiliser la traduction automatique
            require_human_review: Exiger une révision humaine
        
        Returns:
            TranslationRequest créée
        """
        request = TranslationRequest.objects.create(
            source_text=source_text,
            source_language=source_language,
            context=context,
            priority=priority,
            requested_by=requested_by,
            use_auto_translation=use_auto_translation,
            require_human_review=require_human_review
        )
        
        request.target_languages.set(target_languages)
        
        # Traiter la demande si la traduction automatique est activée
        if use_auto_translation:
            self.process_translation_request(request)
        
        return request
    
    def process_translation_request(self, request: TranslationRequest) -> None:
        """
        Traite une demande de traduction
        
        Args:
            request: Demande de traduction à traiter
        """
        request.status = 'processing'
        request.started_at = timezone.now()
        request.save()
        
        try:
            with transaction.atomic():
                # Créer la clé de traduction
                translation_key = self.create_translation_key(
                    key=f"request_{request.id}",
                    source_text=request.source_text,
                    source_language=request.source_language,
                    context=request.context,
                    created_by=request.requested_by
                )
                
                # Traduire vers chaque langue cible
                for target_language in request.target_languages.all():
                    translation = self.translate_key(
                        translation_key=translation_key,
                        target_language=target_language,
                        translated_by=request.requested_by,
                        use_auto_translation=request.use_auto_translation,
                        provider=request.translation_service
                    )
                    
                    request.completed_translations.add(translation)
                
                request.status = 'completed'
                request.completed_at = timezone.now()
                request.save()
                
        except Exception as e:
            request.status = 'failed'
            request.error_message = str(e)
            request.save()
    
    def get_translation(self, key: str, language: Language) -> Optional[str]:
        """
        Récupère une traduction pour une clé et une langue
        
        Args:
            key: Clé de traduction
            language: Langue cible
        
        Returns:
            Texte traduit ou None
        """
        try:
            translation_key = TranslationKey.objects.get(key=key)
            translation = Translation.objects.get(
                translation_key=translation_key,
                language=language,
                is_active=True
            )
            
            # Mettre à jour les statistiques
            translation_key.usage_count += 1
            translation_key.last_used = timezone.now()
            translation_key.save()
            
            return translation.translated_text
            
        except (TranslationKey.DoesNotExist, Translation.DoesNotExist):
            return None
    
    def get_translations_for_language(self, language: Language, 
                                    context: str = None) -> Dict[str, str]:
        """
        Récupère toutes les traductions pour une langue
        
        Args:
            language: Langue cible
            context: Contexte optionnel
        
        Returns:
            Dictionnaire {clé: traduction}
        """
        queryset = Translation.objects.filter(
            language=language,
            is_active=True,
            status__in=['auto_translated', 'human_translated', 'reviewed', 'approved']
        ).select_related('translation_key')
        
        if context:
            queryset = queryset.filter(translation_key__context=context)
        
        translations = {}
        for translation in queryset:
            translations[translation.translation_key.key] = translation.translated_text
        
        return translations
    
    def update_translation(self, translation: Translation, new_text: str,
                          updated_by: User, status: str = 'human_translated') -> Translation:
        """
        Met à jour une traduction existante
        
        Args:
            translation: Traduction à mettre à jour
            new_text: Nouveau texte traduit
            updated_by: Utilisateur mettant à jour
            status: Nouveau statut
        
        Returns:
            Translation mise à jour
        """
        translation.translated_text = new_text
        translation.status = status
        translation.translated_by = updated_by
        translation.translated_at = timezone.now()
        translation.save()
        
        return translation
    
    def review_translation(self, translation: Translation, approved: bool,
                          reviewed_by: User, notes: str = '') -> Translation:
        """
        Révision d'une traduction
        
        Args:
            translation: Traduction à réviser
            approved: Approuvée ou rejetée
            reviewed_by: Utilisateur révisant
            notes: Notes de révision
        
        Returns:
            Translation révisée
        """
        translation.status = 'approved' if approved else 'rejected'
        translation.reviewed_by = reviewed_by
        translation.reviewed_at = timezone.now()
        translation.notes = notes
        translation.save()
        
        return translation
    
    def get_translation_stats(self, language: Language = None) -> Dict:
        """
        Récupère les statistiques de traduction
        
        Args:
            language: Langue spécifique (optionnel)
        
        Returns:
            Dictionnaire avec les statistiques
        """
        base_queryset = Translation.objects.filter(is_active=True)
        
        if language:
            base_queryset = base_queryset.filter(language=language)
        
        stats = {
            'total_translations': base_queryset.count(),
            'auto_translated': base_queryset.filter(status='auto_translated').count(),
            'human_translated': base_queryset.filter(status='human_translated').count(),
            'reviewed': base_queryset.filter(status='reviewed').count(),
            'approved': base_queryset.filter(status='approved').count(),
            'pending': base_queryset.filter(status='pending').count(),
            'rejected': base_queryset.filter(status='rejected').count(),
        }
        
        # Calculer le pourcentage de traduction automatique
        if stats['total_translations'] > 0:
            stats['auto_translation_percentage'] = (
                stats['auto_translated'] / stats['total_translations'] * 100
            )
        else:
            stats['auto_translation_percentage'] = 0
        
        return stats

