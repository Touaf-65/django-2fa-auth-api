"""
Serializers pour les permissions
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Permission, ConditionalPermission

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les permissions
    """
    created_by_username = serializers.CharField(source='created_by.email', read_only=True)
    is_custom_display = serializers.CharField(source='get_is_custom_display', read_only=True)
    
    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'description',
            'app_label',
            'model',
            'action',
            'field_name',
            'min_value',
            'max_value',
            'conditions',
            'is_custom',
            'is_custom_display',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de permissions
    """
    class Meta:
        model = Permission
        fields = [
            'name',
            'codename',
            'description',
            'app_label',
            'model',
            'action',
            'field_name',
            'min_value',
            'max_value',
            'conditions',
        ]
    
    def validate_codename(self, value):
        """
        Valide l'unicité du code de permission
        """
        if Permission.objects.filter(codename=value).exists():
            raise serializers.ValidationError("Une permission avec ce code existe déjà.")
        return value
    
    def validate(self, data):
        """
        Validation globale
        """
        # Vérifier que si field_name est fourni, les contraintes de valeur sont cohérentes
        if data.get('field_name'):
            min_value = data.get('min_value')
            max_value = data.get('max_value')
            
            if min_value is not None and max_value is not None:
                if min_value > max_value:
                    raise serializers.ValidationError(
                        "La valeur minimale ne peut pas être supérieure à la valeur maximale."
                    )
        
        return data


class PermissionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour de permissions
    """
    class Meta:
        model = Permission
        fields = [
            'name',
            'description',
            'field_name',
            'min_value',
            'max_value',
            'conditions',
            'is_active',
        ]
    
    def validate(self, data):
        """
        Validation globale
        """
        # Vérifier les contraintes de valeur
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise serializers.ValidationError(
                    "La valeur minimale ne peut pas être supérieure à la valeur maximale."
                )
        
        return data


class ConditionalPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les permissions conditionnelles
    """
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    condition_type_display = serializers.CharField(source='get_condition_type_display', read_only=True)
    
    class Meta:
        model = ConditionalPermission
        fields = [
            'id',
            'permission',
            'permission_name',
            'permission_codename',
            'condition_type',
            'condition_type_display',
            'condition_data',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de permissions
    """
    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'app_label',
            'model',
            'action',
            'field_name',
            'is_active',
        ]


class PermissionStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des permissions
    """
    total_permissions = serializers.IntegerField()
    custom_permissions = serializers.IntegerField()
    active_permissions = serializers.IntegerField()
    permissions_by_app = serializers.DictField()
    permissions_by_action = serializers.DictField()



