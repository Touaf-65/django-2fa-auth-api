"""
URLs pour le Monitoring App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Log Views
    LogEntryListCreateView, LogEntryRetrieveView, LogEntrySearchView,
    log_statistics_view, log_export_view, log_create_view,
    
    # Metric Views
    MetricListCreateView, MetricRetrieveUpdateView, MetricValueListCreateView,
    record_metric_view, increment_counter_view, set_gauge_view,
    metric_statistics_view, metric_value_statistics_view, metric_export_view,
    
    # Alert Views
    AlertRuleListCreateView, AlertRuleRetrieveUpdateView, AlertListCreateView,
    AlertRetrieveView, acknowledge_alert_view, resolve_alert_view,
    active_alerts_view, alert_statistics_view, alert_trends_view,
    create_alert_rule_view, test_alert_rule_view, AlertNotificationListView,
    
    # Performance Views
    PerformanceMetricListCreateView, PerformanceMetricRetrieveUpdateView,
    PerformanceReportListCreateView, PerformanceReportRetrieveView,
    record_response_time_view, record_throughput_view, record_error_rate_view,
    performance_summary_view, performance_trends_view, slow_endpoints_view,
    error_endpoints_view, generate_performance_report_view, performance_statistics_view,
    
    # Health Views
    SystemHealthListView, SystemHealthRetrieveView, HealthCheckListCreateView,
    HealthCheckRetrieveUpdateView, HealthCheckResultListView,
    current_system_health_view, run_health_check_view, run_all_health_checks_view,
    health_statistics_view, database_health_view, cache_health_view,
    storage_health_view, external_services_health_view, health_check_success_rate_view,
    health_check_latest_result_view,
    
    # Dashboard Views
    DashboardListCreateView, DashboardRetrieveUpdateView, DashboardWidgetListCreateView,
    DashboardWidgetRetrieveUpdateView, dashboard_data_view, add_widget_view,
    reorder_widgets_view, clone_dashboard_view, user_dashboards_view,
    public_dashboards_view, dashboard_statistics_view, widget_data_view,
)

app_name = 'monitoring'

urlpatterns = [
    # Log URLs
    path('logs/', LogEntryListCreateView.as_view(), name='log-list-create'),
    path('logs/<int:pk>/', LogEntryRetrieveView.as_view(), name='log-retrieve'),
    path('logs/search/', LogEntrySearchView.as_view(), name='log-search'),
    path('logs/statistics/', log_statistics_view, name='log-statistics'),
    path('logs/export/', log_export_view, name='log-export'),
    path('logs/create/', log_create_view, name='log-create'),
    
    # Metric URLs
    path('metrics/', MetricListCreateView.as_view(), name='metric-list-create'),
    path('metrics/<int:pk>/', MetricRetrieveUpdateView.as_view(), name='metric-retrieve-update'),
    path('metrics/values/', MetricValueListCreateView.as_view(), name='metric-value-list-create'),
    path('metrics/record/', record_metric_view, name='metric-record'),
    path('metrics/counter/increment/', increment_counter_view, name='metric-counter-increment'),
    path('metrics/gauge/set/', set_gauge_view, name='metric-gauge-set'),
    path('metrics/statistics/', metric_statistics_view, name='metric-statistics'),
    path('metrics/<str:metric_name>/statistics/', metric_value_statistics_view, name='metric-value-statistics'),
    path('metrics/export/', metric_export_view, name='metric-export'),
    
    # Alert URLs
    path('alerts/rules/', AlertRuleListCreateView.as_view(), name='alert-rule-list-create'),
    path('alerts/rules/<int:pk>/', AlertRuleRetrieveUpdateView.as_view(), name='alert-rule-retrieve-update'),
    path('alerts/rules/create/', create_alert_rule_view, name='alert-rule-create'),
    path('alerts/rules/<int:rule_id>/test/', test_alert_rule_view, name='alert-rule-test'),
    
    path('alerts/', AlertListCreateView.as_view(), name='alert-list-create'),
    path('alerts/<int:pk>/', AlertRetrieveView.as_view(), name='alert-retrieve'),
    path('alerts/<int:alert_id>/acknowledge/', acknowledge_alert_view, name='alert-acknowledge'),
    path('alerts/<int:alert_id>/resolve/', resolve_alert_view, name='alert-resolve'),
    path('alerts/active/', active_alerts_view, name='alert-active'),
    path('alerts/statistics/', alert_statistics_view, name='alert-statistics'),
    path('alerts/trends/', alert_trends_view, name='alert-trends'),
    
    path('alerts/notifications/', AlertNotificationListView.as_view(), name='alert-notification-list'),
    
    # Performance URLs
    path('performance/metrics/', PerformanceMetricListCreateView.as_view(), name='performance-metric-list-create'),
    path('performance/metrics/<int:pk>/', PerformanceMetricRetrieveUpdateView.as_view(), name='performance-metric-retrieve-update'),
    
    path('performance/reports/', PerformanceReportListCreateView.as_view(), name='performance-report-list-create'),
    path('performance/reports/<int:pk>/', PerformanceReportRetrieveView.as_view(), name='performance-report-retrieve'),
    path('performance/reports/generate/', generate_performance_report_view, name='performance-report-generate'),
    
    path('performance/response-time/', record_response_time_view, name='performance-response-time'),
    path('performance/throughput/', record_throughput_view, name='performance-throughput'),
    path('performance/error-rate/', record_error_rate_view, name='performance-error-rate'),
    
    path('performance/summary/', performance_summary_view, name='performance-summary'),
    path('performance/trends/<str:metric_name>/', performance_trends_view, name='performance-trends'),
    path('performance/slow-endpoints/', slow_endpoints_view, name='performance-slow-endpoints'),
    path('performance/error-endpoints/', error_endpoints_view, name='performance-error-endpoints'),
    path('performance/statistics/', performance_statistics_view, name='performance-statistics'),
    
    # Health URLs
    path('health/system/', SystemHealthListView.as_view(), name='system-health-list'),
    path('health/system/<int:pk>/', SystemHealthRetrieveView.as_view(), name='system-health-retrieve'),
    path('health/system/current/', current_system_health_view, name='system-health-current'),
    
    path('health/checks/', HealthCheckListCreateView.as_view(), name='health-check-list-create'),
    path('health/checks/<int:pk>/', HealthCheckRetrieveUpdateView.as_view(), name='health-check-retrieve-update'),
    path('health/checks/<int:health_check_id>/run/', run_health_check_view, name='health-check-run'),
    path('health/checks/<int:health_check_id>/success-rate/', health_check_success_rate_view, name='health-check-success-rate'),
    path('health/checks/<int:health_check_id>/latest-result/', health_check_latest_result_view, name='health-check-latest-result'),
    path('health/checks/run-all/', run_all_health_checks_view, name='health-check-run-all'),
    
    path('health/results/', HealthCheckResultListView.as_view(), name='health-check-result-list'),
    
    path('health/statistics/', health_statistics_view, name='health-statistics'),
    path('health/database/', database_health_view, name='health-database'),
    path('health/cache/', cache_health_view, name='health-cache'),
    path('health/storage/', storage_health_view, name='health-storage'),
    path('health/external-services/', external_services_health_view, name='health-external-services'),
    
    # Dashboard URLs
    path('dashboards/', DashboardListCreateView.as_view(), name='dashboard-list-create'),
    path('dashboards/<int:pk>/', DashboardRetrieveUpdateView.as_view(), name='dashboard-retrieve-update'),
    path('dashboards/<int:dashboard_id>/data/', dashboard_data_view, name='dashboard-data'),
    path('dashboards/<int:dashboard_id>/clone/', clone_dashboard_view, name='dashboard-clone'),
    path('dashboards/user/', user_dashboards_view, name='dashboard-user'),
    path('dashboards/public/', public_dashboards_view, name='dashboard-public'),
    path('dashboards/statistics/', dashboard_statistics_view, name='dashboard-statistics'),
    
    path('dashboards/<int:dashboard_id>/widgets/', add_widget_view, name='dashboard-add-widget'),
    path('dashboards/<int:dashboard_id>/reorder/', reorder_widgets_view, name='dashboard-reorder-widgets'),
    
    path('widgets/', DashboardWidgetListCreateView.as_view(), name='widget-list-create'),
    path('widgets/<int:pk>/', DashboardWidgetRetrieveUpdateView.as_view(), name='widget-retrieve-update'),
    path('widgets/<int:widget_id>/data/', widget_data_view, name='widget-data'),
]
