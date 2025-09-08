"""
Signals pour le Monitoring App
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.monitoring.models import LogEntry, Metric, Alert, SystemHealth
from apps.monitoring.services import LoggingService, MetricsService, AlertService

User = get_user_model()


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """Log la création d'un utilisateur"""
    if created:
        logging_service = LoggingService()
        logging_service.info(
            f"User created: {instance.email}",
            source='user',
            user=instance,
            metadata={
                'user_id': instance.id,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
            }
        )


@receiver(post_save, sender=LogEntry)
def log_entry_created(sender, instance, created, **kwargs):
    """Log la création d'une entrée de log"""
    if created and instance.is_error:
        # Envoyer une alerte pour les erreurs critiques
        if instance.level == 'CRITICAL':
            logging_service = LoggingService()
            logging_service.critical(
                f"Critical log entry created: {instance.message}",
                source='monitoring',
                metadata={
                    'log_entry_id': instance.id,
                    'original_message': instance.message,
                    'original_source': instance.source,
                }
            )


@receiver(post_save, sender=Metric)
def metric_created(sender, instance, created, **kwargs):
    """Log la création d'une métrique"""
    if created:
        logging_service = LoggingService()
        logging_service.info(
            f"Metric created: {instance.name}",
            source='monitoring',
            metadata={
                'metric_id': instance.id,
                'metric_name': instance.name,
                'metric_type': instance.metric_type,
                'unit': instance.unit,
            }
        )


@receiver(post_save, sender=Alert)
def alert_created(sender, instance, created, **kwargs):
    """Log la création d'une alerte"""
    if created:
        logging_service = LoggingService()
        logging_service.warning(
            f"Alert created: {instance.rule.name}",
            source='monitoring',
            metadata={
                'alert_id': instance.id,
                'rule_name': instance.rule.name,
                'severity': instance.severity,
                'value': instance.value,
                'threshold': instance.threshold,
            }
        )


@receiver(post_save, sender=SystemHealth)
def system_health_updated(sender, instance, created, **kwargs):
    """Log la mise à jour de la santé du système"""
    if not created:  # Mise à jour uniquement
        logging_service = LoggingService()
        
        if instance.status == 'unhealthy':
            logging_service.critical(
                f"System health degraded to unhealthy: {instance.overall_score}%",
                source='monitoring',
                metadata={
                    'system_health_id': instance.id,
                    'overall_score': instance.overall_score,
                    'status': instance.status,
                    'issues': instance.issues,
                }
            )
        elif instance.status == 'degraded':
            logging_service.warning(
                f"System health degraded: {instance.overall_score}%",
                source='monitoring',
                metadata={
                    'system_health_id': instance.id,
                    'overall_score': instance.overall_score,
                    'status': instance.status,
                    'issues': instance.issues,
                }
            )
