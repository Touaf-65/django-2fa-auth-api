"""
URLs pour l'app Internationalization
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LanguageViewSet, LanguagePreferenceViewSet, LanguageStatsView,
    TranslationKeyViewSet, TranslationViewSet, TranslationRequestViewSet,
    TranslationStatsView, AutoTranslateView,
    ContentViewSet, ContentTranslationViewSet, ContentSearchView
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet)
router.register(r'language-preferences', LanguagePreferenceViewSet)
router.register(r'translation-keys', TranslationKeyViewSet)
router.register(r'translations', TranslationViewSet)
router.register(r'translation-requests', TranslationRequestViewSet)
router.register(r'content', ContentViewSet)
router.register(r'content-translations', ContentTranslationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Vues spéciales
    path('language-stats/', LanguageStatsView.as_view({'get': 'stats'}), name='language-stats'),
    path('language-usage/', LanguageStatsView.as_view({'get': 'usage'}), name='language-usage'),
    path('translation-stats/', TranslationStatsView.as_view({'get': 'stats'}), name='translation-stats'),
    path('auto-translate/', AutoTranslateView.as_view({'post': 'create'}), name='auto-translate'),
    path('content-search/', ContentSearchView.as_view({'get': 'list'}), name='content-search'),
]
