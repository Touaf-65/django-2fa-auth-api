"""
Service pour la gestion des alertes système
"""
import psutil
import time
from django.utils import timezone
from django.db.models import Q
from apps.admin_api.models import AlertRule, SystemAlert, AlertNotification
from .monitoring_service import MonitoringService


class AlertService:
    """Service pour la gestion des alertes système"""
    
    def __init__(self):
        self.monitoring = MonitoringService()
    
    def check_all_alerts(self):
        """Vérifie toutes les règles d'alerte actives"""
        active_rules = AlertRule.objects.filter(status='active')
        
        for rule in active_rules:
            try:
                self.check_alert_rule(rule)
            except Exception as e:
                print(f"Erreur lors de la vérification de la règle {rule.name}: {e}")
    
    def check_alert_rule(self, rule):
        """Vérifie une règle d'alerte spécifique"""
        # Vérifie si la règle est en cooldown
        if self._is_in_cooldown(rule):
            return
        
        # Vérifie le nombre maximum d'alertes par heure
        if self._has_reached_hourly_limit(rule):
            return
        
        # Récupère la valeur actuelle selon le type d'alerte
        current_value = self._get_current_value(rule)
        
        if current_value is None:
            return
        
        # Vérifie si l'alerte doit être déclenchée
        if rule.should_trigger_alert(current_value):
            self._trigger_alert(rule, current_value)
    
    def _is_in_cooldown(self, rule):
        """Vérifie si la règle est en période de cooldown"""
        last_alert = SystemAlert.objects.filter(
            alert_rule=rule,
            status__in=['triggered', 'acknowledged']
        ).order_by('-triggered_at').first()
        
        if not last_alert:
            return False
        
        cooldown_end = last_alert.triggered_at + timezone.timedelta(seconds=rule.cooldown_period)
        return timezone.now() < cooldown_end
    
    def _has_reached_hourly_limit(self, rule):
        """Vérifie si la règle a atteint la limite d'alertes par heure"""
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        
        hourly_count = SystemAlert.objects.filter(
            alert_rule=rule,
            triggered_at__gte=one_hour_ago
        ).count()
        
        return hourly_count >= rule.max_alerts_per_hour
    
    def _get_current_value(self, rule):
        """Récupère la valeur actuelle selon le type d'alerte"""
        alert_type = rule.alert_type
        
        if alert_type == 'cpu':
            return psutil.cpu_percent(interval=1)
        elif alert_type == 'memory':
            return psutil.virtual_memory().percent
        elif alert_type == 'disk':
            return psutil.disk_usage('/').percent
        elif alert_type == 'system':
            return self.monitoring.get_system_health_score()
        elif alert_type == 'database':
            return self.monitoring.get_database_health_score()
        elif alert_type == 'api':
            return self.monitoring.get_api_response_time()
        elif alert_type == 'error':
            return self.monitoring.get_error_rate()
        elif alert_type == 'user':
            return self.monitoring.get_active_users_count()
        elif alert_type == 'security':
            return self.monitoring.get_security_events_count()
        else:
            return None
    
    def _trigger_alert(self, rule, current_value):
        """Déclenche une alerte"""
        # Crée l'alerte
        alert = SystemAlert.objects.create(
            alert_rule=rule,
            title=f"Alerte {rule.name}",
            message=self._generate_alert_message(rule, current_value),
            current_value=current_value,
            threshold_value=rule.threshold_value,
            severity=rule.severity,
            context_data={
                'comparison_operator': rule.comparison_operator,
                'check_interval': rule.check_interval,
                'cooldown_period': rule.cooldown_period,
            }
        )
        
        # Envoie les notifications
        self._send_notifications(alert, rule)
        
        return alert
    
    def _generate_alert_message(self, rule, current_value):
        """Génère le message d'alerte"""
        operator_text = {
            '>': 'supérieur à',
            '>=': 'supérieur ou égal à',
            '<': 'inférieur à',
            '<=': 'inférieur ou égal à',
            '==': 'égal à',
            '!=': 'différent de',
        }
        
        operator = operator_text.get(rule.comparison_operator, rule.comparison_operator)
        
        return (
            f"Alerte {rule.get_alert_type_display()}: "
            f"La valeur actuelle ({current_value}) est {operator} "
            f"la valeur seuil ({rule.threshold_value}). "
            f"Sévérité: {rule.get_severity_display()}"
        )
    
    def _send_notifications(self, alert, rule):
        """Envoie les notifications pour une alerte"""
        from .notification_service import NotificationService
        notification_service = NotificationService()
        
        for channel_config in rule.notification_channels:
            try:
                notification = AlertNotification.objects.create(
                    alert=alert,
                    channel_type=channel_config['type'],
                    recipient=channel_config['recipient'],
                    subject=f"Alerte {alert.severity.upper()}: {alert.title}",
                    message=alert.message
                )
                
                # Envoie la notification
                success = notification_service.send_alert_notification(notification)
                
                if success:
                    notification.status = 'sent'
                    notification.sent_at = timezone.now()
                else:
                    notification.status = 'failed'
                
                notification.save()
                
            except Exception as e:
                print(f"Erreur lors de l'envoi de notification: {e}")
    
    def acknowledge_alert(self, alert, user):
        """Reconnaît une alerte"""
        alert.acknowledge(user)
        
        # Log de l'action
        from apps.admin_api.models import AdminLog
        AdminLog.objects.create(
            admin_user=user,
            action='alert_acknowledge',
            target_model='SystemAlert',
            target_id=str(alert.id),
            message=f'Alerte reconnue: {alert.title}',
            level='info'
        )
    
    def resolve_alert(self, alert, user):
        """Résout une alerte"""
        alert.resolve(user)
        
        # Log de l'action
        from apps.admin_api.models import AdminLog
        AdminLog.objects.create(
            admin_user=user,
            action='alert_resolve',
            target_model='SystemAlert',
            target_id=str(alert.id),
            message=f'Alerte résolue: {alert.title}',
            level='info'
        )
    
    def get_alert_statistics(self):
        """Récupère les statistiques des alertes"""
        from django.db.models import Count
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = {
            'total_alerts': SystemAlert.objects.count(),
            'active_alerts': SystemAlert.objects.filter(status='triggered').count(),
            'acknowledged_alerts': SystemAlert.objects.filter(status='acknowledged').count(),
            'resolved_alerts': SystemAlert.objects.filter(status='resolved').count(),
            'alerts_24h': SystemAlert.objects.filter(triggered_at__gte=last_24h).count(),
            'alerts_7d': SystemAlert.objects.filter(triggered_at__gte=last_7d).count(),
            'alerts_by_severity': list(
                SystemAlert.objects.values('severity')
                .annotate(count=Count('id'))
                .order_by('severity')
            ),
            'alerts_by_type': list(
                SystemAlert.objects.values('alert_rule__alert_type')
                .annotate(count=Count('id'))
                .order_by('alert_rule__alert_type')
            ),
        }
        
        return stats



