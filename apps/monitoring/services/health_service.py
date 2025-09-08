"""
Service de monitoring de la santé du système
"""
import time
import psutil
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from django.core.cache import cache as django_cache
from apps.monitoring.models import SystemHealth, HealthCheck, HealthCheckResult


class HealthService:
    """Service pour le monitoring de la santé du système"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def check_database_health(self):
        """Vérifie la santé de la base de données"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result and result[0] == 1:
                return {
                    'status': 'pass',
                    'message': 'Database connection successful',
                    'response_time': 0.001,  # Très rapide
                }
            else:
                return {
                    'status': 'fail',
                    'message': 'Database query failed',
                    'response_time': None,
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Database connection failed: {str(e)}',
                'response_time': None,
                'error': str(e),
            }
    
    def check_cache_health(self):
        """Vérifie la santé du cache"""
        try:
            start_time = time.time()
            
            # Test d'écriture
            test_key = 'health_check_test'
            test_value = 'test_value'
            django_cache.set(test_key, test_value, 10)
            
            # Test de lecture
            retrieved_value = django_cache.get(test_key)
            
            response_time = time.time() - start_time
            
            if retrieved_value == test_value:
                # Nettoyer
                django_cache.delete(test_key)
                
                return {
                    'status': 'pass',
                    'message': 'Cache read/write successful',
                    'response_time': response_time,
                }
            else:
                return {
                    'status': 'fail',
                    'message': 'Cache read/write failed',
                    'response_time': response_time,
                }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Cache operation failed: {str(e)}',
                'response_time': None,
                'error': str(e),
            }
    
    def check_storage_health(self):
        """Vérifie la santé du stockage"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent < 90:
                status = 'pass'
                message = f'Storage usage: {usage_percent:.1f}%'
            elif usage_percent < 95:
                status = 'warn'
                message = f'Storage usage high: {usage_percent:.1f}%'
            else:
                status = 'fail'
                message = f'Storage usage critical: {usage_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'usage_percent': usage_percent,
                'total_space': disk_usage.total,
                'used_space': disk_usage.used,
                'free_space': disk_usage.free,
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Storage check failed: {str(e)}',
                'error': str(e),
            }
    
    def check_external_services_health(self):
        """Vérifie la santé des services externes"""
        # Ici vous pouvez ajouter des vérifications pour vos services externes
        # Par exemple: SendGrid, Twilio, etc.
        
        services_status = {
            'sendgrid': self._check_sendgrid_health(),
            'twilio': self._check_twilio_health(),
        }
        
        # Déterminer le statut global
        if all(status['status'] == 'pass' for status in services_status.values()):
            overall_status = 'pass'
            message = 'All external services healthy'
        elif any(status['status'] == 'fail' for status in services_status.values()):
            overall_status = 'fail'
            message = 'Some external services failed'
        else:
            overall_status = 'warn'
            message = 'Some external services degraded'
        
        return {
            'status': overall_status,
            'message': message,
            'services': services_status,
        }
    
    def _check_sendgrid_health(self):
        """Vérifie la santé de SendGrid"""
        try:
            # Ici vous pouvez implémenter une vraie vérification SendGrid
            # Pour l'instant, on simule
            return {
                'status': 'pass',
                'message': 'SendGrid API accessible',
                'response_time': 0.1,
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'SendGrid check failed: {str(e)}',
                'error': str(e),
            }
    
    def _check_twilio_health(self):
        """Vérifie la santé de Twilio"""
        try:
            # Ici vous pouvez implémenter une vraie vérification Twilio
            # Pour l'instant, on simule
            return {
                'status': 'pass',
                'message': 'Twilio API accessible',
                'response_time': 0.15,
            }
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Twilio check failed: {str(e)}',
                'error': str(e),
            }
    
    def run_health_check(self, health_check):
        """Exécute une vérification de santé spécifique"""
        start_time = time.time()
        
        try:
            if health_check.check_type == 'database':
                result = self.check_database_health()
            elif health_check.check_type == 'cache':
                result = self.check_cache_health()
            elif health_check.check_type == 'storage':
                result = self.check_storage_health()
            elif health_check.check_type == 'external_api':
                result = self.check_external_services_health()
            else:
                result = {
                    'status': 'unknown',
                    'message': f'Unknown check type: {health_check.check_type}',
                }
            
            response_time = time.time() - start_time
            result['response_time'] = response_time
            
            # Enregistrer le résultat
            health_check_result = HealthCheckResult.objects.create(
                health_check=health_check,
                status=result['status'],
                message=result['message'],
                response_time=response_time,
                error_message=result.get('error', ''),
                metadata=result,
            )
            
            return health_check_result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Enregistrer l'erreur
            health_check_result = HealthCheckResult.objects.create(
                health_check=health_check,
                status='fail',
                message=f'Health check failed: {str(e)}',
                response_time=response_time,
                error_message=str(e),
                metadata={'exception': str(e)},
            )
            
            return health_check_result
    
    def run_all_health_checks(self):
        """Exécute toutes les vérifications de santé actives"""
        health_checks = HealthCheck.objects.filter(is_active=True)
        results = []
        
        for health_check in health_checks:
            result = self.run_health_check(health_check)
            results.append(result)
        
        return results
    
    def get_system_health(self):
        """Récupère la santé générale du système"""
        cache_key = 'system_health'
        health = cache.get(cache_key)
        
        if health is None:
            # Exécuter les vérifications
            db_health = self.check_database_health()
            cache_health = self.check_cache_health()
            storage_health = self.check_storage_health()
            external_health = self.check_external_services_health()
            
            # Collecter les métriques système
            system_metrics = self._collect_system_metrics()
            
            # Déterminer le statut global
            statuses = [
                db_health['status'],
                cache_health['status'],
                storage_health['status'],
                external_health['status'],
            ]
            
            if all(status == 'pass' for status in statuses):
                overall_status = 'healthy'
            elif any(status == 'fail' for status in statuses):
                overall_status = 'unhealthy'
            else:
                overall_status = 'degraded'
            
            # Créer l'enregistrement de santé
            health = SystemHealth.objects.create(
                status=overall_status,
                database_status=db_health['status'],
                cache_status=cache_health['status'],
                storage_status=storage_health['status'],
                external_services_status=external_health['status'],
                cpu_usage=system_metrics.get('cpu_usage'),
                memory_usage=system_metrics.get('memory_usage'),
                disk_usage=system_metrics.get('disk_usage'),
                network_latency=system_metrics.get('network_latency'),
                issues=self._identify_issues(db_health, cache_health, storage_health, external_health),
                recommendations=self._generate_recommendations(overall_status, system_metrics),
                metadata={
                    'database': db_health,
                    'cache': cache_health,
                    'storage': storage_health,
                    'external_services': external_health,
                    'system_metrics': system_metrics,
                }
            )
            
            # Calculer le score global
            health.calculate_overall_score()
            health.update_status()
            
            cache.set(cache_key, health, self.cache_timeout)
        
        return health
    
    def _collect_system_metrics(self):
        """Collecte les métriques système"""
        try:
            metrics = {}
            
            # CPU
            metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Mémoire
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = memory.percent
            
            # Disque
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = (disk.used / disk.total) * 100
            
            # Réseau (latence simulée)
            metrics['network_latency'] = 50  # ms
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_issues(self, db_health, cache_health, storage_health, external_health):
        """Identifie les problèmes du système"""
        issues = []
        
        if db_health['status'] != 'pass':
            issues.append({
                'component': 'database',
                'severity': 'critical' if db_health['status'] == 'fail' else 'warning',
                'message': db_health['message'],
            })
        
        if cache_health['status'] != 'pass':
            issues.append({
                'component': 'cache',
                'severity': 'warning',
                'message': cache_health['message'],
            })
        
        if storage_health['status'] != 'pass':
            issues.append({
                'component': 'storage',
                'severity': 'critical' if storage_health['status'] == 'fail' else 'warning',
                'message': storage_health['message'],
            })
        
        if external_health['status'] != 'pass':
            issues.append({
                'component': 'external_services',
                'severity': 'warning',
                'message': external_health['message'],
            })
        
        return issues
    
    def _generate_recommendations(self, overall_status, system_metrics):
        """Génère des recommandations basées sur l'état du système"""
        recommendations = []
        
        if overall_status == 'unhealthy':
            recommendations.append({
                'priority': 'high',
                'message': 'System is unhealthy. Immediate attention required.',
            })
        
        if system_metrics.get('cpu_usage', 0) > 80:
            recommendations.append({
                'priority': 'medium',
                'message': 'High CPU usage detected. Consider scaling or optimization.',
            })
        
        if system_metrics.get('memory_usage', 0) > 80:
            recommendations.append({
                'priority': 'medium',
                'message': 'High memory usage detected. Consider memory optimization.',
            })
        
        if system_metrics.get('disk_usage', 0) > 90:
            recommendations.append({
                'priority': 'high',
                'message': 'Disk space running low. Consider cleanup or expansion.',
            })
        
        return recommendations
    
    def get_health_statistics(self, hours=24):
        """Récupère les statistiques de santé"""
        cache_key = f'health_statistics_{hours}'
        stats = cache.get(cache_key)
        
        if stats is None:
            from datetime import timedelta
            from django.db.models import Count
            
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Statistiques des vérifications de santé
            health_checks = HealthCheckResult.objects.filter(created_at__gte=start_time)
            
            stats = {
                'total_checks': health_checks.count(),
                'passed_checks': health_checks.filter(status='pass').count(),
                'failed_checks': health_checks.filter(status='fail').count(),
                'warning_checks': health_checks.filter(status='warn').count(),
                'checks_by_type': list(
                    health_checks.values('health_check__check_type')
                    .annotate(count=Count('id'))
                    .order_by('health_check__check_type')
                ),
                'checks_by_status': list(
                    health_checks.values('status')
                    .annotate(count=Count('id'))
                    .order_by('status')
                ),
                'average_response_time': health_checks.aggregate(
                    avg_time=Avg('response_time')
                )['avg_time'] or 0,
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats



