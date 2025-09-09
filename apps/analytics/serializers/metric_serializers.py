"""
Serializers pour les métriques Analytics
"""
from rest_framework import serializers
from apps.analytics.models import AnalyticsMetric, MetricValue


class AnalyticsMetricSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques analytiques"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    last_value = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsMetric
        fields = [
            'id', 'name', 'display_name', 'description', 'category', 'category_display',
            'metric_type', 'metric_type_display', 'unit', 'aggregation_method',
            'retention_days', 'calculation_query', 'data_source', 'warning_threshold',
            'critical_threshold', 'alert_enabled', 'is_active', 'last_calculated',
            'calculation_frequency', 'last_value', 'trend', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_calculated', 'created_at', 'updated_at'
        ]
    
    def get_last_value(self, obj):
        """Récupère la dernière valeur de la métrique"""
        last_value = obj.values.order_by('-timestamp').first()
        if last_value:
            return {
                'value': last_value.value,
                'timestamp': last_value.timestamp,
                'labels': last_value.labels
            }
        return None
    
    def get_trend(self, obj):
        """Récupère la tendance de la métrique"""
        # Calculer la tendance sur les 7 derniers jours
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        values = obj.values.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('timestamp')
        
        if values.count() < 2:
            return None
        
        first_value = values.first().value
        last_value = values.last().value
        
        if first_value == 0:
            return None
        
        trend_percentage = ((last_value - first_value) / first_value) * 100
        return {
            'percentage': round(trend_percentage, 2),
            'direction': 'up' if trend_percentage > 0 else 'down' if trend_percentage < 0 else 'stable',
            'first_value': first_value,
            'last_value': last_value
        }


class AnalyticsMetricCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de métriques"""
    
    class Meta:
        model = AnalyticsMetric
        fields = [
            'name', 'display_name', 'description', 'category', 'metric_type',
            'unit', 'aggregation_method', 'retention_days', 'calculation_query',
            'data_source', 'warning_threshold', 'critical_threshold',
            'alert_enabled', 'calculation_frequency'
        ]
    
    def validate_name(self, value):
        """Validation du nom de la métrique"""
        if AnalyticsMetric.objects.filter(name=value).exists():
            raise serializers.ValidationError("Une métrique avec ce nom existe déjà")
        return value


class MetricValueSerializer(serializers.ModelSerializer):
    """Serializer pour les valeurs de métriques"""
    metric_name = serializers.CharField(source='metric.name', read_only=True)
    metric_display_name = serializers.CharField(source='metric.display_name', read_only=True)
    calculated_by_email = serializers.EmailField(source='calculated_by.email', read_only=True)
    
    class Meta:
        model = MetricValue
        fields = [
            'id', 'metric', 'metric_name', 'metric_display_name', 'value', 'timestamp',
            'labels', 'dimensions', 'source', 'calculated_by', 'calculated_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class MetricValueCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de valeurs de métriques"""
    
    class Meta:
        model = MetricValue
        fields = [
            'metric', 'value', 'timestamp', 'labels', 'dimensions', 'source'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        metric = data.get('metric')
        value = data.get('value')
        
        # Vérifier que la valeur est compatible avec le type de métrique
        if metric and metric.metric_type in ['counter', 'gauge']:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError(
                    f"La valeur doit être numérique pour les métriques de type {metric.metric_type}"
                )
        
        return data


class MetricTrendSerializer(serializers.Serializer):
    """Serializer pour les tendances de métriques"""
    metric_name = serializers.CharField()
    period_days = serializers.IntegerField(min_value=1, max_value=365)
    granularity = serializers.ChoiceField(choices=['hour', 'day', 'week'])
    data = serializers.ListField(child=serializers.DictField())


class MetricComparisonSerializer(serializers.Serializer):
    """Serializer pour les comparaisons de métriques"""
    metric_name = serializers.CharField()
    period1_start = serializers.DateTimeField()
    period1_end = serializers.DateTimeField()
    period2_start = serializers.DateTimeField()
    period2_end = serializers.DateTimeField()
    comparison = serializers.DictField()


class MetricAlertSerializer(serializers.Serializer):
    """Serializer pour les alertes de métriques"""
    metric_name = serializers.CharField()
    current_value = serializers.FloatField()
    threshold = serializers.FloatField()
    threshold_type = serializers.ChoiceField(choices=['warning', 'critical'])
    alert_message = serializers.CharField()
    triggered_at = serializers.DateTimeField()


class MetricSummarySerializer(serializers.Serializer):
    """Serializer pour les résumés de métriques"""
    total_metrics = serializers.IntegerField()
    active_metrics = serializers.IntegerField()
    metrics_by_category = serializers.DictField()
    metrics_by_type = serializers.DictField()
    alerts_triggered = serializers.IntegerField()
    top_metrics = AnalyticsMetricSerializer(many=True)


class MetricCalculationSerializer(serializers.Serializer):
    """Serializer pour les calculs de métriques"""
    metric_name = serializers.CharField()
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    labels = serializers.DictField(required=False)
    result = serializers.FloatField()
    calculation_time = serializers.FloatField()
    cached = serializers.BooleanField()


class MetricBulkUpdateSerializer(serializers.Serializer):
    """Serializer pour les mises à jour en lot de métriques"""
    metrics = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100,
        help_text="Liste des métriques à mettre à jour (maximum 100)"
    )
    
    def validate_metrics(self, value):
        """Validation des métriques en lot"""
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 métriques autorisées par lot")
        
        # Vérifier que toutes les métriques ont un nom
        for metric in value:
            if 'name' not in metric:
                raise serializers.ValidationError("Toutes les métriques doivent avoir un nom")
        
        return value

