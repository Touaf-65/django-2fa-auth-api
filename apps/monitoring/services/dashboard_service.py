"""
Service de gestion des tableaux de bord
"""
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Avg, Sum
from apps.monitoring.models import Dashboard, DashboardWidget


class DashboardService:
    """Service pour la gestion des tableaux de bord"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def create_dashboard(self, name, owner, description='', **kwargs):
        """Crée un nouveau tableau de bord"""
        dashboard = Dashboard.objects.create(
            name=name,
            description=description,
            owner=owner,
            visibility=kwargs.get('visibility', 'private'),
            is_active=kwargs.get('is_active', True),
            refresh_interval=kwargs.get('refresh_interval', 30),
            layout_config=kwargs.get('layout_config', {}),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {}),
        )
        
        return dashboard
    
    def get_dashboard(self, dashboard_id, user=None):
        """Récupère un tableau de bord"""
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            
            # Vérifier les permissions
            if dashboard.is_private and user != dashboard.owner:
                return None
            
            return dashboard
        except Dashboard.DoesNotExist:
            return None
    
    def get_user_dashboards(self, user, include_shared=True):
        """Récupère les tableaux de bord d'un utilisateur"""
        queryset = Dashboard.objects.filter(owner=user, is_active=True)
        
        if include_shared:
            # Ajouter les tableaux de bord partagés
            shared_dashboards = Dashboard.objects.filter(
                visibility__in=['shared', 'public'],
                is_active=True
            ).exclude(owner=user)
            queryset = queryset.union(shared_dashboards)
        
        return queryset.order_by('-created_at')
    
    def get_public_dashboards(self):
        """Récupère les tableaux de bord publics"""
        return Dashboard.objects.filter(
            visibility='public',
            is_active=True
        ).order_by('-created_at')
    
    def add_widget(self, dashboard, widget_type, title, config, position=None, **kwargs):
        """Ajoute un widget à un tableau de bord"""
        if position is None:
            position = dashboard.widgets.count()
        
        widget = DashboardWidget.objects.create(
            dashboard=dashboard,
            widget_type=widget_type,
            title=title,
            description=kwargs.get('description', ''),
            config=config,
            position=position,
            size=kwargs.get('size', {'width': 6, 'height': 4}),
            is_active=kwargs.get('is_active', True),
            metadata=kwargs.get('metadata', {}),
        )
        
        return widget
    
    def update_widget(self, widget, **kwargs):
        """Met à jour un widget"""
        for key, value in kwargs.items():
            if hasattr(widget, key):
                setattr(widget, key, value)
        
        widget.save()
        return widget
    
    def remove_widget(self, widget):
        """Supprime un widget"""
        # Réorganiser les positions des autres widgets
        dashboard = widget.dashboard
        widgets = dashboard.widgets.filter(position__gt=widget.position)
        
        for w in widgets:
            w.position -= 1
            w.save()
        
        widget.delete()
    
    def reorder_widgets(self, dashboard, widget_positions):
        """Réorganise les widgets d'un tableau de bord"""
        for widget_id, new_position in widget_positions.items():
            try:
                widget = dashboard.widgets.get(id=widget_id)
                widget.move_to_position(new_position)
            except DashboardWidget.DoesNotExist:
                continue
    
    def get_dashboard_data(self, dashboard):
        """Récupère les données d'un tableau de bord"""
        cache_key = f'dashboard_data_{dashboard.id}'
        data = cache.get(cache_key)
        
        if data is None:
            widgets = dashboard.get_widgets()
            data = {
                'dashboard': {
                    'id': dashboard.id,
                    'name': dashboard.name,
                    'description': dashboard.description,
                    'refresh_interval': dashboard.refresh_interval,
                    'created_at': dashboard.created_at.isoformat(),
                },
                'widgets': []
            }
            
            for widget in widgets:
                widget_data = self._get_widget_data(widget)
                data['widgets'].append(widget_data)
            
            cache.set(cache_key, data, self.cache_timeout)
        
        return data
    
    def _get_widget_data(self, widget):
        """Récupère les données d'un widget"""
        widget_data = {
            'id': widget.id,
            'type': widget.widget_type,
            'title': widget.title,
            'description': widget.description,
            'position': widget.position,
            'size': widget.get_size(),
            'config': widget.config,
            'data': None,
        }
        
        # Générer les données selon le type de widget
        if widget.widget_type == 'metric':
            widget_data['data'] = self._get_metric_widget_data(widget)
        elif widget.widget_type == 'chart':
            widget_data['data'] = self._get_chart_widget_data(widget)
        elif widget.widget_type == 'table':
            widget_data['data'] = self._get_table_widget_data(widget)
        elif widget.widget_type == 'alert':
            widget_data['data'] = self._get_alert_widget_data(widget)
        elif widget.widget_type == 'log':
            widget_data['data'] = self._get_log_widget_data(widget)
        elif widget.widget_type == 'health':
            widget_data['data'] = self._get_health_widget_data(widget)
        
        return widget_data
    
    def _get_metric_widget_data(self, widget):
        """Génère les données pour un widget de métrique"""
        from apps.monitoring.services import MetricsService
        
        metrics_service = MetricsService()
        config = widget.config
        
        metric_name = config.get('metric_name')
        if not metric_name:
            return None
        
        # Récupérer la dernière valeur
        metric_value = metrics_service.get_metric_value(metric_name)
        if not metric_value:
            return None
        
        return {
            'value': metric_value.value,
            'timestamp': metric_value.timestamp.isoformat(),
            'labels': metric_value.labels,
            'metadata': metric_value.metadata,
        }
    
    def _get_chart_widget_data(self, widget):
        """Génère les données pour un widget de graphique"""
        from apps.monitoring.services import MetricsService
        from datetime import timedelta
        
        metrics_service = MetricsService()
        config = widget.config
        
        metric_name = config.get('metric_name')
        hours = config.get('hours', 24)
        
        if not metric_name:
            return None
        
        end_time = timezone.now()
        start_time = end_time - timedelta(hours=hours)
        
        values = metrics_service.get_metric_values(metric_name, start_time, end_time)
        
        return {
            'chart_type': config.get('chart_type', 'line'),
            'data': [
                {
                    'timestamp': v.timestamp.isoformat(),
                    'value': v.value,
                    'labels': v.labels,
                }
                for v in values.order_by('timestamp')
            ],
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
            }
        }
    
    def _get_table_widget_data(self, widget):
        """Génère les données pour un widget de tableau"""
        from apps.monitoring.services import LoggingService
        
        logging_service = LoggingService()
        config = widget.config
        
        level = config.get('level')
        source = config.get('source')
        hours = config.get('hours', 24)
        limit = config.get('limit', 50)
        
        logs = logging_service.get_logs(
            level=level,
            source=source,
            hours=hours,
            limit=limit
        )
        
        return {
            'columns': ['timestamp', 'level', 'source', 'message'],
            'data': [
                {
                    'timestamp': log.created_at.isoformat(),
                    'level': log.level,
                    'source': log.source,
                    'message': log.message[:100] + '...' if len(log.message) > 100 else log.message,
                }
                for log in logs
            ]
        }
    
    def _get_alert_widget_data(self, widget):
        """Génère les données pour un widget d'alerte"""
        from apps.monitoring.services import AlertService
        
        alert_service = AlertService()
        config = widget.config
        
        severity = config.get('severity')
        limit = config.get('limit', 10)
        
        alerts = alert_service.get_active_alerts(severity=severity)[:limit]
        
        return {
            'alerts': [
                {
                    'id': alert.id,
                    'rule_name': alert.rule.name,
                    'severity': alert.severity,
                    'message': alert.message,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'created_at': alert.created_at.isoformat(),
                }
                for alert in alerts
            ]
        }
    
    def _get_log_widget_data(self, widget):
        """Génère les données pour un widget de log"""
        from apps.monitoring.services import LoggingService
        
        logging_service = LoggingService()
        config = widget.config
        
        query = config.get('query', '')
        level = config.get('level')
        source = config.get('source')
        hours = config.get('hours', 24)
        limit = config.get('limit', 20)
        
        if query:
            logs = logging_service.search_logs(
                query=query,
                level=level,
                source=source,
                hours=hours,
                limit=limit
            )
        else:
            logs = logging_service.get_logs(
                level=level,
                source=source,
                hours=hours,
                limit=limit
            )
        
        return {
            'logs': [
                {
                    'id': log.id,
                    'level': log.level,
                    'source': log.source,
                    'message': log.message,
                    'timestamp': log.created_at.isoformat(),
                    'user': log.user.email if log.user else None,
                }
                for log in logs
            ]
        }
    
    def _get_health_widget_data(self, widget):
        """Génère les données pour un widget de santé"""
        from apps.monitoring.services import HealthService
        
        health_service = HealthService()
        config = widget.config
        
        check_type = config.get('check_type')
        
        if check_type:
            # Données pour un type de vérification spécifique
            try:
                from apps.monitoring.models import HealthCheck
                health_check = HealthCheck.objects.get(check_type=check_type)
                latest_result = health_check.get_latest_result()
                
                if latest_result:
                    return {
                        'check_type': check_type,
                        'status': latest_result.status,
                        'message': latest_result.message,
                        'response_time': latest_result.response_time,
                        'timestamp': latest_result.created_at.isoformat(),
                    }
            except HealthCheck.DoesNotExist:
                pass
        
        # Données de santé générale
        system_health = health_service.get_system_health()
        
        return {
            'overall_status': system_health.status,
            'overall_score': system_health.overall_score,
            'components': {
                'database': system_health.database_status,
                'cache': system_health.cache_status,
                'storage': system_health.storage_status,
                'external_services': system_health.external_services_status,
            },
            'issues': system_health.issues,
            'recommendations': system_health.recommendations,
            'timestamp': system_health.created_at.isoformat(),
        }
    
    def get_dashboard_statistics(self):
        """Récupère les statistiques des tableaux de bord"""
        cache_key = 'dashboard_statistics'
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = {
                'total_dashboards': Dashboard.objects.count(),
                'active_dashboards': Dashboard.objects.filter(is_active=True).count(),
                'public_dashboards': Dashboard.objects.filter(visibility='public').count(),
                'shared_dashboards': Dashboard.objects.filter(visibility='shared').count(),
                'private_dashboards': Dashboard.objects.filter(visibility='private').count(),
                'total_widgets': DashboardWidget.objects.count(),
                'active_widgets': DashboardWidget.objects.filter(is_active=True).count(),
                'widgets_by_type': list(
                    DashboardWidget.objects.values('widget_type')
                    .annotate(count=Count('id'))
                    .order_by('widget_type')
                ),
            }
            
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def clone_dashboard(self, source_dashboard, new_name, new_owner):
        """Clone un tableau de bord"""
        # Créer le nouveau tableau de bord
        new_dashboard = Dashboard.objects.create(
            name=new_name,
            description=f"Clone of {source_dashboard.name}",
            owner=new_owner,
            visibility='private',  # Toujours privé pour les clones
            is_active=True,
            refresh_interval=source_dashboard.refresh_interval,
            layout_config=source_dashboard.layout_config,
            tags=source_dashboard.tags,
            metadata=source_dashboard.metadata,
        )
        
        # Cloner les widgets
        for widget in source_dashboard.widgets.filter(is_active=True):
            DashboardWidget.objects.create(
                dashboard=new_dashboard,
                widget_type=widget.widget_type,
                title=widget.title,
                description=widget.description,
                config=widget.config,
                position=widget.position,
                size=widget.size,
                is_active=True,
                metadata=widget.metadata,
            )
        
        return new_dashboard



