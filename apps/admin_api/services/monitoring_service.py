"""
Service de monitoring système
"""
import psutil
import time
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from django.conf import settings


class MonitoringService:
    """Service de monitoring système"""
    
    def __init__(self):
        self.cache_timeout = 60  # 1 minute
    
    def get_system_health_score(self):
        """Calcule un score de santé global du système (0-100)"""
        try:
            # Vérifie la base de données
            db_score = self.get_database_health_score()
            
            # Vérifie le cache
            cache_score = self.get_cache_health_score()
            
            # Vérifie l'espace disque
            disk_score = self.get_disk_health_score()
            
            # Vérifie la mémoire
            memory_score = self.get_memory_health_score()
            
            # Vérifie le CPU
            cpu_score = self.get_cpu_health_score()
            
            # Calcule la moyenne pondérée
            total_score = (
                db_score * 0.3 +
                cache_score * 0.2 +
                disk_score * 0.2 +
                memory_score * 0.15 +
                cpu_score * 0.15
            )
            
            return round(total_score, 2)
            
        except Exception as e:
            print(f"Erreur lors du calcul du score de santé: {e}")
            return 0
    
    def get_database_health_score(self):
        """Score de santé de la base de données (0-100)"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return 100
        except Exception:
            return 0
    
    def get_cache_health_score(self):
        """Score de santé du cache (0-100)"""
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                return 100
            else:
                return 0
        except Exception:
            return 0
    
    def get_disk_health_score(self):
        """Score de santé du disque (0-100)"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = disk_usage.percent
            
            if usage_percent < 70:
                return 100
            elif usage_percent < 80:
                return 80
            elif usage_percent < 90:
                return 60
            elif usage_percent < 95:
                return 40
            else:
                return 20
                
        except Exception:
            return 0
    
    def get_memory_health_score(self):
        """Score de santé de la mémoire (0-100)"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent < 70:
                return 100
            elif usage_percent < 80:
                return 80
            elif usage_percent < 90:
                return 60
            elif usage_percent < 95:
                return 40
            else:
                return 20
                
        except Exception:
            return 0
    
    def get_cpu_health_score(self):
        """Score de santé du CPU (0-100)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent < 70:
                return 100
            elif cpu_percent < 80:
                return 80
            elif cpu_percent < 90:
                return 60
            elif cpu_percent < 95:
                return 40
            else:
                return 20
                
        except Exception:
            return 0
    
    def get_api_response_time(self):
        """Temps de réponse moyen de l'API (ms)"""
        # Ici vous pouvez implémenter la logique pour mesurer le temps de réponse
        # Par exemple, en utilisant des middlewares ou des logs
        return 100  # Valeur par défaut
    
    def get_error_rate(self):
        """Taux d'erreur (0-100)"""
        try:
            from apps.admin_api.models import AdminLog
            from datetime import timedelta
            
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            
            total_logs = AdminLog.objects.filter(created_at__gte=last_hour).count()
            error_logs = AdminLog.objects.filter(
                created_at__gte=last_hour,
                level__in=['error', 'critical']
            ).count()
            
            if total_logs == 0:
                return 0
            
            error_rate = (error_logs / total_logs) * 100
            return round(error_rate, 2)
            
        except Exception:
            return 0
    
    def get_active_users_count(self):
        """Nombre d'utilisateurs actifs (dernière heure)"""
        try:
            from django.contrib.auth import get_user_model
            from datetime import timedelta
            
            User = get_user_model()
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            
            active_users = User.objects.filter(
                last_login__gte=last_hour,
                is_active=True
            ).count()
            
            return active_users
            
        except Exception:
            return 0
    
    def get_security_events_count(self):
        """Nombre d'événements de sécurité (dernière heure)"""
        try:
            from apps.security.models import SecurityEvent
            from datetime import timedelta
            
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            
            security_events = SecurityEvent.objects.filter(
                created_at__gte=last_hour
            ).count()
            
            return security_events
            
        except Exception:
            return 0
    
    def get_system_metrics(self):
        """Récupère toutes les métriques système"""
        return {
            'timestamp': timezone.now().isoformat(),
            'health_score': self.get_system_health_score(),
            'database_score': self.get_database_health_score(),
            'cache_score': self.get_cache_health_score(),
            'disk_score': self.get_disk_health_score(),
            'memory_score': self.get_memory_health_score(),
            'cpu_score': self.get_cpu_health_score(),
            'api_response_time': self.get_api_response_time(),
            'error_rate': self.get_error_rate(),
            'active_users': self.get_active_users_count(),
            'security_events': self.get_security_events_count(),
            'system_info': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            }
        }
    
    def get_cached_metrics(self):
        """Récupère les métriques depuis le cache ou les calcule"""
        cache_key = 'system_metrics'
        metrics = cache.get(cache_key)
        
        if metrics is None:
            metrics = self.get_system_metrics()
            cache.set(cache_key, metrics, self.cache_timeout)
        
        return metrics



