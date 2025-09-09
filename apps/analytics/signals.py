"""
Signals pour l'app Analytics
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.analytics.models import Report, ReportSchedule, AnalyticsDashboard, AnalyticsMetric
from apps.analytics.services import AnalyticsService

User = get_user_model()


@receiver(post_save, sender=Report)
def report_created(sender, instance, created, **kwargs):
    """Signal déclenché lors de la création d'un rapport"""
    if created:
        # Log de création de rapport
        from apps.monitoring.services import LoggingService
        logging_service = LoggingService()
        
        logging_service.info(
            f"Rapport créé: {instance.name}",
            source='analytics',
            metadata={
                'report_id': instance.id,
                'report_type': instance.report_type,
                'template_id': instance.template.id if instance.template else None,
            }
        )


@receiver(post_save, sender=ReportSchedule)
def report_schedule_created(sender, instance, created, **kwargs):
    """Signal déclenché lors de la création d'une planification de rapport"""
    if created:
        # Log de création de planification
        from apps.monitoring.services import LoggingService
        logging_service = LoggingService()
        
        logging_service.info(
            f"Planification de rapport créée: {instance.name}",
            source='analytics',
            metadata={
                'schedule_id': instance.id,
                'frequency': instance.frequency,
                'template_id': instance.template.id,
            }
        )


@receiver(post_save, sender=AnalyticsDashboard)
def dashboard_created(sender, instance, created, **kwargs):
    """Signal déclenché lors de la création d'un tableau de bord"""
    if created:
        # Log de création de tableau de bord
        from apps.monitoring.services import LoggingService
        logging_service = LoggingService()
        
        logging_service.info(
            f"Tableau de bord créé: {instance.name}",
            source='analytics',
            metadata={
                'dashboard_id': instance.id,
                'dashboard_type': instance.dashboard_type,
                'is_public': instance.is_public,
            }
        )


@receiver(post_save, sender=AnalyticsMetric)
def metric_created(sender, instance, created, **kwargs):
    """Signal déclenché lors de la création d'une métrique"""
    if created:
        # Log de création de métrique
        from apps.monitoring.services import LoggingService
        logging_service = LoggingService()
        
        logging_service.info(
            f"Métrique créée: {instance.name}",
            source='analytics',
            metadata={
                'metric_id': instance.id,
                'metric_type': instance.metric_type,
                'category': instance.category,
            }
        )


@receiver(pre_delete, sender=Report)
def report_deleted(sender, instance, **kwargs):
    """Signal déclenché avant la suppression d'un rapport"""
    # Log de suppression de rapport
    from apps.monitoring.services import LoggingService
    logging_service = LoggingService()
    
    logging_service.warning(
        f"Rapport supprimé: {instance.name}",
        source='analytics',
        metadata={
            'report_id': instance.id,
            'report_type': instance.report_type,
            'status': instance.status,
        }
    )


@receiver(pre_delete, sender=AnalyticsDashboard)
def dashboard_deleted(sender, instance, **kwargs):
    """Signal déclenché avant la suppression d'un tableau de bord"""
    # Log de suppression de tableau de bord
    from apps.monitoring.services import LoggingService
    logging_service = LoggingService()
    
    logging_service.warning(
        f"Tableau de bord supprimé: {instance.name}",
        source='analytics',
        metadata={
            'dashboard_id': instance.id,
            'dashboard_type': instance.dashboard_type,
            'view_count': instance.view_count,
        }
    )

