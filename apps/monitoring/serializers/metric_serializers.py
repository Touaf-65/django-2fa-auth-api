"""
Serializers pour les métriques
"""
from rest_framework import serializers
from apps.monitoring.models import Metric, MetricValue


class MetricSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques"""
    
    latest_value = serializers.SerializerMethodField()
    is_counter = serializers.BooleanField(read_only=True)
    is_gauge = serializers.BooleanField(read_only=True)
    is_histogram = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Metric
        fields = [
            'id', 'name', 'display_name', 'description', 'metric_type',
            'unit', 'is_active', 'is_public', 'retention_days',
            'warning_threshold', 'critical_threshold', 'tags', 'metadata',
            'latest_value', 'is_counter', 'is_gauge', 'is_histogram',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_value(self, obj):
        """Récupère la dernière valeur de la métrique"""
        latest = obj.get_latest_value()
        if latest:
            return {
                'value': latest.value,
                'timestamp': latest.timestamp.isoformat(),
                'labels': latest.labels,
            }
        return None
    
    def create(self, validated_data):
        """Crée une nouvelle métrique"""
        # Extraire les métadonnées et tags
        tags = validated_data.pop('tags', [])
        metadata = validated_data.pop('metadata', {})
        
        metric = Metric.objects.create(
            **validated_data,
            tags=tags,
            metadata=metadata
        )
        
        return metric


class MetricValueSerializer(serializers.ModelSerializer):
    """Serializer pour les valeurs de métriques"""
    
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    metric_display_name = serializers.CharField(source='metric.display_name', read_only=True)
    metric_unit = serializers.CharField(source='metric.unit', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_above_warning = serializers.BooleanField(read_only=True)
    is_above_critical = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MetricValue
        fields = [
            'id', 'metric', 'metric_name', 'metric_display_name', 'metric_unit',
            'value', 'timestamp', 'user', 'user_email', 'session_id', 'request_id',
            'labels', 'metadata', 'is_above_warning', 'is_above_critical',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crée une nouvelle valeur de métrique"""
        # Extraire les métadonnées et labels
        labels = validated_data.pop('labels', {})
        metadata = validated_data.pop('metadata', {})
        
        metric_value = MetricValue.objects.create(
            **validated_data,
            labels=labels,
            metadata=metadata
        )
        
        return metric_value


class MetricCreateSerializer(serializers.Serializer):
    """Serializer pour créer une métrique"""
    
    name = serializers.CharField(max_length=100)
    display_name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    metric_type = serializers.ChoiceField(choices=Metric.TYPE_CHOICES)
    unit = serializers.ChoiceField(choices=Metric.UNIT_CHOICES, default='count')
    is_active = serializers.BooleanField(default=True)
    is_public = serializers.BooleanField(default=False)
    retention_days = serializers.IntegerField(min_value=1, max_value=365, default=30)
    warning_threshold = serializers.FloatField(required=False, allow_null=True)
    critical_threshold = serializers.FloatField(required=False, allow_null=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False
    )
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_name(self, value):
        """Valide le nom de la métrique"""
        if Metric.objects.filter(name=value).exists():
            raise serializers.ValidationError("A metric with this name already exists")
        return value
    
    def validate_thresholds(self, data):
        """Valide les seuils"""
        warning_threshold = data.get('warning_threshold')
        critical_threshold = data.get('critical_threshold')
        
        if warning_threshold is not None and critical_threshold is not None:
            if warning_threshold >= critical_threshold:
                raise serializers.ValidationError(
                    "Warning threshold must be less than critical threshold"
                )
        
        return data


class MetricValueCreateSerializer(serializers.Serializer):
    """Serializer pour créer une valeur de métrique"""
    
    metric_name = serializers.CharField(max_length=100)
    value = serializers.FloatField()
    labels = serializers.JSONField(default=dict, required=False)
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_metric_name(self, value):
        """Valide le nom de la métrique"""
        try:
            Metric.objects.get(name=value, is_active=True)
        except Metric.DoesNotExist:
            raise serializers.ValidationError("Metric not found or inactive")
        return value
    
    def validate_value(self, value):
        """Valide la valeur"""
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError("Value must be a number")
        return float(value)


class MetricStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des métriques"""
    
    metric_name = serializers.CharField()
    period = serializers.DictField()
    statistics = serializers.DictField()
    latest_value = serializers.FloatField()


class MetricExportSerializer(serializers.Serializer):
    """Serializer pour l'export des métriques"""
    
    metric_name = serializers.CharField(max_length=100)
    hours = serializers.IntegerField(min_value=1, max_value=168, default=24)
    format = serializers.ChoiceField(
        choices=['csv', 'json'],
        default='csv'
    )
    
    def validate_metric_name(self, value):
        """Valide le nom de la métrique"""
        try:
            Metric.objects.get(name=value)
        except Metric.DoesNotExist:
            raise serializers.ValidationError("Metric not found")
        return value
    
    def validate_hours(self, value):
        """Valide le nombre d'heures"""
        if value > 168:  # 7 jours maximum
            raise serializers.ValidationError("Maximum 168 hours (7 days) allowed")
        return value


class MetricsSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé des métriques"""
    
    total_metrics = serializers.IntegerField()
    metrics_by_type = serializers.ListField(
        child=serializers.DictField()
    )
    active_metrics = serializers.IntegerField()
    public_metrics = serializers.IntegerField()
    metrics_with_alerts = serializers.IntegerField()
    recent_values = serializers.ListField(
        child=serializers.DictField()
    )


