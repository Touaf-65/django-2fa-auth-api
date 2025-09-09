"""
URLs pour l'app Analytics
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Rapports
    ReportTemplateListCreateView, ReportTemplateDetailView,
    ReportListCreateView, ReportDetailView,
    ReportScheduleListCreateView, ReportScheduleDetailView,
    generate_report, report_data, execute_schedule, report_summary,
    
    # Tableaux de bord
    AnalyticsDashboardListCreateView, AnalyticsDashboardDetailView,
    DashboardWidgetListCreateView, DashboardWidgetDetailView,
    dashboard_data, share_dashboard, update_dashboard_layout,
    widget_data, dashboard_summary, duplicate_dashboard,
    
    # Exports
    ExportFormatListView, DataExportListCreateView, DataExportDetailView,
    process_export, download_export, quick_export, bulk_export,
    export_status, export_summary, cleanup_expired_exports,
    
    # Métriques
    AnalyticsMetricListCreateView, AnalyticsMetricDetailView,
    MetricValueListCreateView, MetricValueDetailView,
    calculate_metric, metric_trend, top_metrics, create_metric,
    update_metric, delete_metric, bulk_update_metrics, metric_summary,
)

app_name = 'analytics'

# URLs pour les rapports
report_urls = [
    # Templates de rapports
    path('templates/', ReportTemplateListCreateView.as_view(), name='report-template-list'),
    path('templates/<int:pk>/', ReportTemplateDetailView.as_view(), name='report-template-detail'),
    
    # Rapports
    path('reports/', ReportListCreateView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:report_id>/generate/', generate_report, name='report-generate'),
    path('reports/<int:report_id>/data/', report_data, name='report-data'),
    path('reports/summary/', report_summary, name='report-summary'),
    
    # Planifications de rapports
    path('schedules/', ReportScheduleListCreateView.as_view(), name='report-schedule-list'),
    path('schedules/<int:pk>/', ReportScheduleDetailView.as_view(), name='report-schedule-detail'),
    path('schedules/<int:schedule_id>/execute/', execute_schedule, name='report-schedule-execute'),
]

# URLs pour les tableaux de bord
dashboard_urls = [
    # Tableaux de bord
    path('dashboards/', AnalyticsDashboardListCreateView.as_view(), name='dashboard-list'),
    path('dashboards/<int:pk>/', AnalyticsDashboardDetailView.as_view(), name='dashboard-detail'),
    path('dashboards/<int:dashboard_id>/data/', dashboard_data, name='dashboard-data'),
    path('dashboards/<int:dashboard_id>/share/', share_dashboard, name='dashboard-share'),
    path('dashboards/<int:dashboard_id>/layout/', update_dashboard_layout, name='dashboard-layout'),
    path('dashboards/<int:dashboard_id>/duplicate/', duplicate_dashboard, name='dashboard-duplicate'),
    path('dashboards/summary/', dashboard_summary, name='dashboard-summary'),
    
    # Widgets
    path('dashboards/<int:dashboard_id>/widgets/', DashboardWidgetListCreateView.as_view(), name='widget-list'),
    path('widgets/<int:pk>/', DashboardWidgetDetailView.as_view(), name='widget-detail'),
    path('widgets/<int:widget_id>/data/', widget_data, name='widget-data'),
]

# URLs pour les exports
export_urls = [
    # Formats d'export
    path('formats/', ExportFormatListView.as_view(), name='export-format-list'),
    
    # Exports de données
    path('exports/', DataExportListCreateView.as_view(), name='export-list'),
    path('exports/<int:pk>/', DataExportDetailView.as_view(), name='export-detail'),
    path('exports/<int:export_id>/process/', process_export, name='export-process'),
    path('exports/<int:export_id>/download/', download_export, name='export-download'),
    path('exports/<int:export_id>/status/', export_status, name='export-status'),
    path('exports/summary/', export_summary, name='export-summary'),
    path('exports/cleanup/', cleanup_expired_exports, name='export-cleanup'),
    
    # Exports rapides
    path('quick-export/', quick_export, name='quick-export'),
    path('bulk-export/', bulk_export, name='bulk-export'),
]

# URLs pour les métriques
metric_urls = [
    # Métriques
    path('metrics/', AnalyticsMetricListCreateView.as_view(), name='metric-list'),
    path('metrics/<int:pk>/', AnalyticsMetricDetailView.as_view(), name='metric-detail'),
    path('metrics/create/', create_metric, name='metric-create'),
    path('metrics/<str:metric_name>/update/', update_metric, name='metric-update'),
    path('metrics/<str:metric_name>/delete/', delete_metric, name='metric-delete'),
    path('metrics/bulk-update/', bulk_update_metrics, name='metric-bulk-update'),
    path('metrics/summary/', metric_summary, name='metric-summary'),
    
    # Calculs de métriques
    path('metrics/<str:metric_name>/calculate/', calculate_metric, name='metric-calculate'),
    path('metrics/<str:metric_name>/trend/', metric_trend, name='metric-trend'),
    path('metrics/top/', top_metrics, name='metric-top'),
    
    # Valeurs de métriques
    path('values/', MetricValueListCreateView.as_view(), name='metric-value-list'),
    path('values/<int:pk>/', MetricValueDetailView.as_view(), name='metric-value-detail'),
]

urlpatterns = [
    # Rapports
    path('reports/', include(report_urls)),
    
    # Tableaux de bord
    path('dashboards/', include(dashboard_urls)),
    
    # Exports
    path('exports/', include(export_urls)),
    
    # Métriques
    path('metrics/', include(metric_urls)),
]

