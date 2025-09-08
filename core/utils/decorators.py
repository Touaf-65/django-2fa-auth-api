"""
Décorateurs utilitaires pour Django
"""
import time
import functools
import logging
from typing import Any, Callable, Optional, Dict, List
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


def cache_result(timeout: int = 300, key_prefix: str = None):
    """
    Décorateur pour mettre en cache le résultat d'une fonction
    
    Args:
        timeout: Durée du cache en secondes
        key_prefix: Préfixe pour la clé de cache
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Génère une clé de cache unique
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Vérifie le cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Exécute la fonction et met en cache le résultat
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window: int = 3600, key_func: Callable = None):
    """
    Décorateur pour limiter le taux de requêtes
    
    Args:
        max_requests: Nombre maximum de requêtes
        window: Fenêtre de temps en secondes
        key_func: Fonction pour générer la clé de rate limiting
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Génère une clé de rate limiting
            if key_func:
                key = key_func(request)
            else:
                key = f"rate_limit:{request.META.get('REMOTE_ADDR', 'unknown')}"
            
            # Vérifie le nombre de requêtes
            current_requests = cache.get(key, 0)
            if current_requests >= max_requests:
                return JsonResponse(
                    {'error': 'Rate limit exceeded'}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Incrémente le compteur
            cache.set(key, current_requests + 1, window)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Décorateur pour réessayer une fonction en cas d'échec
    
    Args:
        max_retries: Nombre maximum de tentatives
        delay: Délai initial entre les tentatives
        backoff: Facteur de backoff exponentiel
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Tentative {attempt + 1} échouée pour {func.__name__}: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"Toutes les tentatives ont échoué pour {func.__name__}: {e}")
            
            raise last_exception
        
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    Décorateur pour logger le temps d'exécution d'une fonction
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"{func.__name__} exécutée en {execution_time:.2f} secondes")
        return result
    
    return wrapper


def require_permissions(permissions: List[str]):
    """
    Décorateur pour vérifier les permissions
    
    Args:
        permissions: Liste des permissions requises
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            for permission in permissions:
                if not request.user.has_perm(permission):
                    return JsonResponse(
                        {'error': f'Permission required: {permission}'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_authentication(func: Callable) -> Callable:
    """
    Décorateur pour vérifier l'authentification
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return func(request, *args, **kwargs)
    
    return wrapper


def validate_request_data(required_fields: List[str] = None, optional_fields: List[str] = None):
    """
    Décorateur pour valider les données de requête
    
    Args:
        required_fields: Champs requis
        optional_fields: Champs optionnels
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.data if hasattr(request, 'data') else request.POST
                
                # Vérifie les champs requis
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return JsonResponse(
                            {'error': f'Champs requis manquants: {", ".join(missing_fields)}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Vérifie les champs autorisés
                if optional_fields:
                    allowed_fields = set(required_fields or []) | set(optional_fields)
                    invalid_fields = [field for field in data.keys() if field not in allowed_fields]
                    if invalid_fields:
                        return JsonResponse(
                            {'error': f'Champs non autorisés: {", ".join(invalid_fields)}'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def handle_exceptions(exceptions: Dict[type, str] = None):
    """
    Décorateur pour gérer les exceptions
    
    Args:
        exceptions: Dictionnaire des exceptions et leurs messages
    """
    if exceptions is None:
        exceptions = {
            ValueError: 'Valeur invalide',
            TypeError: 'Type invalide',
            KeyError: 'Clé manquante',
            PermissionDenied: 'Permission refusée',
        }
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                for exception_type, message in exceptions.items():
                    if isinstance(e, exception_type):
                        logger.error(f"Exception dans {func.__name__}: {e}")
                        return JsonResponse(
                            {'error': message}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Exception non gérée
                logger.error(f"Exception non gérée dans {func.__name__}: {e}")
                return JsonResponse(
                    {'error': 'Erreur interne du serveur'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return wrapper
    return decorator


def async_operation(func: Callable) -> Callable:
    """
    Décorateur pour exécuter une fonction de manière asynchrone
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    
    return wrapper


def background_task(func: Callable) -> Callable:
    """
    Décorateur pour exécuter une tâche en arrière-plan
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()
    
    return wrapper


def cache_page_with_vary(timeout: int = 300, vary_headers: List[str] = None):
    """
    Décorateur pour mettre en cache une page avec des en-têtes variables
    
    Args:
        timeout: Durée du cache en secondes
        vary_headers: En-têtes à prendre en compte pour la variation
    """
    if vary_headers is None:
        vary_headers = ['Accept-Language', 'User-Agent']
    
    def decorator(func: Callable) -> Callable:
        @cache_page(timeout)
        @vary_on_headers(*vary_headers)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def method_decorator_list(decorators: List[Callable]):
    """
    Applique une liste de décorateurs à une méthode de classe
    """
    def decorator(func: Callable) -> Callable:
        for decorator_func in reversed(decorators):
            func = decorator_func(func)
        return func
    return decorator


def conditional_decorator(condition: Callable, decorator_func: Callable):
    """
    Applique un décorateur conditionnellement
    
    Args:
        condition: Fonction qui détermine si le décorateur doit être appliqué
        decorator_func: Décorateur à appliquer
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return decorator_func(func)(*args, **kwargs)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timeout_decorator(timeout_seconds: int = 30):
    """
    Décorateur pour ajouter un timeout à une fonction
    
    Args:
        timeout_seconds: Timeout en secondes
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Fonction {func.__name__} a dépassé le timeout de {timeout_seconds} secondes")
            
            # Configure le signal d'alarme
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restaure le signal
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def memoize(maxsize: int = 128):
    """
    Décorateur pour mémoriser les résultats d'une fonction
    
    Args:
        maxsize: Taille maximale du cache
    """
    def decorator(func: Callable) -> Callable:
        cache_dict = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Crée une clé de cache
            key = str(args) + str(kwargs)
            
            if key in cache_dict:
                return cache_dict[key]
            
            result = func(*args, **kwargs)
            
            # Limite la taille du cache
            if len(cache_dict) >= maxsize:
                # Supprime le premier élément (FIFO)
                first_key = next(iter(cache_dict))
                del cache_dict[first_key]
            
            cache_dict[key] = result
            return result
        
        return wrapper
    return decorator


def singleton(cls):
    """
    Décorateur pour implémenter le pattern Singleton
    """
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


def deprecated(reason: str = "Cette fonction est dépréciée"):
    """
    Décorateur pour marquer une fonction comme dépréciée
    
    Args:
        reason: Raison de la dépréciation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(f"{func.__name__} est dépréciée: {reason}", DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

