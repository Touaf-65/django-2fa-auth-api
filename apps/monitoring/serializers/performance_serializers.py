"""
Serializers pour les performances
"""
from rest_framework import serializers
from apps.monitoring.models import PerformanceMetric, PerformanceReport


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques de performance"""
    
    latest_value = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'name', 'display_name', 'description', 'category',
            'is_active', 'collection_interval', 'warning_threshold',
            'critical_threshold', 'tags', 'metadata', 'latest_value',
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
            }
        return None
    
    def create(self, validated_data):
        """Crée une nouvelle métrique de performance"""
        # Extraire les métadonnées et tags
        tags = validated_data.pop('tags', [])
        metadata = validated_data.pop('metadata', {})
        
        metric = PerformanceMetric.objects.create(
            **validated_data,
            tags=tags,
            metadata=metadata
        )
        
        return metric


class PerformanceReportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports de performance"""
    
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)
    duration = serializers.DurationField(read_only=True)
    metrics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceReport
        fields = [
            'id', 'name', 'report_type', 'period_start', 'period_end',
            'metrics', 'summary', 'details', 'is_generated', 'generated_at',
            'generated_by', 'generated_by_email', 'metadata', 'duration',
            'metrics_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_metrics_count(self, obj):
        """Récupère le nombre de métriques"""
        return obj.metrics.count()
    
    def create(self, validated_data):
        """Crée un nouveau rapport de performance"""
        # Extraire les métriques et métadonnées
        metrics = validated_data.pop('metrics', [])
        metadata = validated_data.pop('metadata', {})
        
        report = PerformanceReport.objects.create(
            **validated_data,
            metadata=metadata
        )
        
        if metrics:
            report.metrics.set(metrics)
        
        return report


class PerformanceMetricCreateSerializer(serializers.Serializer):
    """Serializer pour créer une métrique de performance"""
    
    name = serializers.CharField(max_length=100)
    display_name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ChoiceField(choices=PerformanceMetric.CATEGORY_CHOICES)
    is_active = serializers.BooleanField(default=True)
    collection_interval = serializers.IntegerField(min_value=1, max_value=3600, default=60)
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
        if PerformanceMetric.objects.filter(name=value).exists():
            raise serializers.ValidationError("A performance metric with this name already exists")
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


class PerformanceReportCreateSerializer(serializers.Serializer):
    """Serializer pour créer un rapport de performance"""
    
    name = serializers.CharField(max_length=200)
    report_type = serializers.ChoiceField(choices=PerformanceReport.REPORT_TYPE_CHOICES)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    metric_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    def validate_period(self, data):
        """Valide la période du rapport"""
        period_start = data.get('period_start')
        period_end = data.get('period_end')
        
        if period_start and period_end:
            if period_start >= period_end:
                raise serializers.ValidationError(
                    "period_start must be before period_end"
                )
            
            # Vérifier que la période n'est pas trop longue (max 30 jours)
            from datetime import timedelta
            if period_end - period_start > timedelta(days=30):
                raise serializers.ValidationError(
                    "Report period cannot exceed 30 days"
                )
        
        return data
    
    def validate_metric_ids(self, value):
        """Valide les IDs des métriques"""
        if value:
            existing_metrics = PerformanceMetric.objects.filter(id__in=value)
            if existing_metrics.count() != len(value):
                raise serializers.ValidationError("One or more metrics not found")
        return value


class ResponseTimeRecordSerializer(serializers.Serializer):
    """Serializer pour enregistrer un temps de réponse"""
    
    endpoint = serializers.CharField(max_length=500)
    method = serializers.CharField(max_length=10, default='GET')
    response_time = serializers.FloatField(min_value=0)
    status_code = serializers.IntegerField(min_value=100, max_value=599, required=False)
    
    def validate_method(self, value):
        """Valide la méthode HTTP"""
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        if value.upper() not in valid_methods:
            raise serializers.ValidationError(f"Invalid HTTP method: {value}")
        return value.upper()
    
    def validate_response_time(self, value):
        """Valide le temps de réponse"""
        if value < 0:
            raise serializers.ValidationError("Response time cannot be negative")
        if value > 300:  # 5 minutes maximum
            raise serializers.ValidationError("Response time too high (max 300 seconds)")
        return value


class ThroughputRecordSerializer(serializers.Serializer):
    """Serializer pour enregistrer le débit"""
    
    endpoint = serializers.CharField(max_length=500)
    method = serializers.CharField(max_length=10, default='GET')
    count = serializers.IntegerField(min_value=1)
    
    def validate_method(self, value):
        """Valide la méthode HTTP"""
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        if value.upper() not in valid_methods:
            raise serializers.ValidationError(f"Invalid HTTP method: {value}")
        return value.upper()
    
    def validate_count(self, value):
        """Valide le nombre de requêtes"""
        if value < 1:
            raise serializers.ValidationError("Count must be at least 1")
        if value > 10000:
            raise serializers.ValidationError("Count too high (max 10000)")
        return value


class ErrorRateRecordSerializer(serializers.Serializer):
    """Serializer pour enregistrer le taux d'erreur"""
    
    endpoint = serializers.CharField(max_length=500)
    method = serializers.CharField(max_length=10, default='GET')
    error_count = serializers.IntegerField(min_value=0)
    total_count = serializers.IntegerField(min_value=1)
    
    def validate_method(self, value):
        """Valide la méthode HTTP"""
        valid_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        if value.upper() not in valid_methods:
            raise serializers.ValidationError(f"Invalid HTTP method: {value}")
        return value.upper()
    
    def validate_counts(self, data):
        """Valide les compteurs"""
        error_count = data.get('error_count', 0)
        total_count = data.get('total_count', 1)
        
        if error_count > total_count:
            raise serializers.ValidationError("Error count cannot exceed total count")
        
        return data


class PerformanceSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé des performances"""
    
    total_metrics = serializers.IntegerField()
    metrics_by_category = serializers.ListField(
        child=serializers.DictField()
    )
    system_metrics = serializers.DictField()
    performance_metrics = serializers.ListField(
        child=serializers.DictField()
    )


class PerformanceTrendsSerializer(serializers.Serializer):
    """Serializer pour les tendances de performance"""
    
    metric_name = serializers.CharField()
    display_name = serializers.CharField()
    category = serializers.CharField()
    period = serializers.DictField()
    statistics = serializers.DictField()
    values = serializers.ListField(
        child=serializers.DictField()
    )


class SlowEndpointsSerializer(serializers.Serializer):
    """Serializer pour les endpoints lents"""
    
    slow_endpoints = serializers.ListField(
        child=serializers.DictField()
    )
    period_hours = serializers.IntegerField()
    limit = serializers.IntegerField()


class ErrorEndpointsSerializer(serializers.Serializer):
    """Serializer pour les endpoints avec erreurs"""
    
    error_endpoints = serializers.ListField(
        child=serializers.DictField()
    )
    period_hours = serializers.IntegerField()
    limit = serializers.IntegerField()


