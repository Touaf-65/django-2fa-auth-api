"""
Service pour la génération de rapports Analytics
"""
import json
import time
from datetime import datetime, timedelta
from django.db import connection
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from apps.analytics.models import Report, ReportTemplate, ReportSchedule
from apps.monitoring.models import LogEntry, MetricValue
from apps.authentication.models import User
from apps.security.models import SecurityEvent

User = get_user_model()


class ReportService:
    """Service pour la génération et gestion des rapports"""
    
    def __init__(self):
        self.templates = {
            'user_activity': self._generate_user_activity_report,
            'security_audit': self._generate_security_audit_report,
            'performance': self._generate_performance_report,
            'usage': self._generate_usage_report,
        }
    
    def generate_report(self, report_id, user=None):
        """Génère un rapport"""
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'generating'
            report.save()
            
            start_time = time.time()
            
            # Générer le rapport selon son type
            if report.report_type in self.templates:
                data = self.templates[report.report_type](report)
            else:
                data = self._generate_custom_report(report)
            
            # Calculer le temps d'exécution
            execution_time = time.time() - start_time
            
            # Sauvegarder les résultats
            report.data = data
            report.summary = self._generate_summary(data, report.report_type)
            report.status = 'completed'
            report.generated_at = timezone.now()
            report.execution_time = execution_time
            report.save()
            
            return report
            
        except Exception as e:
            if 'report' in locals():
                report.status = 'failed'
                report.error_message = str(e)
                report.save()
            raise e
    
    def _generate_user_activity_report(self, report):
        """Génère un rapport d'activité utilisateur"""
        filters = report.filters or {}
        start_date = report.date_range_start or timezone.now() - timedelta(days=30)
        end_date = report.date_range_end or timezone.now()
        
        # Statistiques des utilisateurs
        user_stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(
                last_login__gte=start_date,
                last_login__lte=end_date
            ).count(),
            'new_users': User.objects.filter(
                date_joined__gte=start_date,
                date_joined__lte=end_date
            ).count(),
        }
        
        # Activité par jour
        daily_activity = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
            
            daily_logs = LogEntry.objects.filter(
                created_at__gte=day_start,
                created_at__lte=day_end,
                source='api'
            ).count()
            
            daily_activity.append({
                'date': current_date.isoformat(),
                'activity_count': daily_logs
            })
            
            current_date += timedelta(days=1)
        
        # Top utilisateurs actifs
        top_users = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            user__isnull=False
        ).values('user__email', 'user__first_name', 'user__last_name').annotate(
            activity_count=models.Count('id')
        ).order_by('-activity_count')[:10]
        
        return {
            'user_stats': user_stats,
            'daily_activity': daily_activity,
            'top_users': list(top_users),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _generate_security_audit_report(self, report):
        """Génère un rapport d'audit sécurité"""
        filters = report.filters or {}
        start_date = report.date_range_start or timezone.now() - timedelta(days=7)
        end_date = report.date_range_end or timezone.now()
        
        # Événements de sécurité
        security_events = SecurityEvent.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Statistiques par type d'événement
        event_stats = {}
        for event in security_events:
            event_type = event.event_type
            if event_type not in event_stats:
                event_stats[event_type] = 0
            event_stats[event_type] += 1
        
        # Tentatives de connexion échouées
        failed_logins = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            source='auth',
            level='WARNING'
        ).count()
        
        # IPs suspectes
        suspicious_ips = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            source='security',
            level__in=['WARNING', 'ERROR']
        ).values('ip_address').annotate(
            count=models.Count('id')
        ).filter(count__gte=5).order_by('-count')[:10]
        
        return {
            'event_stats': event_stats,
            'failed_logins': failed_logins,
            'suspicious_ips': list(suspicious_ips),
            'total_events': security_events.count(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _generate_performance_report(self, report):
        """Génère un rapport de performance"""
        filters = report.filters or {}
        start_date = report.date_range_start or timezone.now() - timedelta(days=7)
        end_date = report.date_range_end or timezone.now()
        
        # Métriques de performance
        performance_metrics = MetricValue.objects.filter(
            metric__name__in=['api_response_time', 'db_queries_time', 'api_requests_total'],
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        # Temps de réponse moyen
        avg_response_time = performance_metrics.filter(
            metric__name='api_response_time'
        ).aggregate(avg=models.Avg('value'))['avg'] or 0
        
        # Requêtes DB moyennes
        avg_db_time = performance_metrics.filter(
            metric__name='db_queries_time'
        ).aggregate(avg=models.Avg('value'))['avg'] or 0
        
        # Volume de requêtes
        total_requests = performance_metrics.filter(
            metric__name='api_requests_total'
        ).aggregate(total=models.Sum('value'))['total'] or 0
        
        # Endpoints les plus lents
        slow_endpoints = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            source='api',
            response_time__isnull=False
        ).values('path').annotate(
            avg_time=models.Avg('response_time'),
            count=models.Count('id')
        ).order_by('-avg_time')[:10]
        
        return {
            'avg_response_time': round(avg_response_time, 3),
            'avg_db_time': round(avg_db_time, 3),
            'total_requests': total_requests,
            'slow_endpoints': list(slow_endpoints),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _generate_usage_report(self, report):
        """Génère un rapport d'utilisation"""
        filters = report.filters or {}
        start_date = report.date_range_start or timezone.now() - timedelta(days=30)
        end_date = report.date_range_end or timezone.now()
        
        # Utilisation par endpoint
        endpoint_usage = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            source='api'
        ).values('path', 'method').annotate(
            count=models.Count('id'),
            avg_response_time=models.Avg('response_time')
        ).order_by('-count')[:20]
        
        # Utilisation par utilisateur
        user_usage = LogEntry.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            user__isnull=False
        ).values('user__email').annotate(
            count=models.Count('id')
        ).order_by('-count')[:20]
        
        # Heures de pointe
        hourly_usage = []
        for hour in range(24):
            hour_start = start_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            count = LogEntry.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end,
                source='api'
            ).count()
            
            hourly_usage.append({
                'hour': hour,
                'count': count
            })
        
        return {
            'endpoint_usage': list(endpoint_usage),
            'user_usage': list(user_usage),
            'hourly_usage': hourly_usage,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    def _generate_custom_report(self, report):
        """Génère un rapport personnalisé"""
        # Implémentation pour les rapports personnalisés
        return {
            'message': 'Rapport personnalisé généré',
            'config': report.config,
            'filters': report.filters
        }
    
    def _generate_summary(self, data, report_type):
        """Génère un résumé du rapport"""
        if report_type == 'user_activity':
            return {
                'total_users': data.get('user_stats', {}).get('total_users', 0),
                'active_users': data.get('user_stats', {}).get('active_users', 0),
                'new_users': data.get('user_stats', {}).get('new_users', 0),
            }
        elif report_type == 'security_audit':
            return {
                'total_events': data.get('total_events', 0),
                'failed_logins': data.get('failed_logins', 0),
                'suspicious_ips': len(data.get('suspicious_ips', [])),
            }
        elif report_type == 'performance':
            return {
                'avg_response_time': data.get('avg_response_time', 0),
                'total_requests': data.get('total_requests', 0),
                'slow_endpoints': len(data.get('slow_endpoints', [])),
            }
        elif report_type == 'usage':
            return {
                'total_endpoints': len(data.get('endpoint_usage', [])),
                'total_users': len(data.get('user_usage', [])),
                'peak_hour': max(data.get('hourly_usage', []), key=lambda x: x['count'])['hour'] if data.get('hourly_usage') else 0,
            }
        
        return {'message': 'Résumé généré'}
    
    def schedule_report(self, schedule_id):
        """Exécute un rapport planifié"""
        try:
            schedule = ReportSchedule.objects.get(id=schedule_id)
            
            # Créer un nouveau rapport basé sur le template
            report = Report.objects.create(
                name=f"{schedule.template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                template=schedule.template,
                report_type=schedule.template.report_type,
                generated_by=schedule.created_by,
                status='pending'
            )
            
            # Générer le rapport
            self.generate_report(report.id)
            
            # Mettre à jour la planification
            schedule.last_run = timezone.now()
            schedule.last_status = report.status
            schedule.total_runs += 1
            if report.status == 'completed':
                schedule.successful_runs += 1
            schedule.save()
            
            # Envoyer notification si activée
            if schedule.notification_enabled and schedule.recipients:
                self._send_report_notification(report, schedule.recipients)
            
            return report
            
        except Exception as e:
            if 'schedule' in locals():
                schedule.last_status = 'failed'
                schedule.save()
            raise e
    
    def _send_report_notification(self, report, recipients):
        """Envoie une notification de rapport"""
        subject = f"Rapport généré: {report.name}"
        message = f"""
        Le rapport "{report.name}" a été généré avec succès.
        
        Statut: {report.get_status_display()}
        Généré le: {report.generated_at}
        Temps d'exécution: {report.execution_time}s
        
        Vous pouvez consulter le rapport dans l'interface d'administration.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True
        )
