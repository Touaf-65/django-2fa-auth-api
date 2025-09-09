"""
Vues API pour la gestion du contenu multilingue
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.internationalization.models import Content, ContentTranslation
from apps.internationalization.serializers import (
    ContentSerializer, ContentTranslationSerializer, ContentSearchSerializer
)
from apps.internationalization.services import ContentService


class ContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion du contenu multilingue
    """
    queryset = Content.objects.filter(is_active=True)
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['content_type', 'is_active', 'is_public', 'source_language']
    search_fields = ['title', 'description', 'identifier']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions requises pour cette action
        """
        if self.action in ['list', 'retrieve', 'get_in_language']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Crée un contenu pour l'utilisateur connecté
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def get_in_language(self, request, pk=None):
        """
        Récupère un contenu dans une langue spécifique
        """
        content = self.get_object()
        language_code = request.query_params.get('language')
        
        if not language_code:
            return Response(
                {'error': 'Paramètre "language" requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.internationalization.models import Language
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return Response(
                {'error': f'Langue "{language_code}" non trouvée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_service = ContentService()
        content_data = content_service.get_content_in_language(content, language)
        
        return Response(content_data)
    
    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        """
        Traduit un contenu vers une langue spécifique
        """
        content = self.get_object()
        language_code = request.data.get('language')
        translated_title = request.data.get('translated_title', '')
        translated_description = request.data.get('translated_description', '')
        translated_content = request.data.get('translated_content', '')
        use_auto_translation = request.data.get('use_auto_translation', True)
        
        if not language_code:
            return Response(
                {'error': 'Langue cible requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.internationalization.models import Language
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return Response(
                {'error': f'Langue "{language_code}" non trouvée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_service = ContentService()
        translation = content_service.translate_content(
            content=content,
            target_language=language,
            translated_title=translated_title,
            translated_description=translated_description,
            translated_content=translated_content,
            translated_by=request.user,
            use_auto_translation=use_auto_translation
        )
        
        serializer = ContentTranslationSerializer(translation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Récupère les statistiques de contenu
        """
        content_type = request.query_params.get('content_type')
        
        content_service = ContentService()
        stats = content_service.get_content_stats(content_type)
        
        return Response(stats)


class ContentTranslationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des traductions de contenu
    """
    queryset = ContentTranslation.objects.filter(is_active=True)
    serializer_class = ContentTranslationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'is_active', 'language', 'content']
    search_fields = ['translated_title', 'translated_description', 'translated_content']
    ordering_fields = ['translated_at', 'reviewed_at', 'published_at', 'created_at']
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
        Révision d'une traduction de contenu
        """
        translation = self.get_object()
        approved = request.data.get('approved', True)
        notes = request.data.get('notes', '')
        
        content_service = ContentService()
        translation = content_service.review_content_translation(
            translation=translation,
            approved=approved,
            reviewed_by=request.user,
            notes=notes
        )
        
        serializer = self.get_serializer(translation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publie une traduction de contenu
        """
        translation = self.get_object()
        
        if translation.status not in ['approved', 'human_translated']:
            return Response(
                {'error': 'La traduction doit être approuvée avant publication'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content_service = ContentService()
        translation = content_service.publish_content_translation(
            translation=translation,
            published_by=request.user
        )
        
        serializer = self.get_serializer(translation)
        return Response(serializer.data)


class ContentSearchView(viewsets.ViewSet):
    """
    Vue pour la recherche de contenu multilingue
    """
    queryset = Content.objects.none()  # ViewSet sans modèle
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Recherche du contenu multilingue
        """
        query = request.query_params.get('q')
        language_code = request.query_params.get('language')
        content_type = request.query_params.get('content_type')
        limit = int(request.query_params.get('limit', 20))
        
        if not query:
            return Response(
                {'error': 'Paramètre de recherche "q" requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        language = None
        if language_code:
            from apps.internationalization.models import Language
            try:
                language = Language.objects.get(code=language_code)
            except Language.DoesNotExist:
                return Response(
                    {'error': f'Langue "{language_code}" non trouvée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        content_service = ContentService()
        results = content_service.search_content(
            query=query,
            language=language,
            content_type=content_type,
            limit=limit
        )
        
        serializer = ContentSearchSerializer(results, many=True)
        return Response({
            'query': query,
            'results': serializer.data,
            'total': len(results)
        })
