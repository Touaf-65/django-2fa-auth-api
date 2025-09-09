"""
Service de traduction automatique avec plusieurs fournisseurs
"""
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from apps.internationalization.models import Language, Translation, TranslationKey


class AutoTranslationService:
    """
    Service de traduction automatique avec support de plusieurs fournisseurs
    """
    
    def __init__(self):
        self.providers = {
            'google': GoogleTranslateProvider(),
            'microsoft': MicrosoftTranslateProvider(),
            'deepl': DeepLTranslateProvider(),
            'openai': OpenAITranslateProvider(),
            'mock': MockTranslateProvider(),  # Pour les tests
        }
        self.default_provider = getattr(settings, 'DEFAULT_TRANSLATION_PROVIDER', 'mock')
    
    def translate_text(self, text: str, source_lang: str, target_lang: str, 
                      provider: str = None, context: str = None) -> Dict:
        """
        Traduit un texte en utilisant le fournisseur spécifié
        
        Args:
            text: Texte à traduire
            source_lang: Code de la langue source
            target_lang: Code de la langue cible
            provider: Fournisseur à utiliser (optionnel)
            context: Contexte de la traduction (optionnel)
        
        Returns:
            Dict avec les résultats de la traduction
        """
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Fournisseur '{provider}' non supporté")
        
        # Vérifier le cache
        cache_key = f"translation:{provider}:{source_lang}:{target_lang}:{hash(text)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Effectuer la traduction
            result = self.providers[provider].translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                context=context
            )
            
            # Mettre en cache le résultat
            cache.set(cache_key, result, timeout=3600)  # 1 heure
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': provider,
                'text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
    
    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str,
                       provider: str = None) -> List[Dict]:
        """
        Traduit plusieurs textes en lot
        
        Args:
            texts: Liste des textes à traduire
            source_lang: Code de la langue source
            target_lang: Code de la langue cible
            provider: Fournisseur à utiliser (optionnel)
        
        Returns:
            Liste des résultats de traduction
        """
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Fournisseur '{provider}' non supporté")
        
        try:
            return self.providers[provider].translate_batch(
                texts=texts,
                source_lang=source_lang,
                target_lang=target_lang
            )
        except Exception as e:
            return [{
                'success': False,
                'error': str(e),
                'provider': provider,
                'text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            } for text in texts]
    
    def get_supported_languages(self, provider: str = None) -> List[str]:
        """
        Retourne les langues supportées par le fournisseur
        
        Args:
            provider: Fournisseur à interroger (optionnel)
        
        Returns:
            Liste des codes de langues supportées
        """
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Fournisseur '{provider}' non supporté")
        
        return self.providers[provider].get_supported_languages()
    
    def get_translation_quality(self, text: str, translation: str, 
                               source_lang: str, target_lang: str) -> float:
        """
        Évalue la qualité d'une traduction
        
        Args:
            text: Texte original
            translation: Traduction
            source_lang: Langue source
            target_lang: Langue cible
        
        Returns:
            Score de qualité (0-1)
        """
        # Utiliser OpenAI pour l'évaluation de qualité si disponible
        if 'openai' in self.providers:
            try:
                return self.providers['openai'].evaluate_quality(
                    text, translation, source_lang, target_lang
                )
            except:
                pass
        
        # Fallback vers une évaluation simple
        return self._simple_quality_evaluation(text, translation)
    
    def _simple_quality_evaluation(self, text: str, translation: str) -> float:
        """
        Évaluation simple de la qualité basée sur la longueur et les caractères
        """
        if not text or not translation:
            return 0.0
        
        # Ratio de longueur
        length_ratio = len(translation) / len(text)
        length_score = 1.0 - abs(1.0 - length_ratio) * 0.3
        
        # Présence de caractères spéciaux
        special_chars = sum(1 for c in translation if not c.isalnum() and c not in ' .,!?')
        special_score = 1.0 - (special_chars / len(translation)) * 0.2
        
        return min(1.0, max(0.0, (length_score + special_score) / 2))


class BaseTranslationProvider:
    """Classe de base pour les fournisseurs de traduction"""
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        """Traduit un texte"""
        raise NotImplementedError
    
    def translate_batch(self, texts: List[str], source_lang: str, 
                       target_lang: str) -> List[Dict]:
        """Traduit plusieurs textes"""
        results = []
        for text in texts:
            results.append(self.translate(text, source_lang, target_lang))
        return results
    
    def get_supported_languages(self) -> List[str]:
        """Retourne les langues supportées"""
        raise NotImplementedError


class GoogleTranslateProvider(BaseTranslationProvider):
    """Fournisseur Google Translate"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_TRANSLATE_API_KEY', None)
        self.base_url = 'https://translation.googleapis.com/language/translate/v2'
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        if not self.api_key:
            raise ValueError("Clé API Google Translate non configurée")
        
        params = {
            'key': self.api_key,
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        if context:
            params['context'] = context
        
        try:
            response = requests.post(self.base_url, data=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            translated_text = data['data']['translations'][0]['translatedText']
            
            return {
                'success': True,
                'translated_text': translated_text,
                'provider': 'google',
                'confidence': 0.9,  # Google ne fournit pas de score de confiance
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'google'
            }
    
    def get_supported_languages(self) -> List[str]:
        return ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi']


class MicrosoftTranslateProvider(BaseTranslationProvider):
    """Fournisseur Microsoft Translator"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'MICROSOFT_TRANSLATE_API_KEY', None)
        self.base_url = 'https://api.cognitive.microsofttranslator.com/translate'
        self.region = getattr(settings, 'MICROSOFT_TRANSLATE_REGION', 'global')
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        if not self.api_key:
            raise ValueError("Clé API Microsoft Translator non configurée")
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-Type': 'application/json'
        }
        
        params = {
            'api-version': '3.0',
            'from': source_lang,
            'to': target_lang
        }
        
        body = [{'text': text}]
        
        try:
            response = requests.post(
                f"{self.base_url}?{requests.compat.urlencode(params)}",
                headers=headers,
                json=body,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            translated_text = data[0]['translations'][0]['text']
            
            return {
                'success': True,
                'translated_text': translated_text,
                'provider': 'microsoft',
                'confidence': 0.85,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'microsoft'
            }
    
    def get_supported_languages(self) -> List[str]:
        return ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi']


class DeepLTranslateProvider(BaseTranslationProvider):
    """Fournisseur DeepL"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPL_API_KEY', None)
        self.base_url = 'https://api-free.deepl.com/v2/translate'
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        if not self.api_key:
            raise ValueError("Clé API DeepL non configurée")
        
        headers = {
            'Authorization': f'DeepL-Auth-Key {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'text': text,
            'source_lang': source_lang.upper(),
            'target_lang': target_lang.upper()
        }
        
        if context:
            data['context'] = context
        
        try:
            response = requests.post(self.base_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result['translations'][0]['text']
            
            return {
                'success': True,
                'translated_text': translated_text,
                'provider': 'deepl',
                'confidence': 0.95,  # DeepL est généralement très précis
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'deepl'
            }
    
    def get_supported_languages(self) -> List[str]:
        return ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']


class OpenAITranslateProvider(BaseTranslationProvider):
    """Fournisseur OpenAI GPT pour traduction et évaluation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.base_url = 'https://api.openai.com/v1/chat/completions'
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        if not self.api_key:
            raise ValueError("Clé API OpenAI non configurée")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"Traduis le texte suivant du {source_lang} vers le {target_lang}: {text}"
        if context:
            prompt += f" (Contexte: {context})"
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'Tu es un traducteur professionnel. Réponds uniquement avec la traduction.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1000,
            'temperature': 0.3
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result['choices'][0]['message']['content'].strip()
            
            return {
                'success': True,
                'translated_text': translated_text,
                'provider': 'openai',
                'confidence': 0.9,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'openai'
            }
    
    def evaluate_quality(self, text: str, translation: str, 
                        source_lang: str, target_lang: str) -> float:
        """Évalue la qualité d'une traduction"""
        if not self.api_key:
            return 0.5  # Score par défaut
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""
        Évalue la qualité de cette traduction du {source_lang} vers le {target_lang}:
        
        Texte original: {text}
        Traduction: {translation}
        
        Donne un score de 0 à 1 (1 = parfait). Réponds uniquement avec le nombre.
        """
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 10,
            'temperature': 0.1
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            score_text = result['choices'][0]['message']['content'].strip()
            
            # Extraire le score numérique
            import re
            score_match = re.search(r'0\.\d+|1\.0|0|1', score_text)
            if score_match:
                return float(score_match.group())
            
            return 0.5
            
        except Exception as e:
            return 0.5
    
    def get_supported_languages(self) -> List[str]:
        return ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi']


class MockTranslateProvider(BaseTranslationProvider):
    """Fournisseur de test pour les développements"""
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                  context: str = None) -> Dict:
        # Simulation d'une traduction
        translated_text = f"[{target_lang.upper()}] {text}"
        
        return {
            'success': True,
            'translated_text': translated_text,
            'provider': 'mock',
            'confidence': 0.8,
            'source_lang': source_lang,
            'target_lang': target_lang
        }
    
    def get_supported_languages(self) -> List[str]:
        return ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']

