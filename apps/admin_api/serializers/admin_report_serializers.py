"""
Serializers pour AdminReport
"""
from rest_framework import serializers
from apps.admin_api.models import AdminReport


class AdminReportSerializer(serializers.ModelSerializer):
    """Serializer complet pour AdminReport"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = AdminReport
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminReportListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AdminReport"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = AdminReport
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'description',
            'created_by_email', 'is_scheduled', 'created_at'
        ]


class AdminReportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une AdminReport"""
    
    class Meta:
        model = AdminReport
        fields = [
            'name', 'report_type', 'description', 'parameters',
            'is_scheduled', 'schedule_cron'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

