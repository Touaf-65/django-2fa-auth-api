"""
Serializers pour AdminAction
"""
from rest_framework import serializers
from apps.admin_api.models import AdminAction


class AdminActionSerializer(serializers.ModelSerializer):
    """Serializer complet pour AdminAction"""
    admin_user_email = serializers.CharField(source='admin_user.email', read_only=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'started_at', 'completed_at', 'duration']


class AdminActionListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AdminAction"""
    admin_user_email = serializers.CharField(source='admin_user.email', read_only=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AdminAction
        fields = [
            'id', 'action_type', 'action_type_display', 'status', 'status_display',
            'priority', 'title', 'admin_user_email', 'target_user_email',
            'created_at', 'started_at', 'completed_at', 'duration'
        ]


class AdminActionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une AdminAction"""
    
    class Meta:
        model = AdminAction
        fields = [
            'action_type', 'priority', 'title', 'description', 'details',
            'target_user', 'ip_address', 'user_agent', 'session_key'
        ]
    
    def create(self, validated_data):
        validated_data['admin_user'] = self.context['request'].user
        return super().create(validated_data)


class AdminActionUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une AdminAction"""
    
    class Meta:
        model = AdminAction
        fields = ['status', 'result', 'error_message']
        read_only_fields = ['action_type', 'admin_user', 'target_user']



