"""
Serializers pour AdminLog
"""
from rest_framework import serializers
from apps.admin_api.models import AdminLog


class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer complet pour AdminLog"""
    admin_user_email = serializers.CharField(source='admin_user.email', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminLogListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AdminLog"""
    admin_user_email = serializers.CharField(source='admin_user.email', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = [
            'id', 'level', 'level_display', 'action', 'target_model',
            'admin_user_email', 'message', 'created_at'
        ]

