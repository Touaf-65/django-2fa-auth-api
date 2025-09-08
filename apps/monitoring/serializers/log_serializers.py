"""
Serializers pour les logs
"""
from rest_framework import serializers
from apps.monitoring.models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    """Serializer pour les entrées de log"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_error = serializers.BooleanField(read_only=True)
    is_warning = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'level', 'source', 'message', 'user', 'user_email',
            'session_id', 'request_id', 'ip_address', 'user_agent',
            'metadata', 'tags', 'app_name', 'module_name', 'function_name',
            'line_number', 'method', 'path', 'status_code', 'response_time',
            'exception_type', 'exception_message', 'stack_trace',
            'is_error', 'is_warning', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crée une nouvelle entrée de log"""
        # Extraire les métadonnées et tags
        metadata = validated_data.pop('metadata', {})
        tags = validated_data.pop('tags', [])
        
        log_entry = LogEntry.objects.create(
            **validated_data,
            metadata=metadata,
            tags=tags
        )
        
        return log_entry


class LogEntrySearchSerializer(serializers.Serializer):
    """Serializer pour la recherche dans les logs"""
    
    query = serializers.CharField(max_length=500, required=False)
    level = serializers.ChoiceField(
        choices=LogEntry.LEVEL_CHOICES,
        required=False
    )
    source = serializers.ChoiceField(
        choices=LogEntry.SOURCE_CHOICES,
        required=False
    )
    hours = serializers.IntegerField(min_value=1, max_value=168, default=24)
    limit = serializers.IntegerField(min_value=1, max_value=1000, default=100)
    
    def validate_hours(self, value):
        """Valide le nombre d'heures"""
        if value > 168:  # 7 jours maximum
            raise serializers.ValidationError("Maximum 168 hours (7 days) allowed")
        return value
    
    def validate_limit(self, value):
        """Valide la limite de résultats"""
        if value > 1000:
            raise serializers.ValidationError("Maximum 1000 results allowed")
        return value


class LogEntryExportSerializer(serializers.Serializer):
    """Serializer pour l'export des logs"""
    
    level = serializers.ChoiceField(
        choices=LogEntry.LEVEL_CHOICES,
        required=False
    )
    source = serializers.ChoiceField(
        choices=LogEntry.SOURCE_CHOICES,
        required=False
    )
    hours = serializers.IntegerField(min_value=1, max_value=168, default=24)
    format = serializers.ChoiceField(
        choices=['csv', 'json'],
        default='csv'
    )
    
    def validate_hours(self, value):
        """Valide le nombre d'heures"""
        if value > 168:  # 7 jours maximum
            raise serializers.ValidationError("Maximum 168 hours (7 days) allowed")
        return value


class LogEntryCreateSerializer(serializers.Serializer):
    """Serializer pour créer un log via API"""
    
    level = serializers.ChoiceField(
        choices=LogEntry.LEVEL_CHOICES,
        default='INFO'
    )
    message = serializers.CharField(max_length=1000)
    source = serializers.ChoiceField(
        choices=LogEntry.SOURCE_CHOICES,
        default='api'
    )
    metadata = serializers.JSONField(default=dict, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False
    )
    
    def validate_message(self, value):
        """Valide le message"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()
    
    def validate_tags(self, value):
        """Valide les tags"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags allowed")
        return value


class LogStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des logs"""
    
    total_logs = serializers.IntegerField()
    logs_by_level = serializers.ListField(
        child=serializers.DictField()
    )
    logs_by_source = serializers.ListField(
        child=serializers.DictField()
    )
    error_logs = serializers.IntegerField()
    warning_logs = serializers.IntegerField()
    info_logs = serializers.IntegerField()
    debug_logs = serializers.IntegerField()
    logs_by_hour = serializers.ListField(
        child=serializers.DictField()
    )
