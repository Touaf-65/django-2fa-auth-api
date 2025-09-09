"""
Middleware de détection et gestion des langues
"""
from django.utils.deprecation import MiddlewareMixin
from django.utils import translation
from django.conf import settings

from apps.internationalization.services import LanguageService


class LanguageMiddleware(MiddlewareMixin):
    """
    Middleware pour la détection automatique de la langue
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.language_service = LanguageService()
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Traite la requête pour détecter la langue
        """
        # Détecter la langue préférée
        detected_language = self.language_service.detect_user_language(request)
        
        # Définir la langue dans la requête
        request.language = detected_language
        request.language_code = detected_language.code
        
        # Activer la langue dans Django
        translation.activate(detected_language.code)
        
        # Sauvegarder en session pour les requêtes suivantes
        if hasattr(request, 'session'):
            request.session['language'] = detected_language.code
        
        # Mettre à jour les statistiques d'utilisation
        self.language_service.update_language_usage(detected_language)
        
        return None
    
    def process_response(self, request, response):
        """
        Traite la réponse pour ajouter des en-têtes de langue
        """
        # Ajouter l'en-tête Content-Language
        if hasattr(request, 'language_code'):
            response['Content-Language'] = request.language_code
        
        # Ajouter l'en-tête Vary pour le cache
        if 'Vary' in response:
            if 'Accept-Language' not in response['Vary']:
                response['Vary'] += ', Accept-Language'
        else:
            response['Vary'] = 'Accept-Language'
        
        return response
    
    def process_exception(self, request, exception):
        """
        Traite les exceptions en conservant la langue
        """
        # Réactiver la langue en cas d'exception
        if hasattr(request, 'language_code'):
            translation.activate(request.language_code)
        
        return None

