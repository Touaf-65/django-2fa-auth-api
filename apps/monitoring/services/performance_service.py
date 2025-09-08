"""
Service de monitoring des performances
"""
import time
import psutil
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Avg, Count, Sum, Min, Max
from apps.monitoring.models import PerformanceMetric, PerformanceReport


class PerformanceService:
    """Service pour le monitoring des performances"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def collect_system_metrics(self):
        """Collecte les métriques système"""
        metrics = {}
        
        try:
            # CPU
            metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            metrics['cpu_count'] = psutil.cpu_count()
            
            # Mémoire
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = memory.percent
            metrics['memory_total'] = memory.total
            metrics['memory_available'] = memory.available
            
            # Disque
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = (disk.used / disk.total) * 100
            metrics['disk_total'] = disk.total
            metrics['disk_free'] = disk.free
            
            # Réseau
            network = psutil.net_io_counters()
            metrics['network_bytes_sent'] = network.bytes_sent
            metrics['network_bytes_recv'] = network.bytes_recv
            
        except Exception as e:
            # En cas d'erreur, retourner des valeurs par défaut
            metrics = {
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'error': str(e)
            }
        
        return metrics
    
    def record_performance_metric(self, name, value, category='custom', **kwargs):
        """Enregistre une métrique de performance"""
        metric, created = PerformanceMetric.objects.get_or_create(
            name=name,
            defaults={
                'display_name': name.replace('_', ' ').title(),
                'category': category,
                'description': kwargs.get('description', ''),
                'is_active': kwargs.get('is_active', True),
                'collection_interval': kwargs.get('collection_interval', 60),
                'warning_threshold': kwargs.get('warning_threshold'),
                'critical_threshold': kwargs.get('critical_threshold'),
                'tags': kwargs.get('tags', []),
                'metadata': kwargs.get('metadata', {}),
            }
        )
        
        # Enregistrer la valeur
        from apps.monitoring.models import MetricValue
        metric_value = MetricValue.objects.create(
            metric=metric,
            value=value,
            timestamp=timezone.now(),
            labels=kwargs.get('labels', {}),
            metadata=kwargs.get('metadata', {}),
        )
        
        return metric_value
    
    def record_response_time(self, endpoint, method, response_time, status_code=None, **kwargs):
        """Enregistre le temps de réponse d'un endpoint"""
        labels = {
            'endpoint': endpoint,
            'method': method,
        }
        
        if status_code:
            labels['status_code'] = str(status_code)
        
        return self.record_performance_metric(
            'response_time',
            response_time,
            category='response_time',
            labels=labels,
            **kwargs
        )
    
    def record_throughput(self, endpoint, method, count, **kwargs):
        """Enregistre le débit d'un endpoint"""
        labels = {
            'endpoint': endpoint,
            'method': method,
        }
        
        return self.record_performance_metric(
            'throughput',
            count,
            category='throughput',
            labels=labels,
            **kwargs
        )
    
    def record_error_rate(self, endpoint, method, error_count, total_count, **kwargs):
        """Enregistre le taux d'erreur d'un endpoint"""
        labels = {
            'endpoint': endpoint,
            'method': method,
        }
        
        error_rate = (error_count / total_count) * 100 if total_count > 0 else 0
        
        return self.record_performance_metric(
            'error_rate',
            error_rate,
            category='error_rate',
            labels=labels,
            **kwargs
        )
    
    def get_performance_summary(self, hours=24):
        """Récupère un résumé des performances"""
        cache_key = f'performance_summary_{hours}'
        summary = cache.get(cache_key)
        
        if summary is None:
            from datetime import timedelta
            
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            metrics = PerformanceMetric.objects.filter(is_active=True)
            summary = {
                'total_metrics': metrics.count(),
                'metrics_by_category': list(
                    metrics.values('category')
                    .annotate(count=Count('id'))
                    .order_by('category')
                ),
                'system_metrics': self.collect_system_metrics(),
                'performance_metrics': [],
            }
            
            # Ajouter les métriques de performance récentes
            for metric in metrics[:10]:
                latest_value = metric.get_latest_value()
                if latest_value:
                    summary['performance_metrics'].append({
                        'name': metric.name,
                        'display_name': metric.display_name,
                        'category': metric.category,
                        'value': latest_value.value,
                        'timestamp': latest_value.timestamp.isoformat(),
                    })
            
            cache.set(cache_key, summary, self.cache_timeout)
        
        return summary
    
    def get_performance_trends(self, metric_name, hours=24):
        """Récupère les tendances de performance pour une métrique"""
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        try:
            metric = PerformanceMetric.objects.get(name=metric_name)
            values = metric.get_values_in_range(start_time, end_time)
            
            if not values.exists():
                return None
            
            trends = {
                'metric_name': metric_name,
                'display_name': metric.display_name,
                'category': metric.category,
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'hours': hours,
                },
                'statistics': values.aggregate(
                    count=Count('id'),
                    min=Min('value'),
                    max=Max('value'),
                    avg=Avg('value'),
                    sum=Sum('value')
                ),
                'values': [
                    {
                        'timestamp': v.timestamp.isoformat(),
                        'value': v.value,
                        'labels': v.labels,
                    }
                    for v in values.order_by('timestamp')
                ]
            }
            
            return trends
            
        except PerformanceMetric.DoesNotExist:
            return None
    
    def generate_performance_report(self, name, report_type, period_start, period_end, metrics=None):
        """Génère un rapport de performance"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Créer le rapport
        report = PerformanceReport.objects.create(
            name=name,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
        )
        
        # Ajouter les métriques
        if metrics:
            report.metrics.set(metrics)
        else:
            # Utiliser toutes les métriques actives
            report.metrics.set(PerformanceMetric.objects.filter(is_active=True))
        
        # Générer le contenu du rapport
        report.details = self._generate_report_details(report)
        report.save()
        
        # Marquer comme généré
        report.mark_generated()
        
        return report
    
    def _generate_report_details(self, report):
        """Génère les détails d'un rapport"""
        details = {
            'generated_at': timezone.now().isoformat(),
            'period_duration': str(report.duration),
            'metrics_analyzed': report.metrics.count(),
            'metrics_data': {},
        }
        
        # Analyser chaque métrique
        for metric in report.metrics.all():
            values = metric.get_values_in_range(
                report.period_start,
                report.period_end
            )
            
            if values.exists():
                stats = values.aggregate(
                    count=Count('id'),
                    min=Min('value'),
                    max=Max('value'),
                    avg=Avg('value'),
                    sum=Sum('value')
                )
                
                details['metrics_data'][metric.name] = {
                    'display_name': metric.display_name,
                    'category': metric.category,
                    'statistics': stats,
                    'latest_value': values.order_by('-timestamp').first().value,
                }
        
        return details
    
    def get_slow_endpoints(self, hours=24, limit=10):
        """Récupère les endpoints les plus lents"""
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        try:
            response_time_metric = PerformanceMetric.objects.get(
                name='response_time',
                category='response_time'
            )
            
            values = response_time_metric.get_values_in_range(start_time, end_time)
            
            # Grouper par endpoint et calculer la moyenne
            endpoint_stats = {}
            for value in values:
                endpoint = value.labels.get('endpoint', 'unknown')
                method = value.labels.get('method', 'unknown')
                key = f"{method} {endpoint}"
                
                if key not in endpoint_stats:
                    endpoint_stats[key] = {
                        'endpoint': endpoint,
                        'method': method,
                        'values': [],
                        'count': 0,
                    }
                
                endpoint_stats[key]['values'].append(value.value)
                endpoint_stats[key]['count'] += 1
            
            # Calculer les moyennes et trier
            slow_endpoints = []
            for key, stats in endpoint_stats.items():
                avg_response_time = sum(stats['values']) / len(stats['values'])
                slow_endpoints.append({
                    'endpoint': stats['endpoint'],
                    'method': stats['method'],
                    'average_response_time': avg_response_time,
                    'request_count': stats['count'],
                })
            
            # Trier par temps de réponse moyen
            slow_endpoints.sort(key=lambda x: x['average_response_time'], reverse=True)
            
            return slow_endpoints[:limit]
            
        except PerformanceMetric.DoesNotExist:
            return []
    
    def get_error_endpoints(self, hours=24, limit=10):
        """Récupère les endpoints avec le plus d'erreurs"""
        from datetime import timedelta
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        try:
            error_rate_metric = PerformanceMetric.objects.get(
                name='error_rate',
                category='error_rate'
            )
            
            values = error_rate_metric.get_values_in_range(start_time, end_time)
            
            # Grouper par endpoint
            endpoint_stats = {}
            for value in values:
                endpoint = value.labels.get('endpoint', 'unknown')
                method = value.labels.get('method', 'unknown')
                key = f"{method} {endpoint}"
                
                if key not in endpoint_stats:
                    endpoint_stats[key] = {
                        'endpoint': endpoint,
                        'method': method,
                        'error_rates': [],
                    }
                
                endpoint_stats[key]['error_rates'].append(value.value)
            
            # Calculer les moyennes et trier
            error_endpoints = []
            for key, stats in endpoint_stats.items():
                avg_error_rate = sum(stats['error_rates']) / len(stats['error_rates'])
                error_endpoints.append({
                    'endpoint': stats['endpoint'],
                    'method': stats['method'],
                    'average_error_rate': avg_error_rate,
                    'measurement_count': len(stats['error_rates']),
                })
            
            # Trier par taux d'erreur moyen
            error_endpoints.sort(key=lambda x: x['average_error_rate'], reverse=True)
            
            return error_endpoints[:limit]
            
        except PerformanceMetric.DoesNotExist:
            return []
    
    def cleanup_old_metrics(self, days=30):
        """Nettoie les anciennes métriques de performance"""
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Nettoyer les valeurs de métriques
        from apps.monitoring.models import MetricValue
        deleted_values, _ = MetricValue.objects.filter(
            metric__in=PerformanceMetric.objects.all(),
            timestamp__lt=cutoff_date
        ).delete()
        
        return deleted_values

