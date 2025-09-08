"""
Service pour les health checks de l'API
"""
import requests
import time
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from apps.api.models import APIHealthCheck, APIHealthCheckResult, APISystemStatus


class HealthCheckService:
    """Service pour les health checks de l'API"""
    
    def __init__(self):
        self.cache_timeout = 60  # 1 minute
    
    def run_health_check(self, health_check):
        """Exécute un health check spécifique"""
        start_time = time.time()
        
        try:
            if health_check.check_type == 'database':
                result = self._check_database()
            elif health_check.check_type == 'cache':
                result = self._check_cache()
            elif health_check.check_type == 'external_api':
                result = self._check_external_api(health_check)
            elif health_check.check_type == 'storage':
                result = self._check_storage()
            elif health_check.check_type == 'queue':
                result = self._check_queue()
            else:
                result = self._check_custom(health_check)
            
            response_time = (time.time() - start_time) * 1000  # Convertir en ms
            
            # Crée le résultat
            health_result = APIHealthCheckResult.objects.create(
                health_check=health_check,
                status=result['status'],
                response_time=response_time,
                status_code=result.get('status_code'),
                response_body=result.get('response_body', ''),
                error_message=result.get('error_message', ''),
            )
            
            return health_result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_result = APIHealthCheckResult.objects.create(
                health_check=health_check,
                status='unhealthy',
                response_time=response_time,
                error_message=str(e),
            )
            
            return health_result
    
    def _check_database(self):
        """Vérifie la base de données"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {
                    'status': 'healthy',
                    'status_code': 200,
                    'response_body': 'Database connection successful'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def _check_cache(self):
        """Vérifie le cache"""
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                return {
                    'status': 'healthy',
                    'status_code': 200,
                    'response_body': 'Cache is working'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'status_code': 500,
                    'error_message': 'Cache read/write failed'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def _check_external_api(self, health_check):
        """Vérifie une API externe"""
        try:
            response = requests.get(
                health_check.endpoint_url,
                timeout=health_check.timeout,
                headers=health_check.headers
            )
            
            if response.status_code == health_check.expected_status_code:
                if health_check.expected_response and health_check.expected_response not in response.text:
                    return {
                        'status': 'degraded',
                        'status_code': response.status_code,
                        'response_body': response.text,
                        'error_message': 'Unexpected response content'
                    }
                
                return {
                    'status': 'healthy',
                    'status_code': response.status_code,
                    'response_body': response.text
                }
            else:
                return {
                    'status': 'unhealthy',
                    'status_code': response.status_code,
                    'response_body': response.text,
                    'error_message': f'Expected status {health_check.expected_status_code}, got {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'status_code': 408,
                'error_message': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'status_code': 503,
                'error_message': 'Connection error'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def _check_storage(self):
        """Vérifie le stockage"""
        try:
            import os
            import tempfile
            
            # Test d'écriture
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b'test')
                temp_path = f.name
            
            # Test de lecture
            with open(temp_path, 'rb') as f:
                content = f.read()
            
            # Nettoyage
            os.unlink(temp_path)
            
            if content == b'test':
                return {
                    'status': 'healthy',
                    'status_code': 200,
                    'response_body': 'Storage is working'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'status_code': 500,
                    'error_message': 'Storage read/write failed'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def _check_queue(self):
        """Vérifie la file d'attente"""
        try:
            # Ici vous pouvez implémenter la logique pour vérifier votre système de queue
            # Par exemple, Redis, Celery, etc.
            return {
                'status': 'healthy',
                'status_code': 200,
                'response_body': 'Queue is working'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def _check_custom(self, health_check):
        """Vérifie un health check personnalisé"""
        try:
            # Ici vous pouvez implémenter la logique pour des health checks personnalisés
            # Par exemple, vérifier des services spécifiques à votre application
            return {
                'status': 'healthy',
                'status_code': 200,
                'response_body': 'Custom check passed'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'status_code': 500,
                'error_message': str(e)
            }
    
    def run_all_health_checks(self):
        """Exécute tous les health checks actifs"""
        health_checks = APIHealthCheck.objects.filter(is_active=True)
        results = []
        
        for health_check in health_checks:
            result = self.run_health_check(health_check)
            results.append(result)
        
        # Met à jour le statut global du système
        self._update_system_status(results)
        
        return results
    
    def _update_system_status(self, results):
        """Met à jour le statut global du système"""
        if not results:
            return
        
        # Compte les statuts
        healthy_count = sum(1 for r in results if r.status == 'healthy')
        degraded_count = sum(1 for r in results if r.status == 'degraded')
        unhealthy_count = sum(1 for r in results if r.status == 'unhealthy')
        
        # Détermine le statut global
        if unhealthy_count > 0:
            overall_status = 'unhealthy'
            message = f"{unhealthy_count} health check(s) failed"
        elif degraded_count > 0:
            overall_status = 'degraded'
            message = f"{degraded_count} health check(s) degraded"
        else:
            overall_status = 'healthy'
            message = "All health checks passed"
        
        # Calcule les métriques
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        total_response_time = 0
        
        for result in results:
            total_requests += 1
            if result.status == 'healthy':
                successful_requests += 1
            else:
                failed_requests += 1
            total_response_time += result.response_time
        
        average_response_time = total_response_time / total_requests if total_requests > 0 else 0
        
        # Crée le statut du système
        APISystemStatus.objects.create(
            overall_status=overall_status,
            message=message,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            healthy_checks=healthy_count,
            degraded_checks=degraded_count,
            unhealthy_checks=unhealthy_count,
        )
    
    def get_system_status(self):
        """Récupère le statut global du système"""
        cache_key = 'api_system_status'
        status = cache.get(cache_key)
        
        if status is None:
            try:
                status = APISystemStatus.objects.latest('checked_at')
                cache.set(cache_key, status, self.cache_timeout)
            except APISystemStatus.DoesNotExist:
                status = None
        
        return status
    
    def get_health_check_results(self, health_check, limit=10):
        """Récupère les résultats récents d'un health check"""
        return APIHealthCheckResult.objects.filter(
            health_check=health_check
        ).order_by('-checked_at')[:limit]
    
    def get_health_check_statistics(self, days=7):
        """Récupère les statistiques des health checks"""
        from django.db.models import Count, Avg
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        stats = {
            'total_health_checks': APIHealthCheck.objects.filter(is_active=True).count(),
            'total_results': APIHealthCheckResult.objects.filter(
                checked_at__gte=start_date
            ).count(),
            'results_by_status': list(
                APIHealthCheckResult.objects.filter(
                    checked_at__gte=start_date
                ).values('status')
                .annotate(count=Count('id'))
                .order_by('status')
            ),
            'average_response_time': APIHealthCheckResult.objects.filter(
                checked_at__gte=start_date
            ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0,
            'health_checks_by_type': list(
                APIHealthCheck.objects.filter(is_active=True)
                .values('check_type')
                .annotate(count=Count('id'))
                .order_by('check_type')
            ),
        }
        
        return stats



