"""
Serializers pour SystemConfig
"""
from rest_framework import serializers
from apps.admin_api.models import SystemConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    """Serializer complet pour SystemConfig"""
    
    class Meta:
        model = SystemConfig
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemConfigListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des SystemConfig"""
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'category', 'description', 'is_public', 'is_encrypted', 'created_at']


class SystemConfigCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une SystemConfig"""
    
    class Meta:
        model = SystemConfig
        fields = ['key', 'value', 'description', 'category', 'is_public', 'is_encrypted']


class SystemConfigUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une SystemConfig"""
    
    class Meta:
        model = SystemConfig
        fields = ['value', 'description', 'is_public', 'is_encrypted']
        read_only_fields = ['key', 'category']

