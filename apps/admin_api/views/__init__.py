"""
Vues pour l'Admin API
"""
from .admin_action_views import (
    AdminActionListAPIView,
    AdminActionCreateAPIView,
    AdminActionRetrieveAPIView,
    AdminActionUpdateAPIView,
    AdminActionDestroyAPIView,
    admin_action_stats,
)
from .admin_log_views import (
    AdminLogListAPIView,
    AdminLogRetrieveAPIView,
    admin_log_stats,
)
from .system_config_views import (
    SystemConfigListAPIView,
    SystemConfigCreateAPIView,
    SystemConfigRetrieveAPIView,
    SystemConfigUpdateAPIView,
    SystemConfigDestroyAPIView,
)
from .admin_dashboard_views import (
    AdminDashboardListAPIView,
    AdminDashboardRetrieveAPIView,
    admin_dashboard_stats,
)
from .admin_report_views import (
    AdminReportListAPIView,
    AdminReportCreateAPIView,
    AdminReportRetrieveAPIView,
    admin_report_generate,
)
from .admin_user_views import (
    AdminUserListAPIView,
    AdminUserCreateAPIView,
    AdminUserRetrieveAPIView,
    AdminUserUpdateAPIView,
    admin_user_activate,
    admin_user_deactivate,
    admin_user_suspend,
    admin_user_stats,
)
from .admin_system_views import (
    admin_system_info,
    admin_system_health,
    admin_system_backup,
    admin_system_cache_clear,
    admin_system_maintenance,
)
from .alert_views import (
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
)
from .report_views import (
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

__all__ = [
    # AdminAction views
    'AdminActionListAPIView',
    'AdminActionCreateAPIView',
    'AdminActionRetrieveAPIView',
    'AdminActionUpdateAPIView',
    'AdminActionDestroyAPIView',
    'admin_action_stats',
    
    # AdminLog views
    'AdminLogListAPIView',
    'AdminLogRetrieveAPIView',
    'admin_log_stats',
    
    # SystemConfig views
    'SystemConfigListAPIView',
    'SystemConfigCreateAPIView',
    'SystemConfigRetrieveAPIView',
    'SystemConfigUpdateAPIView',
    'SystemConfigDestroyAPIView',
    
    # AdminDashboard views
    'AdminDashboardListAPIView',
    'AdminDashboardRetrieveAPIView',
    'admin_dashboard_stats',
    
    # AdminReport views
    'AdminReportListAPIView',
    'AdminReportCreateAPIView',
    'AdminReportRetrieveAPIView',
    'admin_report_generate',
    
    # AdminUser views
    'AdminUserListAPIView',
    'AdminUserCreateAPIView',
    'AdminUserRetrieveAPIView',
    'AdminUserUpdateAPIView',
    'admin_user_activate',
    'admin_user_deactivate',
    'admin_user_suspend',
    'admin_user_stats',
    
    # AdminSystem views
    'admin_system_info',
    'admin_system_health',
    'admin_system_backup',
    'admin_system_cache_clear',
    'admin_system_maintenance',
    
    # Alert views
    'AlertRuleListAPIView',
    'AlertRuleCreateAPIView',
    'AlertRuleRetrieveAPIView',
    'AlertRuleUpdateAPIView',
    'AlertRuleDestroyAPIView',
    'SystemAlertListAPIView',
    'SystemAlertRetrieveAPIView',
    'acknowledge_alert',
    'resolve_alert',
    'alert_statistics',
    'check_alerts',
    'AlertNotificationListAPIView',
    'AlertNotificationRetrieveAPIView',
    'system_metrics',
    'system_health',
    
    # Report views
    'ReportTemplateListAPIView',
    'ReportTemplateCreateAPIView',
    'ReportTemplateRetrieveAPIView',
    'ReportTemplateUpdateAPIView',
    'ReportTemplateDestroyAPIView',
    'ScheduledReportListAPIView',
    'ScheduledReportCreateAPIView',
    'ScheduledReportRetrieveAPIView',
    'ScheduledReportUpdateAPIView',
    'ScheduledReportDestroyAPIView',
    'execute_scheduled_report',
    'generate_report',
    'ReportExecutionListAPIView',
    'ReportExecutionRetrieveAPIView',
    'report_statistics',
]
