"""
Vues API pour la gestion des langues
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.internationalization.models import Language, LanguagePreference
from apps.internationalization.serializers import (
    LanguageSerializer, LanguagePreferenceSerializer, LanguageStatsSerializer
)
from apps.internationalization.services import LanguageService


class LanguageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des langues
    """
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['code', 'is_default', 'is_rtl', 'region']
    search_fields = ['name', 'native_name', 'code']
    ordering_fields = ['name', 'native_name', 'translation_count', 'last_used']
    ordering = ['name']
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions requises pour cette action
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """
        Récupère la langue par défaut
        """
        language_service = LanguageService()
        default_language = language_service.get_default_language()
        
        if default_language:
            serializer = self.get_serializer(default_language)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Aucune langue par défaut trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def initialize_defaults(self, request):
        """
        Initialise les langues par défaut du système
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permissions insuffisantes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        language_service = LanguageService()
        created_languages = language_service.initialize_default_languages()
        
        serializer = self.get_serializer(created_languages, many=True)
        return Response({
            'message': f'{len(created_languages)} langues créées',
            'languages': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Définit une langue comme langue par défaut
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permissions insuffisantes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        language = self.get_object()
        language.is_default = True
        language.save()
        
        serializer = self.get_serializer(language)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Active/désactive une langue
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permissions insuffisantes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        language = self.get_object()
        language.is_active = not language.is_active
        language.save()
        
        serializer = self.get_serializer(language)
        return Response(serializer.data)


class LanguagePreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des préférences de langue des utilisateurs
    """
    queryset = LanguagePreference.objects.all()
    serializer_class = LanguagePreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Retourne les préférences de l'utilisateur connecté
        """
        return LanguagePreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Crée une préférence pour l'utilisateur connecté
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """
        Récupère les préférences de l'utilisateur connecté
        """
        try:
            preference = LanguagePreference.objects.get(user=request.user)
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        except LanguagePreference.DoesNotExist:
            return Response(
                {'error': 'Aucune préférence trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def set_preferences(self, request):
        """
        Définit les préférences de langue de l'utilisateur
        """
        language_service = LanguageService()
        
        primary_language_code = request.data.get('primary_language')
        secondary_languages = request.data.get('secondary_languages', [])
        
        try:
            primary_language = Language.objects.get(code=primary_language_code)
        except Language.DoesNotExist:
            return Response(
                {'error': f'Langue primaire "{primary_language_code}" non trouvée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        secondary_language_objects = []
        for lang_code in secondary_languages:
            try:
                lang = Language.objects.get(code=lang_code)
                secondary_language_objects.append(lang)
            except Language.DoesNotExist:
                return Response(
                    {'error': f'Langue secondaire "{lang_code}" non trouvée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        preference = language_service.set_user_language_preference(
            user=request.user,
            primary_language=primary_language,
            secondary_languages=secondary_language_objects,
            auto_detect=request.data.get('auto_detect_language', True),
            auto_translate=request.data.get('auto_translate_enabled', True)
        )
        
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def detect_language(self, request):
        """
        Détecte la langue préférée de l'utilisateur
        """
        language_service = LanguageService()
        detected_language = language_service.detect_user_language(request)
        
        serializer = LanguageSerializer(detected_language)
        return Response({
            'detected_language': serializer.data,
            'message': 'Langue détectée avec succès'
        })


class LanguageStatsView(viewsets.ViewSet):
    """
    Vue pour les statistiques des langues
    """
    queryset = Language.objects.none()  # ViewSet sans modèle
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Récupère les statistiques des langues
        """
        language_service = LanguageService()
        stats = language_service.get_language_stats()
        
        serializer = LanguageStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """
        Récupère les statistiques d'utilisation des langues
        """
        from apps.internationalization.models import Translation
        
        # Langues les plus utilisées
        most_used = Language.objects.filter(
            is_active=True,
            translation_count__gt=0
        ).order_by('-translation_count')[:10]
        
        # Langues récemment utilisées
        recent = Language.objects.filter(
            is_active=True,
            last_used__isnull=False
        ).order_by('-last_used')[:5]
        
        # Statistiques par langue
        language_stats = []
        for language in Language.objects.filter(is_active=True):
            translation_count = Translation.objects.filter(
                language=language,
                is_active=True
            ).count()
            
            language_stats.append({
                'language': LanguageSerializer(language).data,
                'translation_count': translation_count,
                'last_used': language.last_used
            })
        
        return Response({
            'most_used_languages': LanguageSerializer(most_used, many=True).data,
            'recent_languages': LanguageSerializer(recent, many=True).data,
            'language_stats': language_stats,
            'total_languages': Language.objects.filter(is_active=True).count()
        })
