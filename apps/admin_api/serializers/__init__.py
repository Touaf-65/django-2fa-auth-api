"""
Serializers pour l'Admin API
"""
from .admin_action_serializers import (
    AdminActionSerializer,
    AdminActionListSerializer,
    AdminActionCreateSerializer,
    AdminActionUpdateSerializer,
)
from .admin_log_serializers import (
    AdminLogSerializer,
    AdminLogListSerializer,
)
from .system_config_serializers import (
    SystemConfigSerializer,
    SystemConfigListSerializer,
    SystemConfigCreateSerializer,
    SystemConfigUpdateSerializer,
)
from .admin_dashboard_serializers import (
    AdminDashboardSerializer,
    AdminDashboardListSerializer,
)
from .admin_report_serializers import (
    AdminReportSerializer,
    AdminReportListSerializer,
    AdminReportCreateSerializer,
)
from .alert_serializers import (
    AlertRuleSerializer,
    AlertRuleListSerializer,
    AlertRuleCreateSerializer,
    SystemAlertSerializer,
    SystemAlertListSerializer,
    AlertNotificationSerializer,
    AlertNotificationListSerializer,
)
from .report_serializers import (
    ReportTemplateSerializer,
    ReportTemplateListSerializer,
    ReportTemplateCreateSerializer,
    ScheduledReportSerializer,
    ScheduledReportListSerializer,
    ScheduledReportCreateSerializer,
    ReportExecutionSerializer,
    ReportExecutionListSerializer,
)

__all__ = [
    # AdminAction serializers
    'AdminActionSerializer',
    'AdminActionListSerializer',
    'AdminActionCreateSerializer',
    'AdminActionUpdateSerializer',
    
    # AdminLog serializers
    'AdminLogSerializer',
    'AdminLogListSerializer',
    
    # SystemConfig serializers
    'SystemConfigSerializer',
    'SystemConfigListSerializer',
    'SystemConfigCreateSerializer',
    'SystemConfigUpdateSerializer',
    
    # AdminDashboard serializers
    'AdminDashboardSerializer',
    'AdminDashboardListSerializer',
    
    # AdminReport serializers
    'AdminReportSerializer',
    'AdminReportListSerializer',
    'AdminReportCreateSerializer',
    
    # Alert serializers
    'AlertRuleSerializer',
    'AlertRuleListSerializer',
    'AlertRuleCreateSerializer',
    'SystemAlertSerializer',
    'SystemAlertListSerializer',
    'AlertNotificationSerializer',
    'AlertNotificationListSerializer',
    
    # Report serializers
    'ReportTemplateSerializer',
    'ReportTemplateListSerializer',
    'ReportTemplateCreateSerializer',
    'ScheduledReportSerializer',
    'ScheduledReportListSerializer',
    'ScheduledReportCreateSerializer',
    'ReportExecutionSerializer',
    'ReportExecutionListSerializer',
]
