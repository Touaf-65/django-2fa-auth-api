"""
Serializers pour les rapports Analytics
"""
from rest_framework import serializers
from apps.analytics.models import Report, ReportTemplate, ReportSchedule


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les templates de rapports"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'template_config',
            'is_active', 'created_by', 'created_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports"""
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'template', 'template_name', 'report_type',
            'report_type_display', 'status', 'status_display', 'config', 'filters',
            'date_range_start', 'date_range_end', 'data', 'summary', 'file_path',
            'file_size', 'generated_at', 'generated_by', 'generated_by_email',
            'execution_time', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'data', 'summary', 'file_path', 'file_size',
            'generated_at', 'execution_time', 'error_message', 'created_at', 'updated_at'
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de rapports"""
    
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'template', 'report_type', 'config', 'filters',
            'date_range_start', 'date_range_end'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        if data.get('template') and data.get('report_type'):
            if data['template'].report_type != data['report_type']:
                raise serializers.ValidationError(
                    "Le type de rapport doit correspondre au template sélectionné"
                )
        return data


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer pour les planifications de rapports"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    last_status_display = serializers.CharField(source='get_last_status_display', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'name', 'template', 'template_name', 'frequency', 'frequency_display',
            'cron_expression', 'timezone', 'is_active', 'recipients', 'notification_enabled',
            'last_run', 'next_run', 'last_status', 'last_status_display', 'created_by',
            'created_by_email', 'total_runs', 'successful_runs', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_run', 'next_run', 'last_status', 'total_runs',
            'successful_runs', 'created_at', 'updated_at'
        ]


class ReportScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de planifications de rapports"""
    
    class Meta:
        model = ReportSchedule
        fields = [
            'name', 'template', 'frequency', 'cron_expression', 'timezone',
            'is_active', 'recipients', 'notification_enabled'
        ]
    
    def validate_recipients(self, value):
        """Validation des destinataires"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Les destinataires doivent être une liste")
        
        # Vérifier que tous les destinataires sont des emails valides
        for email in value:
            if not email or '@' not in email:
                raise serializers.ValidationError(f"Email invalide: {email}")
        
        return value


class ReportSummarySerializer(serializers.Serializer):
    """Serializer pour les résumés de rapports"""
    total_reports = serializers.IntegerField()
    completed_reports = serializers.IntegerField()
    failed_reports = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    avg_execution_time = serializers.FloatField()
    most_used_template = serializers.CharField()
    recent_reports = ReportSerializer(many=True)


class ReportDataSerializer(serializers.Serializer):
    """Serializer pour les données de rapport"""
    data = serializers.JSONField()
    summary = serializers.JSONField()
    metadata = serializers.JSONField()
    generated_at = serializers.DateTimeField()
    execution_time = serializers.FloatField()

