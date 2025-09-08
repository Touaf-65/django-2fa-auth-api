"""
Service de gestion des alertes
"""
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Q
from apps.monitoring.models import Alert, AlertRule, AlertNotification


class AlertService:
    """Service pour la gestion des alertes"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def create_alert(self, rule, metric_value, severity='medium', message=None, **kwargs):
        """Crée une nouvelle alerte"""
        if message is None:
            message = f"Alert triggered for {rule.name}"
        
        alert = Alert.objects.create(
            rule=rule,
            metric_value=metric_value,
            severity=severity,
            message=message,
            value=metric_value.value,
            threshold=rule.threshold,
            labels=kwargs.get('labels', {}),
            annotations=kwargs.get('annotations', {}),
        )
        
        # Envoyer les notifications
        self._send_notifications(alert)
        
        # Invalide le cache
        self._invalidate_alert_cache()
        
        return alert
    
    def evaluate_alert_rules(self, metric_value):
        """Évalue toutes les règles d'alerte pour une valeur de métrique"""
        rules = AlertRule.objects.filter(
            metric=metric_value.metric,
            is_enabled=True,
            status='active'
        )
        
        triggered_alerts = []
        
        for rule in rules:
            if rule.evaluate(metric_value):
                alert = self.create_alert(
                    rule=rule,
                    metric_value=metric_value,
                    severity=rule.severity,
                    message=f"Rule '{rule.name}' triggered: {metric_value.value} {rule.condition} {rule.threshold}"
                )
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def acknowledge_alert(self, alert, user):
        """Acquitte une alerte"""
        alert.acknowledge(user)
        
        # Invalide le cache
        self._invalidate_alert_cache()
        
        return alert
    
    def resolve_alert(self, alert):
        """Résout une alerte"""
        alert.resolve()
        
        # Invalide le cache
        self._invalidate_alert_cache()
        
        return alert
    
    def get_active_alerts(self, severity=None, rule=None):
        """Récupère les alertes actives"""
        queryset = Alert.objects.filter(status='firing')
        
        if severity:
            queryset = queryset.filter(severity=severity)
        if rule:
            queryset = queryset.filter(rule=rule)
        
        return queryset.order_by('-created_at')
    
    def get_alert_statistics(self, hours=24):
        """Récupère les statistiques des alertes"""
        cache_key = f'alert_statistics_{hours}'
        stats = cache.get(cache_key)
        
        if stats is None:
            from datetime import timedelta
            
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            queryset = Alert.objects.filter(created_at__gte=start_time)
            
            stats = {
                'total_alerts': queryset.count(),
                'active_alerts': queryset.filter(status='firing').count(),
                'resolved_alerts': queryset.filter(status='resolved').count(),
                'acknowledged_alerts': queryset.filter(status='acknowledged').count(),
                'alerts_by_severity': list(
                    queryset.values('severity')
                    .annotate(count=Count('id'))
                    .order_by('severity')
                ),
                'alerts_by_rule': list(
                    queryset.values('rule__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
                'alerts_by_hour': list(
                    queryset.extra(
                        select={'hour': 'EXTRACT(hour FROM created_at)'}
                    ).values('hour')
                    .annotate(count=Count('id'))
                    .order_by('hour')
                ),
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def get_alert_trends(self, days=7):
        """Récupère les tendances des alertes"""
        cache_key = f'alert_trends_{days}'
        trends = cache.get(cache_key)
        
        if trends is None:
            from datetime import timedelta
            
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # Tendance par jour
            daily_trends = list(
                Alert.objects.filter(created_at__gte=start_time)
                .extra(select={'date': 'DATE(created_at)'})
                .values('date')
                .annotate(
                    total_alerts=Count('id'),
                    firing_alerts=Count('id', filter=Q(status='firing')),
                    resolved_alerts=Count('id', filter=Q(status='resolved')),
                    acknowledged_alerts=Count('id', filter=Q(status='acknowledged'))
                )
                .order_by('date')
            )
            
            trends = {
                'daily_trends': daily_trends,
                'period': {
                    'start_date': start_time.isoformat(),
                    'end_date': end_time.isoformat(),
                    'days': days,
                }
            }
            
            cache.set(cache_key, trends, self.cache_timeout)
        
        return trends
    
    def create_alert_rule(self, name, metric, condition, threshold, **kwargs):
        """Crée une nouvelle règle d'alerte"""
        rule = AlertRule.objects.create(
            name=name,
            description=kwargs.get('description', ''),
            metric=metric,
            condition=condition,
            threshold=threshold,
            duration=kwargs.get('duration', 0),
            severity=kwargs.get('severity', 'medium'),
            status=kwargs.get('status', 'active'),
            is_enabled=kwargs.get('is_enabled', True),
            notification_channels=kwargs.get('notification_channels', []),
            notification_template=kwargs.get('notification_template', ''),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {}),
        )
        
        return rule
    
    def update_alert_rule(self, rule, **kwargs):
        """Met à jour une règle d'alerte"""
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.save()
        return rule
    
    def delete_alert_rule(self, rule):
        """Supprime une règle d'alerte"""
        rule.delete()
    
    def test_alert_rule(self, rule, test_value):
        """Teste une règle d'alerte avec une valeur"""
        if rule.condition == 'gt':
            return test_value > rule.threshold
        elif rule.condition == 'gte':
            return test_value >= rule.threshold
        elif rule.condition == 'lt':
            return test_value < rule.threshold
        elif rule.condition == 'lte':
            return test_value <= rule.threshold
        elif rule.condition == 'eq':
            return test_value == rule.threshold
        elif rule.condition == 'neq':
            return test_value != rule.threshold
        
        return False
    
    def _send_notifications(self, alert):
        """Envoie les notifications pour une alerte"""
        from apps.monitoring.services import NotificationService
        
        notification_service = NotificationService()
        
        # Envoyer les notifications configurées dans la règle
        for channel in alert.rule.notification_channels:
            notification = AlertNotification.objects.create(
                alert=alert,
                channel=channel['type'],
                recipient=channel['recipient'],
                subject=f"Alert: {alert.rule.name}",
                message=alert.message,
            )
            
            # Envoyer la notification
            success = notification_service.send_notification(notification)
            
            if success:
                notification.mark_sent()
            else:
                notification.mark_failed("Failed to send notification")
    
    def _invalidate_alert_cache(self):
        """Invalide le cache des alertes"""
        cache_keys = [
            'alert_statistics_*',
            'alert_trends_*',
            'active_alerts',
        ]
        
        for key in cache_keys:
            cache.delete(key)


class AlertManager:
    """Gestionnaire d'alertes avec contexte"""
    
    def __init__(self, service=None):
        self.service = service or AlertService()
        self.alerts = []
    
    def create_alert(self, rule, metric_value, **kwargs):
        """Crée une alerte"""
        alert = self.service.create_alert(rule, metric_value, **kwargs)
        self.alerts.append(alert)
        return alert
    
    def acknowledge_all(self, user):
        """Acquitte toutes les alertes"""
        for alert in self.alerts:
            if alert.is_firing:
                self.service.acknowledge_alert(alert, user)
    
    def resolve_all(self):
        """Résout toutes les alertes"""
        for alert in self.alerts:
            if alert.is_firing:
                self.service.resolve_alert(alert)
    
    def get_summary(self):
        """Récupère un résumé des alertes"""
        return {
            'total_alerts': len(self.alerts),
            'firing_alerts': len([a for a in self.alerts if a.is_firing]),
            'resolved_alerts': len([a for a in self.alerts if a.is_resolved]),
            'acknowledged_alerts': len([a for a in self.alerts if a.is_acknowledged]),
        }

