"""
Vues API pour la gestion des traductions
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.internationalization.models import TranslationKey, Translation, TranslationRequest
from apps.internationalization.serializers import (
    TranslationKeySerializer, TranslationSerializer, TranslationRequestSerializer,
    TranslationStatsSerializer
)
from apps.internationalization.services import TranslationService


class TranslationKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clés de traduction
    """
    queryset = TranslationKey.objects.filter(is_active=True)
    serializer_class = TranslationKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['context', 'is_active', 'priority', 'source_language']
    search_fields = ['key', 'source_text', 'description']
    ordering_fields = ['key', 'usage_count', 'last_used', 'created_at']
    ordering = ['key']
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions requises pour cette action
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        """
        Traduit une clé vers une langue spécifique
        """
        translation_key = self.get_object()
        target_language_code = request.data.get('target_language')
        use_auto_translation = request.data.get('use_auto_translation', True)
        provider = request.data.get('provider')
        
        if not target_language_code:
            return Response(
                {'error': 'Langue cible requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.internationalization.models import Language
        try:
            target_language = Language.objects.get(code=target_language_code)
        except Language.DoesNotExist:
            return Response(
                {'error': f'Langue "{target_language_code}" non trouvée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translation_service = TranslationService()
        translation = translation_service.translate_key(
            translation_key=translation_key,
            target_language=target_language,
            translated_by=request.user,
            use_auto_translation=use_auto_translation,
            provider=provider
        )
        
        serializer = TranslationSerializer(translation)
        return Response(serializer.data)


class TranslationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des traductions
    """
    queryset = Translation.objects.filter(is_active=True)
    serializer_class = TranslationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'is_active', 'language', 'translation_key']
    search_fields = ['translated_text', 'notes']
    ordering_fields = ['translated_at', 'reviewed_at', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions requises pour cette action
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Révision d'une traduction
        """
        translation = self.get_object()
        approved = request.data.get('approved', True)
        notes = request.data.get('notes', '')
        
        translation_service = TranslationService()
        translation = translation_service.review_translation(
            translation=translation,
            approved=approved,
            reviewed_by=request.user,
            notes=notes
        )
        
        serializer = self.get_serializer(translation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_text(self, request, pk=None):
        """
        Met à jour le texte d'une traduction
        """
        translation = self.get_object()
        new_text = request.data.get('translated_text')
        status_value = request.data.get('status', 'human_translated')
        
        if not new_text:
            return Response(
                {'error': 'Texte traduit requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translation_service = TranslationService()
        translation = translation_service.update_translation(
            translation=translation,
            new_text=new_text,
            updated_by=request.user,
            status=status_value
        )
        
        serializer = self.get_serializer(translation)
        return Response(serializer.data)


class TranslationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des demandes de traduction
    """
    queryset = TranslationRequest.objects.all()
    serializer_class = TranslationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'priority', 'context', 'requested_by']
    search_fields = ['source_text']
    ordering_fields = ['created_at', 'completed_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Retourne les demandes de l'utilisateur connecté ou toutes si admin
        """
        if self.request.user.is_staff:
            return TranslationRequest.objects.all()
        return TranslationRequest.objects.filter(requested_by=self.request.user)
    
    def perform_create(self, serializer):
        """
        Crée une demande pour l'utilisateur connecté
        """
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Traite une demande de traduction
        """
        translation_request = self.get_object()
        
        if translation_request.status != 'pending':
            return Response(
                {'error': 'La demande a déjà été traitée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translation_service = TranslationService()
        translation_service.process_translation_request(translation_request)
        
        serializer = self.get_serializer(translation_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """
        Récupère les demandes de l'utilisateur connecté
        """
        requests = TranslationRequest.objects.filter(requested_by=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)


class TranslationStatsView(viewsets.ViewSet):
    """
    Vue pour les statistiques de traduction
    """
    queryset = Translation.objects.none()  # ViewSet sans modèle
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Récupère les statistiques de traduction
        """
        from apps.internationalization.models import Language
        
        language_code = request.query_params.get('language')
        language = None
        
        if language_code:
            try:
                language = Language.objects.get(code=language_code)
            except Language.DoesNotExist:
                return Response(
                    {'error': f'Langue "{language_code}" non trouvée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        translation_service = TranslationService()
        stats = translation_service.get_translation_stats(language)
        
        serializer = TranslationStatsSerializer(stats)
        return Response(serializer.data)


class AutoTranslateView(viewsets.ViewSet):
    """
    Vue pour la traduction automatique
    """
    queryset = Translation.objects.none()  # ViewSet sans modèle
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        """
        Effectue une traduction automatique
        """
        text = request.data.get('text')
        source_lang = request.data.get('source_language')
        target_lang = request.data.get('target_language')
        provider = request.data.get('provider')
        context = request.data.get('context')
        
        if not all([text, source_lang, target_lang]):
            return Response(
                {'error': 'Texte, langue source et langue cible requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.internationalization.services import AutoTranslationService
        auto_service = AutoTranslationService()
        
        result = auto_service.translate_text(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            provider=provider,
            context=context
        )
        
        return Response(result)
