"""
Serializers pour la santé du système
"""
from rest_framework import serializers
from apps.monitoring.models import SystemHealth, HealthCheck, HealthCheckResult


class SystemHealthSerializer(serializers.ModelSerializer):
    """Serializer pour la santé du système"""
    
    is_healthy = serializers.BooleanField(read_only=True)
    is_degraded = serializers.BooleanField(read_only=True)
    is_unhealthy = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SystemHealth
        fields = [
            'id', 'status', 'overall_score', 'database_status', 'cache_status',
            'storage_status', 'external_services_status', 'cpu_usage',
            'memory_usage', 'disk_usage', 'network_latency', 'issues',
            'recommendations', 'metadata', 'is_healthy', 'is_degraded',
            'is_unhealthy', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HealthCheckSerializer(serializers.ModelSerializer):
    """Serializer pour les vérifications de santé"""
    
    latest_result = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthCheck
        fields = [
            'id', 'name', 'display_name', 'description', 'check_type',
            'is_active', 'check_interval', 'timeout', 'check_config',
            'tags', 'metadata', 'latest_result', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_result(self, obj):
        """Récupère le dernier résultat de la vérification"""
        latest = obj.get_latest_result()
        if latest:
            return {
                'status': latest.status,
                'message': latest.message,
                'response_time': latest.response_time,
                'timestamp': latest.created_at.isoformat(),
            }
        return None
    
    def create(self, validated_data):
        """Crée une nouvelle vérification de santé"""
        # Extraire les métadonnées et tags
        tags = validated_data.pop('tags', [])
        metadata = validated_data.pop('metadata', {})
        check_config = validated_data.pop('check_config', {})
        
        health_check = HealthCheck.objects.create(
            **validated_data,
            tags=tags,
            metadata=metadata,
            check_config=check_config
        )
        
        return health_check


class HealthCheckResultSerializer(serializers.ModelSerializer):
    """Serializer pour les résultats de vérifications de santé"""
    
    health_check_name = serializers.CharField(source='health_check.name', read_only=True)
    health_check_type = serializers.CharField(source='health_check.check_type', read_only=True)
    is_pass = serializers.BooleanField(read_only=True)
    is_fail = serializers.BooleanField(read_only=True)
    is_warning = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = HealthCheckResult
        fields = [
            'id', 'health_check', 'health_check_name', 'health_check_type',
            'status', 'message', 'response_time', 'error_message', 'metadata',
            'is_pass', 'is_fail', 'is_warning', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crée un nouveau résultat de vérification"""
        # Extraire les métadonnées
        metadata = validated_data.pop('metadata', {})
        
        result = HealthCheckResult.objects.create(
            **validated_data,
            metadata=metadata
        )
        
        return result


class HealthCheckCreateSerializer(serializers.Serializer):
    """Serializer pour créer une vérification de santé"""
    
    name = serializers.CharField(max_length=100)
    display_name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    check_type = serializers.ChoiceField(choices=HealthCheck.TYPE_CHOICES)
    is_active = serializers.BooleanField(default=True)
    check_interval = serializers.IntegerField(min_value=1, max_value=3600, default=60)
    timeout = serializers.IntegerField(min_value=1, max_value=300, default=30)
    check_config = serializers.JSONField(default=dict, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False
    )
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_name(self, value):
        """Valide le nom de la vérification"""
        if HealthCheck.objects.filter(name=value).exists():
            raise serializers.ValidationError("A health check with this name already exists")
        return value
    
    def validate_check_interval(self, value):
        """Valide l'intervalle de vérification"""
        if value < 1:
            raise serializers.ValidationError("Check interval must be at least 1 second")
        if value > 3600:  # 1 heure maximum
            raise serializers.ValidationError("Check interval cannot exceed 1 hour")
        return value
    
    def validate_timeout(self, value):
        """Valide le timeout"""
        if value < 1:
            raise serializers.ValidationError("Timeout must be at least 1 second")
        if value > 300:  # 5 minutes maximum
            raise serializers.ValidationError("Timeout cannot exceed 5 minutes")
        return value


class HealthCheckResultCreateSerializer(serializers.Serializer):
    """Serializer pour créer un résultat de vérification"""
    
    health_check_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=HealthCheckResult._meta.get_field('status').choices)
    message = serializers.CharField(required=False, allow_blank=True)
    response_time = serializers.FloatField(required=False, allow_null=True)
    error_message = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_health_check_id(self, value):
        """Valide l'ID de la vérification de santé"""
        try:
            HealthCheck.objects.get(id=value)
        except HealthCheck.DoesNotExist:
            raise serializers.ValidationError("Health check not found")
        return value
    
    def validate_response_time(self, value):
        """Valide le temps de réponse"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Response time cannot be negative")
        return value


class HealthStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de santé"""
    
    total_checks = serializers.IntegerField()
    passed_checks = serializers.IntegerField()
    failed_checks = serializers.IntegerField()
    warning_checks = serializers.IntegerField()
    checks_by_type = serializers.ListField(
        child=serializers.DictField()
    )
    checks_by_status = serializers.ListField(
        child=serializers.DictField()
    )
    average_response_time = serializers.FloatField()


class HealthCheckSuccessRateSerializer(serializers.Serializer):
    """Serializer pour le taux de succès d'une vérification"""
    
    health_check_id = serializers.IntegerField()
    health_check_name = serializers.CharField()
    success_rate = serializers.FloatField()
    period_hours = serializers.IntegerField()


class ComponentHealthSerializer(serializers.Serializer):
    """Serializer pour la santé d'un composant"""
    
    component = serializers.CharField()
    health = serializers.DictField()


class HealthCheckRunSerializer(serializers.Serializer):
    """Serializer pour exécuter une vérification de santé"""
    
    health_check_id = serializers.IntegerField()
    
    def validate_health_check_id(self, value):
        """Valide l'ID de la vérification de santé"""
        try:
            HealthCheck.objects.get(id=value, is_active=True)
        except HealthCheck.DoesNotExist:
            raise serializers.ValidationError("Health check not found or inactive")
        return value


class HealthCheckRunAllSerializer(serializers.Serializer):
    """Serializer pour exécuter toutes les vérifications de santé"""
    
    force_run = serializers.BooleanField(default=False)
    
    def validate_force_run(self, value):
        """Valide le paramètre force_run"""
        return value
