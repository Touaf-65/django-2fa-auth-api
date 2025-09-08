"""
Service de logging structuré
"""
import logging
import json
from django.utils import timezone
from django.core.cache import cache
from apps.monitoring.models import LogEntry


class LoggingService:
    """Service pour la gestion des logs structurés"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def log(self, level, message, source='system', user=None, **kwargs):
        """Enregistre un log structuré"""
        
        # Extraction des métadonnées
        metadata = kwargs.get('metadata', {})
        tags = kwargs.get('tags', [])
        
        # Contexte de la requête
        request = kwargs.get('request')
        if request:
            metadata.update({
                'method': getattr(request, 'method', ''),
                'path': getattr(request, 'path', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
            })
            
            # Session et requête ID
            session_id = getattr(request, 'session', {}).get('session_key', '')
            request_id = getattr(request, 'id', '')
        else:
            session_id = kwargs.get('session_id', '')
            request_id = kwargs.get('request_id', '')
        
        # Contexte de l'application
        app_name = kwargs.get('app_name', '')
        module_name = kwargs.get('module_name', '')
        function_name = kwargs.get('function_name', '')
        line_number = kwargs.get('line_number')
        
        # Exception/Erreur
        exception_type = kwargs.get('exception_type', '')
        exception_message = kwargs.get('exception_message', '')
        stack_trace = kwargs.get('stack_trace', '')
        
        # Performance
        response_time = kwargs.get('response_time')
        status_code = kwargs.get('status_code')
        
        # Création de l'entrée de log
        log_entry = LogEntry.objects.create(
            level=level,
            source=source,
            message=message,
            user=user,
            session_id=session_id,
            request_id=request_id,
            ip_address=metadata.get('ip_address'),
            user_agent=metadata.get('user_agent', ''),
            metadata=metadata,
            tags=tags,
            app_name=app_name,
            module_name=module_name,
            function_name=function_name,
            line_number=line_number,
            method=metadata.get('method', ''),
            path=metadata.get('path', ''),
            status_code=status_code,
            response_time=response_time,
            exception_type=exception_type,
            exception_message=exception_message,
            stack_trace=stack_trace,
        )
        
        # Invalide le cache des statistiques
        self._invalidate_log_cache()
        
        return log_entry
    
    def debug(self, message, **kwargs):
        """Log de niveau DEBUG"""
        return self.log('DEBUG', message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log de niveau INFO"""
        return self.log('INFO', message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log de niveau WARNING"""
        return self.log('WARNING', message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log de niveau ERROR"""
        return self.log('ERROR', message, **kwargs)
    
    def critical(self, message, **kwargs):
        """Log de niveau CRITICAL"""
        return self.log('CRITICAL', message, **kwargs)
    
    def log_exception(self, exception, message=None, **kwargs):
        """Log d'une exception"""
        import traceback
        
        if message is None:
            message = str(exception)
        
        kwargs.update({
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'stack_trace': traceback.format_exc(),
        })
        
        return self.error(message, **kwargs)
    
    def get_logs(self, level=None, source=None, user=None, hours=24, limit=100):
        """Récupère les logs avec filtres"""
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        queryset = LogEntry.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        
        if level:
            queryset = queryset.filter(level=level)
        if source:
            queryset = queryset.filter(source=source)
        if user:
            queryset = queryset.filter(user=user)
        
        return queryset.order_by('-created_at')[:limit]
    
    def get_log_statistics(self, hours=24):
        """Récupère les statistiques des logs"""
        cache_key = f'log_statistics_{hours}'
        stats = cache.get(cache_key)
        
        if stats is None:
            from datetime import timedelta
            from django.db.models import Count
            
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            queryset = LogEntry.objects.filter(
                created_at__gte=start_time,
                created_at__lte=end_time
            )
            
            stats = {
                'total_logs': queryset.count(),
                'logs_by_level': list(
                    queryset.values('level')
                    .annotate(count=Count('id'))
                    .order_by('level')
                ),
                'logs_by_source': list(
                    queryset.values('source')
                    .annotate(count=Count('id'))
                    .order_by('source')
                ),
                'error_logs': queryset.filter(level__in=['ERROR', 'CRITICAL']).count(),
                'warning_logs': queryset.filter(level='WARNING').count(),
                'info_logs': queryset.filter(level='INFO').count(),
                'debug_logs': queryset.filter(level='DEBUG').count(),
                'logs_by_hour': list(
                    queryset.extra(
                        select={'hour': 'EXTRACT(hour FROM created_at)'}
                    ).values('hour')
                    .annotate(count=Count('id'))
                    .order_by('hour')
                ),
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def search_logs(self, query, level=None, source=None, hours=24, limit=100):
        """Recherche dans les logs"""
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        queryset = LogEntry.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time
        )
        
        # Recherche textuelle
        if query:
            queryset = queryset.filter(
                models.Q(message__icontains=query) |
                models.Q(exception_message__icontains=query) |
                models.Q(metadata__icontains=query)
            )
        
        if level:
            queryset = queryset.filter(level=level)
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset.order_by('-created_at')[:limit]
    
    def _get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _invalidate_log_cache(self):
        """Invalide le cache des logs"""
        # Ici vous pouvez implémenter une logique pour invalider les caches spécifiques
        pass


class StructuredLogger:
    """Logger structuré pour Django"""
    
    def __init__(self, name):
        self.name = name
        self.logging_service = LoggingService()
    
    def debug(self, message, **kwargs):
        """Log de niveau DEBUG"""
        return self.logging_service.debug(
            message,
            app_name=self.name,
            **kwargs
        )
    
    def info(self, message, **kwargs):
        """Log de niveau INFO"""
        return self.logging_service.info(
            message,
            app_name=self.name,
            **kwargs
        )
    
    def warning(self, message, **kwargs):
        """Log de niveau WARNING"""
        return self.logging_service.warning(
            message,
            app_name=self.name,
            **kwargs
        )
    
    def error(self, message, **kwargs):
        """Log de niveau ERROR"""
        return self.logging_service.error(
            message,
            app_name=self.name,
            **kwargs
        )
    
    def critical(self, message, **kwargs):
        """Log de niveau CRITICAL"""
        return self.logging_service.critical(
            message,
            app_name=self.name,
            **kwargs
        )
    
    def exception(self, message, **kwargs):
        """Log d'exception"""
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        kwargs.update({
            'exception_type': exc_type.__name__ if exc_type else '',
            'exception_message': str(exc_value) if exc_value else '',
            'stack_trace': self._format_traceback(exc_traceback) if exc_traceback else '',
        })
        
        return self.error(message, **kwargs)
    
    def _format_traceback(self, traceback):
        """Formate la traceback"""
        import traceback
        return ''.join(traceback.format_tb(traceback))

