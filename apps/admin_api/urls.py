"""
URLs pour l'Admin API
"""
from django.urls import path, include
from .views import (
    # AdminAction views
    AdminActionListAPIView,
    AdminActionCreateAPIView,
    AdminActionRetrieveAPIView,
    AdminActionUpdateAPIView,
    AdminActionDestroyAPIView,
    admin_action_stats,
    
    # AdminLog views
    AdminLogListAPIView,
    AdminLogRetrieveAPIView,
    admin_log_stats,
    
    # SystemConfig views
    SystemConfigListAPIView,
    SystemConfigCreateAPIView,
    SystemConfigRetrieveAPIView,
    SystemConfigUpdateAPIView,
    SystemConfigDestroyAPIView,
    
    # AdminDashboard views
    AdminDashboardListAPIView,
    AdminDashboardRetrieveAPIView,
    admin_dashboard_stats,
    
    # AdminReport views
    AdminReportListAPIView,
    AdminReportCreateAPIView,
    AdminReportRetrieveAPIView,
    admin_report_generate,
    
    # AdminUser views
    AdminUserListAPIView,
    AdminUserCreateAPIView,
    AdminUserRetrieveAPIView,
    AdminUserUpdateAPIView,
    admin_user_activate,
    admin_user_deactivate,
    admin_user_suspend,
    admin_user_stats,
    
    # AdminSystem views
    admin_system_info,
    admin_system_health,
    admin_system_backup,
    admin_system_cache_clear,
    admin_system_maintenance,
    
    # Alert views
    AlertRuleListAPIView,
    AlertRuleCreateAPIView,
    AlertRuleRetrieveAPIView,
    AlertRuleUpdateAPIView,
    AlertRuleDestroyAPIView,
    SystemAlertListAPIView,
    SystemAlertRetrieveAPIView,
    acknowledge_alert,
    resolve_alert,
    alert_statistics,
    check_alerts,
    AlertNotificationListAPIView,
    AlertNotificationRetrieveAPIView,
    system_metrics,
    system_health,
    
    # Report views
    ReportTemplateListAPIView,
    ReportTemplateCreateAPIView,
    ReportTemplateRetrieveAPIView,
    ReportTemplateUpdateAPIView,
    ReportTemplateDestroyAPIView,
    ScheduledReportListAPIView,
    ScheduledReportCreateAPIView,
    ScheduledReportRetrieveAPIView,
    ScheduledReportUpdateAPIView,
    ScheduledReportDestroyAPIView,
    execute_scheduled_report,
    generate_report,
    ReportExecutionListAPIView,
    ReportExecutionRetrieveAPIView,
    report_statistics,
)

app_name = 'admin_api'

urlpatterns = [
    # Admin Actions
    path('actions/', AdminActionListAPIView.as_view(), name='action-list'),
    path('actions/create/', AdminActionCreateAPIView.as_view(), name='action-create'),
    path('actions/<uuid:pk>/', AdminActionRetrieveAPIView.as_view(), name='action-retrieve'),
    path('actions/<uuid:pk>/update/', AdminActionUpdateAPIView.as_view(), name='action-update'),
    path('actions/<uuid:pk>/delete/', AdminActionDestroyAPIView.as_view(), name='action-delete'),
    path('actions/stats/', admin_action_stats, name='action-stats'),
    
    # Admin Logs
    path('logs/', AdminLogListAPIView.as_view(), name='log-list'),
    path('logs/<uuid:pk>/', AdminLogRetrieveAPIView.as_view(), name='log-retrieve'),
    path('logs/stats/', admin_log_stats, name='log-stats'),
    
    # System Configuration
    path('config/', SystemConfigListAPIView.as_view(), name='config-list'),
    path('config/create/', SystemConfigCreateAPIView.as_view(), name='config-create'),
    path('config/<uuid:pk>/', SystemConfigRetrieveAPIView.as_view(), name='config-retrieve'),
    path('config/<uuid:pk>/update/', SystemConfigUpdateAPIView.as_view(), name='config-update'),
    path('config/<uuid:pk>/delete/', SystemConfigDestroyAPIView.as_view(), name='config-delete'),
    
    # Admin Dashboard
    path('dashboard/', AdminDashboardListAPIView.as_view(), name='dashboard-list'),
    path('dashboard/<uuid:pk>/', AdminDashboardRetrieveAPIView.as_view(), name='dashboard-retrieve'),
    path('dashboard/stats/', admin_dashboard_stats, name='dashboard-stats'),
    
    # Admin Reports
    path('reports/', AdminReportListAPIView.as_view(), name='report-list'),
    path('reports/create/', AdminReportCreateAPIView.as_view(), name='report-create'),
    path('reports/<uuid:pk>/', AdminReportRetrieveAPIView.as_view(), name='report-retrieve'),
    path('reports/<uuid:pk>/generate/', admin_report_generate, name='report-generate'),
    
    # User Management
    path('users/', AdminUserListAPIView.as_view(), name='user-list'),
    path('users/create/', AdminUserCreateAPIView.as_view(), name='user-create'),
    path('users/<uuid:pk>/', AdminUserRetrieveAPIView.as_view(), name='user-retrieve'),
    path('users/<uuid:pk>/update/', AdminUserUpdateAPIView.as_view(), name='user-update'),
    path('users/<uuid:pk>/activate/', admin_user_activate, name='user-activate'),
    path('users/<uuid:pk>/deactivate/', admin_user_deactivate, name='user-deactivate'),
    path('users/<uuid:pk>/suspend/', admin_user_suspend, name='user-suspend'),
    path('users/stats/', admin_user_stats, name='user-stats'),
    
    # System Management
    path('system/info/', admin_system_info, name='system-info'),
    path('system/health/', admin_system_health, name='system-health'),
    path('system/backup/', admin_system_backup, name='system-backup'),
    path('system/cache/clear/', admin_system_cache_clear, name='system-cache-clear'),
    path('system/maintenance/', admin_system_maintenance, name='system-maintenance'),
    
    # Alert Management
    path('alerts/rules/', AlertRuleListAPIView.as_view(), name='alert-rule-list'),
    path('alerts/rules/create/', AlertRuleCreateAPIView.as_view(), name='alert-rule-create'),
    path('alerts/rules/<uuid:pk>/', AlertRuleRetrieveAPIView.as_view(), name='alert-rule-retrieve'),
    path('alerts/rules/<uuid:pk>/update/', AlertRuleUpdateAPIView.as_view(), name='alert-rule-update'),
    path('alerts/rules/<uuid:pk>/delete/', AlertRuleDestroyAPIView.as_view(), name='alert-rule-delete'),
    
    path('alerts/', SystemAlertListAPIView.as_view(), name='system-alert-list'),
    path('alerts/<uuid:pk>/', SystemAlertRetrieveAPIView.as_view(), name='system-alert-retrieve'),
    path('alerts/<uuid:pk>/acknowledge/', acknowledge_alert, name='acknowledge-alert'),
    path('alerts/<uuid:pk>/resolve/', resolve_alert, name='resolve-alert'),
    path('alerts/statistics/', alert_statistics, name='alert-statistics'),
    path('alerts/check/', check_alerts, name='check-alerts'),
    
    path('alerts/notifications/', AlertNotificationListAPIView.as_view(), name='alert-notification-list'),
    path('alerts/notifications/<uuid:pk>/', AlertNotificationRetrieveAPIView.as_view(), name='alert-notification-retrieve'),
    
    # Monitoring
    path('monitoring/metrics/', system_metrics, name='system-metrics'),
    path('monitoring/health/', system_health, name='system-health'),
    
    # Report Management
    path('reports/templates/', ReportTemplateListAPIView.as_view(), name='report-template-list'),
    path('reports/templates/create/', ReportTemplateCreateAPIView.as_view(), name='report-template-create'),
    path('reports/templates/<uuid:pk>/', ReportTemplateRetrieveAPIView.as_view(), name='report-template-retrieve'),
    path('reports/templates/<uuid:pk>/update/', ReportTemplateUpdateAPIView.as_view(), name='report-template-update'),
    path('reports/templates/<uuid:pk>/delete/', ReportTemplateDestroyAPIView.as_view(), name='report-template-delete'),
    path('reports/templates/<uuid:pk>/generate/', generate_report, name='generate-report'),
    
    path('reports/scheduled/', ScheduledReportListAPIView.as_view(), name='scheduled-report-list'),
    path('reports/scheduled/create/', ScheduledReportCreateAPIView.as_view(), name='scheduled-report-create'),
    path('reports/scheduled/<uuid:pk>/', ScheduledReportRetrieveAPIView.as_view(), name='scheduled-report-retrieve'),
    path('reports/scheduled/<uuid:pk>/update/', ScheduledReportUpdateAPIView.as_view(), name='scheduled-report-update'),
    path('reports/scheduled/<uuid:pk>/delete/', ScheduledReportDestroyAPIView.as_view(), name='scheduled-report-delete'),
    path('reports/scheduled/<uuid:pk>/execute/', execute_scheduled_report, name='execute-scheduled-report'),
    
    path('reports/executions/', ReportExecutionListAPIView.as_view(), name='report-execution-list'),
    path('reports/executions/<uuid:pk>/', ReportExecutionRetrieveAPIView.as_view(), name='report-execution-retrieve'),
    path('reports/statistics/', report_statistics, name='report-statistics'),
]
