"""
Serializers pour les rapports automatiques
"""
from rest_framework import serializers
from apps.admin_api.models import ReportTemplate, ScheduledReport, ReportExecution


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer complet pour ReportTemplate"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportTemplateListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des ReportTemplate"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'report_type_display',
            'format', 'format_display', 'is_active', 'created_by_email',
            'created_at'
        ]


class ReportTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un ReportTemplate"""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'name', 'description', 'report_type', 'format',
            'query_config', 'template_config', 'filters', 'tags'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ScheduledReportSerializer(serializers.ModelSerializer):
    """Serializer complet pour ScheduledReport"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.report_type', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduledReportListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des ScheduledReport"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.report_type', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'name', 'description', 'template_name', 'template_type',
            'frequency', 'frequency_display', 'next_run', 'last_run',
            'status', 'status_display', 'created_by_email', 'created_at'
        ]


class ScheduledReportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un ScheduledReport"""
    
    class Meta:
        model = ScheduledReport
        fields = [
            'name', 'description', 'template', 'frequency', 'cron_expression',
            'recipients', 'notification_channels', 'retention_days'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer complet pour ReportExecution"""
    scheduled_report_name = serializers.CharField(source='scheduled_report.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReportExecution
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportExecutionListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des ReportExecution"""
    scheduled_report_name = serializers.CharField(source='scheduled_report.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'scheduled_report_name', 'template_name', 'status',
            'status_display', 'started_at', 'completed_at', 'duration',
            'file_path', 'file_size', 'record_count', 'created_at'
        ]



