"""
Service de collecte et gestion des métriques
"""
import time
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Avg, Count, Sum, Min, Max
from apps.monitoring.models import Metric, MetricValue


class MetricsService:
    """Service pour la gestion des métriques"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def create_metric(self, name, display_name, metric_type='gauge', unit='count', **kwargs):
        """Crée une nouvelle métrique"""
        metric, created = Metric.objects.get_or_create(
            name=name,
            defaults={
                'display_name': display_name,
                'metric_type': metric_type,
                'unit': unit,
                'description': kwargs.get('description', ''),
                'is_active': kwargs.get('is_active', True),
                'is_public': kwargs.get('is_public', False),
                'retention_days': kwargs.get('retention_days', 30),
                'warning_threshold': kwargs.get('warning_threshold'),
                'critical_threshold': kwargs.get('critical_threshold'),
                'tags': kwargs.get('tags', []),
                'metadata': kwargs.get('metadata', {}),
            }
        )
        
        if not created:
            # Mise à jour des propriétés
            for key, value in kwargs.items():
                if hasattr(metric, key):
                    setattr(metric, key, value)
            metric.save()
        
        return metric
    
    def record_metric(self, metric_name, value, labels=None, metadata=None, **kwargs):
        """Enregistre une valeur de métrique"""
        try:
            metric = Metric.objects.get(name=metric_name, is_active=True)
        except Metric.DoesNotExist:
            # Créer la métrique automatiquement si elle n'existe pas
            metric = self.create_metric(
                name=metric_name,
                display_name=metric_name.replace('_', ' ').title(),
                **kwargs
            )
        
        # Créer la valeur de métrique
        metric_value = MetricValue.objects.create(
            metric=metric,
            value=value,
            timestamp=timezone.now(),
            user=kwargs.get('user'),
            session_id=kwargs.get('session_id', ''),
            request_id=kwargs.get('request_id', ''),
            labels=labels or {},
            metadata=metadata or {},
        )
        
        # Vérifier les seuils d'alerte
        self._check_alert_thresholds(metric, metric_value)
        
        # Invalide le cache
        self._invalidate_metric_cache(metric_name)
        
        return metric_value
    
    def increment_counter(self, metric_name, value=1, labels=None, **kwargs):
        """Incrémente un compteur"""
        return self.record_metric(
            metric_name,
            value,
            labels=labels,
            metric_type='counter',
            **kwargs
        )
    
    def set_gauge(self, metric_name, value, labels=None, **kwargs):
        """Définit la valeur d'un gauge"""
        return self.record_metric(
            metric_name,
            value,
            labels=labels,
            metric_type='gauge',
            **kwargs
        )
    
    def record_histogram(self, metric_name, value, labels=None, **kwargs):
        """Enregistre une valeur d'histogramme"""
        return self.record_metric(
            metric_name,
            value,
            labels=labels,
            metric_type='histogram',
            **kwargs
        )
    
    def record_timing(self, metric_name, duration, labels=None, **kwargs):
        """Enregistre un temps d'exécution"""
        return self.record_metric(
            metric_name,
            duration,
            labels=labels,
            metric_type='histogram',
            unit='seconds',
            **kwargs
        )
    
    def get_metric_value(self, metric_name, labels=None):
        """Récupère la dernière valeur d'une métrique"""
        try:
            metric = Metric.objects.get(name=metric_name)
            queryset = metric.values.all()
            
            if labels:
                for key, value in labels.items():
                    queryset = queryset.filter(labels__contains={key: value})
            
            return queryset.order_by('-timestamp').first()
        except Metric.DoesNotExist:
            return None
    
    def get_metric_values(self, metric_name, start_time, end_time, labels=None):
        """Récupère les valeurs d'une métrique dans une plage de temps"""
        try:
            metric = Metric.objects.get(name=metric_name)
            queryset = metric.values.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            
            if labels:
                for key, value in labels.items():
                    queryset = queryset.filter(labels__contains={key: value})
            
            return queryset.order_by('timestamp')
        except Metric.DoesNotExist:
            return MetricValue.objects.none()
    
    def get_metric_statistics(self, metric_name, start_time, end_time, labels=None):
        """Récupère les statistiques d'une métrique"""
        values = self.get_metric_values(metric_name, start_time, end_time, labels)
        
        if not values.exists():
            return None
        
        stats = values.aggregate(
            count=Count('id'),
            min=Min('value'),
            max=Max('value'),
            avg=Avg('value'),
            sum=Sum('value')
        )
        
        return {
            'metric_name': metric_name,
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
            },
            'statistics': stats,
            'latest_value': values.order_by('-timestamp').first().value,
        }
    
    def get_metrics_summary(self, hours=24):
        """Récupère un résumé de toutes les métriques"""
        cache_key = f'metrics_summary_{hours}'
        summary = cache.get(cache_key)
        
        if summary is None:
            from datetime import timedelta
            
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            metrics = Metric.objects.filter(is_active=True)
            summary = {
                'total_metrics': metrics.count(),
                'metrics_by_type': list(
                    metrics.values('metric_type')
                    .annotate(count=Count('id'))
                    .order_by('metric_type')
                ),
                'active_metrics': metrics.filter(is_active=True).count(),
                'public_metrics': metrics.filter(is_public=True).count(),
                'metrics_with_alerts': metrics.filter(
                    models.Q(warning_threshold__isnull=False) |
                    models.Q(critical_threshold__isnull=False)
                ).count(),
                'recent_values': [],
            }
            
            # Ajouter les dernières valeurs pour chaque métrique
            for metric in metrics[:10]:  # Limiter à 10 métriques
                latest_value = metric.get_latest_value()
                if latest_value:
                    summary['recent_values'].append({
                        'metric_name': metric.name,
                        'display_name': metric.display_name,
                        'value': latest_value.value,
                        'timestamp': latest_value.timestamp.isoformat(),
                        'unit': metric.unit,
                    })
            
            cache.set(cache_key, summary, self.cache_timeout)
        
        return summary
    
    def cleanup_old_metrics(self, days=None):
        """Nettoie les anciennes valeurs de métriques"""
        from datetime import timedelta
        
        if days is None:
            # Utiliser la rétention configurée pour chaque métrique
            metrics = Metric.objects.filter(is_active=True)
            deleted_count = 0
            
            for metric in metrics:
                cutoff_date = timezone.now() - timedelta(days=metric.retention_days)
                deleted, _ = metric.values.filter(timestamp__lt=cutoff_date).delete()
                deleted_count += deleted
            
            return deleted_count
        else:
            # Utiliser une rétention globale
            cutoff_date = timezone.now() - timedelta(days=days)
            deleted, _ = MetricValue.objects.filter(timestamp__lt=cutoff_date).delete()
            return deleted
    
    def _check_alert_thresholds(self, metric, metric_value):
        """Vérifie les seuils d'alerte pour une métrique"""
        from apps.monitoring.services import AlertService
        
        alert_service = AlertService()
        
        # Vérifier le seuil d'avertissement
        if metric.warning_threshold and metric_value.value > metric.warning_threshold:
            alert_service.create_alert(
                metric=metric,
                metric_value=metric_value,
                severity='warning',
                message=f"Metric {metric.display_name} exceeded warning threshold: {metric_value.value} > {metric.warning_threshold}"
            )
        
        # Vérifier le seuil critique
        if metric.critical_threshold and metric_value.value > metric.critical_threshold:
            alert_service.create_alert(
                metric=metric,
                metric_value=metric_value,
                severity='critical',
                message=f"Metric {metric.display_name} exceeded critical threshold: {metric_value.value} > {metric.critical_threshold}"
            )
    
    def _invalidate_metric_cache(self, metric_name):
        """Invalide le cache d'une métrique"""
        cache_keys = [
            f'metric_{metric_name}',
            'metrics_summary_*',
        ]
        
        for key in cache_keys:
            cache.delete(key)


class MetricsCollector:
    """Collecteur de métriques avec contexte"""
    
    def __init__(self, service=None):
        self.service = service or MetricsService()
        self.start_time = None
        self.metrics = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.record_timing('operation_duration', duration)
    
    def counter(self, name, value=1, labels=None, **kwargs):
        """Incrémente un compteur"""
        self.metrics[name] = self.service.increment_counter(name, value, labels, **kwargs)
        return self.metrics[name]
    
    def gauge(self, name, value, labels=None, **kwargs):
        """Définit un gauge"""
        self.metrics[name] = self.service.set_gauge(name, value, labels, **kwargs)
        return self.metrics[name]
    
    def histogram(self, name, value, labels=None, **kwargs):
        """Enregistre un histogramme"""
        self.metrics[name] = self.service.record_histogram(name, value, labels, **kwargs)
        return self.metrics[name]
    
    def timing(self, name, duration, labels=None, **kwargs):
        """Enregistre un timing"""
        self.metrics[name] = self.service.record_timing(name, duration, labels, **kwargs)
        return self.metrics[name]
    
    def record_timing(self, name, labels=None, **kwargs):
        """Enregistre le temps écoulé depuis le début"""
        if self.start_time:
            duration = time.time() - self.start_time
            return self.timing(name, duration, labels, **kwargs)
        return None

