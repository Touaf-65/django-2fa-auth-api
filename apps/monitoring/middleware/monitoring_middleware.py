"""
Middleware de monitoring pour collecter automatiquement les métriques
"""
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache

from apps.monitoring.services import LoggingService, MetricsService, PerformanceService


class MonitoringMiddleware(MiddlewareMixin):
    """Middleware pour le monitoring automatique des requêtes"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logging_service = LoggingService()
        self.metrics_service = MetricsService()
        self.performance_service = PerformanceService()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Traite la requête entrante"""
        # Générer un ID unique pour la requête
        request.id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Enregistrer le début de la requête
        user = getattr(request, 'user', None)
        # Ne pas logger si l'utilisateur est AnonymousUser
        if user and user.is_authenticated:
            self.logging_service.info(
                f"Request started: {request.method} {request.path}",
                source='api',
                user=user,
                request=request,
                metadata={
                    'request_id': request.id,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'content_type': request.META.get('CONTENT_TYPE', ''),
                    'content_length': request.META.get('CONTENT_LENGTH', 0),
                }
            )
        
        # Incrémenter le compteur de requêtes (seulement pour les requêtes API)
        if request.path.startswith('/api/') and not request.path.startswith('/api/monitoring/'):
            try:
                self.metrics_service.increment_counter(
                    'api_requests_total',
                    labels={
                        'method': request.method,
                        'endpoint': self._get_endpoint_name(request.path),
                    },
                    request=request,
                )
            except Exception:
                # Ignorer les erreurs de métriques pour éviter les boucles
                pass
    
    def process_response(self, request, response):
        """Traite la réponse sortante"""
        if hasattr(request, 'start_time'):
            # Calculer le temps de réponse
            response_time = time.time() - request.start_time
            
            # Enregistrer le temps de réponse (seulement pour les requêtes API)
            if request.path.startswith('/api/') and not request.path.startswith('/api/monitoring/'):
                user = getattr(request, 'user', None)
                if user and user.is_authenticated:
                    try:
                        self.performance_service.record_response_time(
                            endpoint=request.path,
                            method=request.method,
                            response_time=response_time,
                            status_code=response.status_code,
                            user=user,
                            request=request,
                        )
                    except Exception:
                        # Ignorer les erreurs de métriques pour éviter les boucles
                        pass
            
            # Enregistrer les métriques (seulement pour les requêtes API)
            if request.path.startswith('/api/') and not request.path.startswith('/api/monitoring/'):
                try:
                    self.metrics_service.record_metric(
                        'api_response_time',
                        value=response_time,
                        labels={
                            'method': request.method,
                            'endpoint': self._get_endpoint_name(request.path),
                            'status_code': str(response.status_code),
                        },
                        request=request,
                    )
                except Exception:
                    # Ignorer les erreurs de métriques pour éviter les boucles
                    pass
            
            # Incrémenter le compteur de réponses (seulement pour les requêtes API)
            if request.path.startswith('/api/') and not request.path.startswith('/api/monitoring/'):
                try:
                    self.metrics_service.increment_counter(
                        'api_responses_total',
                        labels={
                            'method': request.method,
                            'endpoint': self._get_endpoint_name(request.path),
                            'status_code': str(response.status_code),
                        },
                        request=request,
                    )
                except Exception:
                    # Ignorer les erreurs de métriques pour éviter les boucles
                    pass
            
            # Enregistrer le taux d'erreur (seulement pour les requêtes API)
            if request.path.startswith('/api/') and not request.path.startswith('/api/monitoring/'):
                error_count = 1 if response.status_code >= 400 else 0
                user = getattr(request, 'user', None)
                if user and user.is_authenticated:
                    try:
                        self.performance_service.record_error_rate(
                            endpoint=request.path,
                            method=request.method,
                            error_count=error_count,
                            total_count=1,
                            user=user,
                            request=request,
                        )
                    except Exception:
                        # Ignorer les erreurs de métriques pour éviter les boucles
                        pass
            
            # Log de la réponse
            log_level = 'ERROR' if response.status_code >= 400 else 'INFO'
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                self.logging_service.log(
                    level=log_level,
                    message=f"Request completed: {request.method} {request.path} - {response.status_code}",
                    source='api',
                    user=user,
                    request=request,
                    metadata={
                        'request_id': getattr(request, 'id', ''),
                        'response_time': response_time,
                        'status_code': response.status_code,
                        'content_length': len(response.content) if hasattr(response, 'content') else 0,
                    }
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Traite les exceptions"""
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            
            # Log de l'exception
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                self.logging_service.log_exception(
                    exception=exception,
                    message=f"Request failed: {request.method} {request.path}",
                    source='api',
                    user=user,
                    request=request,
                    metadata={
                        'request_id': getattr(request, 'id', ''),
                        'response_time': response_time,
                    }
                )
            
            # Enregistrer les métriques d'erreur
            self.metrics_service.increment_counter(
                'api_exceptions_total',
                labels={
                    'method': request.method,
                    'endpoint': self._get_endpoint_name(request.path),
                    'exception_type': type(exception).__name__,
                },
                request=request,
            )
            
            # Enregistrer le temps de réponse pour les exceptions
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                self.performance_service.record_response_time(
                    endpoint=request.path,
                    method=request.method,
                    response_time=response_time,
                    status_code=500,
                    user=user,
                    request=request,
                )
    
    def _get_endpoint_name(self, path):
        """Extrait le nom de l'endpoint à partir du chemin"""
        # Simplifier le chemin pour les métriques
        if path.startswith('/api/'):
            # Extraire la partie après /api/
            endpoint = path[5:]  # Enlever '/api/'
            
            # Remplacer les IDs numériques par {id}
            import re
            endpoint = re.sub(r'/\d+/', '/{id}/', endpoint)
            endpoint = re.sub(r'/\d+$', '/{id}', endpoint)
            
            # Remplacer les UUIDs par {uuid}
            endpoint = re.sub(r'/[0-9a-f-]{36}/', '/{uuid}/', endpoint)
            endpoint = re.sub(r'/[0-9a-f-]{36}$', '/{uuid}', endpoint)
            
            return endpoint
        
        return path


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware spécialisé pour le monitoring des performances"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.performance_service = PerformanceService()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Démarre le monitoring de performance"""
        request.performance_start_time = time.time()
        request.performance_metrics = {}
    
    def process_response(self, request, response):
        """Finalise le monitoring de performance"""
        if hasattr(request, 'performance_start_time'):
            total_time = time.time() - request.performance_start_time
            
            # Enregistrer le temps total de traitement
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                self.performance_service.record_metric(
                    'request_processing_time',
                    value=total_time,
                    labels={
                        'method': request.method,
                        'endpoint': self._get_endpoint_name(request.path),
                        'status_code': str(response.status_code),
                    },
                    user=user,
                    request=request,
                )
            
            # Enregistrer la taille de la réponse
            if hasattr(response, 'content'):
                response_size = len(response.content)
                user = getattr(request, 'user', None)
                if user and user.is_authenticated:
                    self.performance_service.record_metric(
                        'response_size_bytes',
                        value=response_size,
                        labels={
                            'method': request.method,
                            'endpoint': self._get_endpoint_name(request.path),
                        },
                        user=user,
                        request=request,
                    )
        
        return response
    
    def _get_endpoint_name(self, path):
        """Extrait le nom de l'endpoint à partir du chemin"""
        if path.startswith('/api/'):
            endpoint = path[5:]
            import re
            endpoint = re.sub(r'/\d+/', '/{id}/', endpoint)
            endpoint = re.sub(r'/\d+$', '/{id}', endpoint)
            return endpoint
        return path


class DatabaseMonitoringMiddleware(MiddlewareMixin):
    """Middleware pour le monitoring des requêtes de base de données"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.metrics_service = MetricsService()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Initialise le monitoring de la base de données"""
        from django.db import connection
        request.db_queries_start = len(connection.queries)
        request.db_queries_time_start = sum(
            float(query['time']) for query in connection.queries
        )
    
    def process_response(self, request, response):
        """Finalise le monitoring de la base de données"""
        if hasattr(request, 'db_queries_start'):
            from django.db import connection
            
            # Calculer les métriques de base de données
            db_queries_count = len(connection.queries) - request.db_queries_start
            db_queries_time = sum(
                float(query['time']) for query in connection.queries
            ) - request.db_queries_time_start
            
            # Enregistrer les métriques
            if db_queries_count > 0:
                user = getattr(request, 'user', None)
                if user and user.is_authenticated:
                    self.metrics_service.record_metric(
                        'db_queries_count',
                        value=db_queries_count,
                        labels={
                            'method': request.method,
                            'endpoint': self._get_endpoint_name(request.path),
                        },
                        user=user,
                        request=request,
                    )
                
                user = getattr(request, 'user', None)
                if user and user.is_authenticated:
                    self.metrics_service.record_metric(
                        'db_queries_time',
                        value=db_queries_time,
                        labels={
                            'method': request.method,
                            'endpoint': self._get_endpoint_name(request.path),
                        },
                        user=user,
                        request=request,
                    )
        
        return response
    
    def _get_endpoint_name(self, path):
        """Extrait le nom de l'endpoint à partir du chemin"""
        if path.startswith('/api/'):
            endpoint = path[5:]
            import re
            endpoint = re.sub(r'/\d+/', '/{id}/', endpoint)
            endpoint = re.sub(r'/\d+$', '/{id}', endpoint)
            return endpoint
        return path


