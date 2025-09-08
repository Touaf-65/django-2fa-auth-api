"""
Serializers pour AdminDashboard
"""
from rest_framework import serializers
from apps.admin_api.models import AdminDashboard


class AdminDashboardSerializer(serializers.ModelSerializer):
    """Serializer complet pour AdminDashboard"""
    
    class Meta:
        model = AdminDashboard
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminDashboardListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des AdminDashboard"""
    
    class Meta:
        model = AdminDashboard
        fields = ['id', 'name', 'description', 'is_default', 'is_active', 'created_at']

