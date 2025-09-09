"""
Service principal pour les calculs analytiques
"""
import json
from datetime import datetime, timedelta
from django.db import models, connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from apps.analytics.models import AnalyticsMetric, MetricValue
from apps.monitoring.models import LogEntry, Metric as MonitoringMetric
from apps.authentication.models import User
from apps.security.models import SecurityEvent

User = get_user_model()


class AnalyticsService:
    """Service principal pour les calculs analytiques"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 heure
    
    def calculate_metric(self, metric_name, start_date=None, end_date=None, labels=None):
        """Calcule une métrique spécifique"""
        try:
            metric = AnalyticsMetric.objects.get(name=metric_name, is_active=True)
            
            # Utiliser le cache si disponible
            cache_key = f"metric_{metric_name}_{start_date}_{end_date}_{labels}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Calculer la métrique selon son type
            if metric.metric_type == 'counter':
                result = self._calculate_counter_metric(metric, start_date, end_date, labels)
            elif metric.metric_type == 'gauge':
                result = self._calculate_gauge_metric(metric, start_date, end_date, labels)
            elif metric.metric_type == 'histogram':
                result = self._calculate_histogram_metric(metric, start_date, end_date, labels)
            elif metric.metric_type == 'summary':
                result = self._calculate_summary_metric(metric, start_date, end_date, labels)
            else:
                result = self._calculate_custom_metric(metric, start_date, end_date, labels)
            
            # Mettre en cache le résultat
            cache.set(cache_key, result, self.cache_timeout)
            
            # Enregistrer la valeur calculée
            self._record_metric_value(metric, result, labels)
            
            return result
            
        except AnalyticsMetric.DoesNotExist:
            raise ValueError(f"Métrique '{metric_name}' non trouvée")
        except Exception as e:
            raise Exception(f"Erreur lors du calcul de la métrique: {str(e)}")
    
    def _calculate_counter_metric(self, metric, start_date, end_date, labels):
        """Calcule une métrique de type compteur"""
        if metric.name == 'total_users':
            return User.objects.count()
        elif metric.name == 'active_users':
            if not start_date:
                start_date = timezone.now() - timedelta(days=30)
            return User.objects.filter(last_login__gte=start_date).count()
        elif metric.name == 'api_requests_total':
            query = LogEntry.objects.filter(source='api')
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            return query.count()
        elif metric.name == 'security_events_total':
            query = SecurityEvent.objects.all()
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            return query.count()
        else:
            return self._execute_custom_query(metric.calculation_query, start_date, end_date)
    
    def _calculate_gauge_metric(self, metric, start_date, end_date, labels):
        """Calcule une métrique de type jauge"""
        if metric.name == 'avg_response_time':
            query = LogEntry.objects.filter(
                source='api',
                response_time__isnull=False
            )
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            
            result = query.aggregate(avg=models.Avg('response_time'))
            return round(result['avg'] or 0, 3)
        
        elif metric.name == 'error_rate':
            total_requests = LogEntry.objects.filter(source='api')
            error_requests = LogEntry.objects.filter(
                source='api',
                level__in=['ERROR', 'CRITICAL']
            )
            
            if start_date:
                total_requests = total_requests.filter(created_at__gte=start_date)
                error_requests = error_requests.filter(created_at__gte=start_date)
            if end_date:
                total_requests = total_requests.filter(created_at__lte=end_date)
                error_requests = error_requests.filter(created_at__lte=end_date)
            
            total_count = total_requests.count()
            error_count = error_requests.count()
            
            return round((error_count / total_count * 100) if total_count > 0 else 0, 2)
        
        else:
            return self._execute_custom_query(metric.calculation_query, start_date, end_date)
    
    def _calculate_histogram_metric(self, metric, start_date, end_date, labels):
        """Calcule une métrique de type histogramme"""
        if metric.name == 'response_time_distribution':
            query = LogEntry.objects.filter(
                source='api',
                response_time__isnull=False
            )
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            
            # Créer des buckets pour l'histogramme
            buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float('inf')]
            distribution = {}
            
            for i, bucket in enumerate(buckets):
                if i == 0:
                    count = query.filter(response_time__lt=bucket).count()
                elif bucket == float('inf'):
                    count = query.filter(response_time__gte=buckets[i-1]).count()
                else:
                    count = query.filter(
                        response_time__gte=buckets[i-1],
                        response_time__lt=bucket
                    ).count()
                
                distribution[f"<{bucket}s" if bucket != float('inf') else f">={buckets[i-1]}s"] = count
            
            return distribution
        
        else:
            return self._execute_custom_query(metric.calculation_query, start_date, end_date)
    
    def _calculate_summary_metric(self, metric, start_date, end_date, labels):
        """Calcule une métrique de type résumé"""
        if metric.name == 'user_activity_summary':
            query = LogEntry.objects.filter(source='api')
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            
            return {
                'total_requests': query.count(),
                'unique_users': query.values('user').distinct().count(),
                'avg_response_time': query.aggregate(avg=models.Avg('response_time'))['avg'] or 0,
                'error_count': query.filter(level__in=['ERROR', 'CRITICAL']).count(),
            }
        
        else:
            return self._execute_custom_query(metric.calculation_query, start_date, end_date)
    
    def _calculate_custom_metric(self, metric, start_date, end_date, labels):
        """Calcule une métrique personnalisée"""
        return self._execute_custom_query(metric.calculation_query, start_date, end_date)
    
    def _execute_custom_query(self, query, start_date, end_date):
        """Exécute une requête personnalisée"""
        if not query:
            return 0
        
        # Remplacer les placeholders
        if start_date:
            query = query.replace('{start_date}', f"'{start_date.isoformat()}'")
        if end_date:
            query = query.replace('{end_date}', f"'{end_date.isoformat()}'")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            raise Exception(f"Erreur dans la requête personnalisée: {str(e)}")
    
    def _record_metric_value(self, metric, value, labels):
        """Enregistre une valeur de métrique"""
        MetricValue.objects.create(
            metric=metric,
            value=value,
            timestamp=timezone.now(),
            labels=labels or {},
            source='analytics_service'
        )
        
        # Mettre à jour la métrique
        metric.last_calculated = timezone.now()
        metric.save()
    
    def get_metric_trend(self, metric_name, days=30, granularity='day'):
        """Obtient la tendance d'une métrique sur une période"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Déterminer l'intervalle selon la granularité
        if granularity == 'hour':
            interval = timedelta(hours=1)
            date_format = '%Y-%m-%d %H:00:00'
        elif granularity == 'day':
            interval = timedelta(days=1)
            date_format = '%Y-%m-%d'
        elif granularity == 'week':
            interval = timedelta(weeks=1)
            date_format = '%Y-W%U'
        else:
            interval = timedelta(days=1)
            date_format = '%Y-%m-%d'
        
        # Récupérer les valeurs existantes
        values = MetricValue.objects.filter(
            metric__name=metric_name,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('timestamp')
        
        # Créer la série temporelle
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Trouver la valeur la plus proche
            closest_value = None
            min_diff = float('inf')
            
            for value in values:
                diff = abs((value.timestamp - current_date).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_value = value
            
            trend_data.append({
                'timestamp': current_date.strftime(date_format),
                'value': closest_value.value if closest_value else 0,
                'labels': closest_value.labels if closest_value else {}
            })
            
            current_date += interval
        
        return trend_data
    
    def get_top_metrics(self, category=None, limit=10):
        """Obtient les métriques les plus importantes"""
        query = AnalyticsMetric.objects.filter(is_active=True)
        if category:
            query = query.filter(category=category)
        
        metrics = query.order_by('-last_calculated')[:limit]
        
        result = []
        for metric in metrics:
            try:
                value = self.calculate_metric(metric.name)
                result.append({
                    'metric': metric,
                    'value': value,
                    'unit': metric.unit,
                    'last_calculated': metric.last_calculated
                })
            except Exception as e:
                result.append({
                    'metric': metric,
                    'value': None,
                    'error': str(e),
                    'last_calculated': metric.last_calculated
                })
        
        return result
    
    def create_metric(self, name, display_name, category, metric_type, **kwargs):
        """Crée une nouvelle métrique"""
        metric = AnalyticsMetric.objects.create(
            name=name,
            display_name=display_name,
            category=category,
            metric_type=metric_type,
            **kwargs
        )
        return metric
    
    def update_metric(self, metric_name, **kwargs):
        """Met à jour une métrique existante"""
        try:
            metric = AnalyticsMetric.objects.get(name=metric_name)
            for key, value in kwargs.items():
                setattr(metric, key, value)
            metric.save()
            return metric
        except AnalyticsMetric.DoesNotExist:
            raise ValueError(f"Métrique '{metric_name}' non trouvée")
    
    def delete_metric(self, metric_name):
        """Supprime une métrique"""
        try:
            metric = AnalyticsMetric.objects.get(name=metric_name)
            metric.is_active = False
            metric.save()
            return True
        except AnalyticsMetric.DoesNotExist:
            raise ValueError(f"Métrique '{metric_name}' non trouvée")

