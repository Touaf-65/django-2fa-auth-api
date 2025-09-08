"""
Serializers pour les alertes
"""
from rest_framework import serializers
from apps.monitoring.models import Alert, AlertRule, AlertNotification


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer pour les règles d'alerte"""
    
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    metric_display_name = serializers.CharField(source='metric.display_name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'metric', 'metric_name', 'metric_display_name',
            'condition', 'threshold', 'duration', 'severity', 'status', 'is_enabled',
            'notification_channels', 'notification_template', 'tags', 'metadata',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crée une nouvelle règle d'alerte"""
        # Extraire les métadonnées et tags
        tags = validated_data.pop('tags', [])
        metadata = validated_data.pop('metadata', {})
        notification_channels = validated_data.pop('notification_channels', [])
        
        alert_rule = AlertRule.objects.create(
            **validated_data,
            tags=tags,
            metadata=metadata,
            notification_channels=notification_channels
        )
        
        return alert_rule


class AlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes"""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    rule_severity = serializers.CharField(source='rule.severity', read_only=True)
    metric_name = serializers.CharField(source='rule.metric.name', read_only=True)
    metric_display_name = serializers.CharField(source='rule.metric.display_name', read_only=True)
    acknowledged_by_email = serializers.EmailField(source='acknowledged_by.email', read_only=True)
    is_firing = serializers.BooleanField(read_only=True)
    is_resolved = serializers.BooleanField(read_only=True)
    is_acknowledged = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'rule', 'rule_name', 'rule_severity', 'metric_name', 'metric_display_name',
            'metric_value', 'status', 'severity', 'message', 'value', 'threshold',
            'acknowledged_by', 'acknowledged_by_email', 'acknowledged_at', 'resolved_at',
            'labels', 'annotations', 'is_firing', 'is_resolved', 'is_acknowledged',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertNotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications d'alerte"""
    
    alert_rule_name = serializers.CharField(source='alert.rule.name', read_only=True)
    alert_severity = serializers.CharField(source='alert.severity', read_only=True)
    is_sent = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'alert', 'alert_rule_name', 'alert_severity', 'channel', 'recipient',
            'subject', 'message', 'status', 'sent_at', 'delivered_at', 'metadata',
            'error_message', 'is_sent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertRuleCreateSerializer(serializers.Serializer):
    """Serializer pour créer une règle d'alerte"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    metric_id = serializers.IntegerField()
    condition = serializers.ChoiceField(choices=AlertRule._meta.get_field('condition').choices)
    threshold = serializers.FloatField()
    duration = serializers.IntegerField(min_value=0, default=0)
    severity = serializers.ChoiceField(choices=AlertRule.SEVERITY_CHOICES, default='medium')
    status = serializers.ChoiceField(choices=AlertRule.STATUS_CHOICES, default='active')
    is_enabled = serializers.BooleanField(default=True)
    notification_channels = serializers.ListField(
        child=serializers.DictField(),
        default=list,
        required=False
    )
    notification_template = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False
    )
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_metric_id(self, value):
        """Valide l'ID de la métrique"""
        from apps.monitoring.models import Metric
        try:
            Metric.objects.get(id=value)
        except Metric.DoesNotExist:
            raise serializers.ValidationError("Metric not found")
        return value
    
    def validate_threshold(self, value):
        """Valide le seuil"""
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError("Threshold must be a number")
        return float(value)
    
    def validate_notification_channels(self, value):
        """Valide les canaux de notification"""
        valid_channels = ['email', 'sms', 'webhook', 'slack', 'teams', 'discord']
        
        for channel in value:
            if not isinstance(channel, dict):
                raise serializers.ValidationError("Each channel must be a dictionary")
            
            if 'type' not in channel or 'recipient' not in channel:
                raise serializers.ValidationError("Each channel must have 'type' and 'recipient'")
            
            if channel['type'] not in valid_channels:
                raise serializers.ValidationError(f"Invalid channel type: {channel['type']}")
        
        return value


class AlertAcknowledgeSerializer(serializers.Serializer):
    """Serializer pour acquitter une alerte"""
    
    message = serializers.CharField(required=False, allow_blank=True)
    
    def validate_message(self, value):
        """Valide le message d'acquittement"""
        if value and len(value) > 500:
            raise serializers.ValidationError("Message too long (max 500 characters)")
        return value


class AlertResolveSerializer(serializers.Serializer):
    """Serializer pour résoudre une alerte"""
    
    message = serializers.CharField(required=False, allow_blank=True)
    
    def validate_message(self, value):
        """Valide le message de résolution"""
        if value and len(value) > 500:
            raise serializers.ValidationError("Message too long (max 500 characters)")
        return value


class AlertTestSerializer(serializers.Serializer):
    """Serializer pour tester une règle d'alerte"""
    
    test_value = serializers.FloatField()
    
    def validate_test_value(self, value):
        """Valide la valeur de test"""
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError("Test value must be a number")
        return float(value)


class AlertStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des alertes"""
    
    total_alerts = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    resolved_alerts = serializers.IntegerField()
    acknowledged_alerts = serializers.IntegerField()
    alerts_by_severity = serializers.ListField(
        child=serializers.DictField()
    )
    alerts_by_rule = serializers.ListField(
        child=serializers.DictField()
    )
    alerts_by_hour = serializers.ListField(
        child=serializers.DictField()
    )


class AlertTrendsSerializer(serializers.Serializer):
    """Serializer pour les tendances des alertes"""
    
    daily_trends = serializers.ListField(
        child=serializers.DictField()
    )
    period = serializers.DictField()


