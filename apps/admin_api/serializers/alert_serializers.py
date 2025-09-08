"""
Serializers pour les alertes système
"""
from rest_framework import serializers
from apps.admin_api.models import AlertRule, SystemAlert, AlertNotification


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer complet pour AlertRule"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AlertRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertRuleListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AlertRule"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'status', 'status_display',
            'threshold_value', 'comparison_operator', 'check_interval',
            'created_by_email', 'created_at'
        ]


class AlertRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une AlertRule"""
    
    class Meta:
        model = AlertRule
        fields = [
            'name', 'description', 'alert_type', 'severity', 'condition',
            'threshold_value', 'comparison_operator', 'check_interval',
            'cooldown_period', 'max_alerts_per_hour', 'notification_channels',
            'escalation_rules', 'tags'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SystemAlertSerializer(serializers.ModelSerializer):
    """Serializer complet pour SystemAlert"""
    alert_rule_name = serializers.CharField(source='alert_rule.name', read_only=True)
    alert_rule_type = serializers.CharField(source='alert_rule.alert_type', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    acknowledged_by_email = serializers.CharField(source='acknowledged_by.email', read_only=True)
    resolved_by_email = serializers.CharField(source='resolved_by.email', read_only=True)
    
    class Meta:
        model = SystemAlert
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'triggered_at']


class SystemAlertListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des SystemAlert"""
    alert_rule_name = serializers.CharField(source='alert_rule.name', read_only=True)
    alert_rule_type = serializers.CharField(source='alert_rule.alert_type', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SystemAlert
        fields = [
            'id', 'title', 'message', 'status', 'status_display',
            'severity', 'severity_display', 'current_value', 'threshold_value',
            'alert_rule_name', 'alert_rule_type', 'triggered_at',
            'acknowledged_at', 'resolved_at'
        ]


class AlertNotificationSerializer(serializers.ModelSerializer):
    """Serializer complet pour AlertNotification"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    alert_severity = serializers.CharField(source='alert.severity', read_only=True)
    channel_type_display = serializers.CharField(source='get_channel_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertNotificationListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AlertNotification"""
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    alert_severity = serializers.CharField(source='alert.severity', read_only=True)
    channel_type_display = serializers.CharField(source='get_channel_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'alert_title', 'alert_severity', 'channel_type',
            'channel_type_display', 'recipient', 'status', 'status_display',
            'subject', 'sent_at', 'delivered_at', 'retry_count', 'created_at'
        ]

