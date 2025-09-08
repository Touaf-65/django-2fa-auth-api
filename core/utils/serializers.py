"""
Serializers de base pour l'application Core
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseSerializer(serializers.ModelSerializer):
    """Serializer de base avec fonctionnalités communes"""
    
    class Meta:
        abstract = True
    
    def create(self, validated_data):
        """Création avec attribution automatique du créateur"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Mise à jour avec attribution automatique du modificateur"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class TimestampedSerializer(BaseSerializer):
    """Serializer pour les modèles avec timestamps"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


class SoftDeleteSerializer(BaseSerializer):
    """Serializer pour les modèles avec suppression douce"""
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)
    deleted_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        abstract = True


class StatusSerializer(BaseSerializer):
    """Serializer pour les modèles avec statut"""
    status = serializers.ChoiceField(choices=[
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('archived', 'Archivé'),
    ])
    
    class Meta:
        abstract = True


class OrderingSerializer(BaseSerializer):
    """Serializer pour les modèles avec ordre"""
    order = serializers.IntegerField(min_value=0)
    
    class Meta:
        abstract = True


class SlugSerializer(BaseSerializer):
    """Serializer pour les modèles avec slug"""
    slug = serializers.SlugField(read_only=True)
    
    class Meta:
        abstract = True


class CacheSerializer(BaseSerializer):
    """Serializer pour les modèles avec cache"""
    cache_key = serializers.CharField(read_only=True)
    cache_data = serializers.JSONField(read_only=True)
    cache_expires_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


class CreatedBySerializer(BaseSerializer):
    """Serializer pour les modèles avec créateur"""
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        abstract = True


class UpdatedBySerializer(BaseSerializer):
    """Serializer pour les modèles avec modificateur"""
    updated_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        abstract = True



