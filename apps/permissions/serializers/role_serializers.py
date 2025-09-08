"""
Serializers pour les rôles
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Role, RolePermission, Permission
from .permission_serializers import PermissionSerializer

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rôles
    """
    created_by_username = serializers.CharField(source='created_by.email', read_only=True)
    permission_count = serializers.SerializerMethodField()
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'permissions',
            'permission_count',
            'is_active',
            'is_system',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permission_count(self, obj):
        """
        Retourne le nombre de permissions du rôle
        """
        return obj.get_permission_count()


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de rôles
    """
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des permissions à assigner au rôle"
    )
    
    class Meta:
        model = Role
        fields = [
            'name',
            'description',
            'permission_ids',
            'is_system',
        ]
    
    def validate_name(self, value):
        """
        Valide l'unicité du nom du rôle
        """
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("Un rôle avec ce nom existe déjà.")
        return value
    
    def create(self, validated_data):
        """
        Crée le rôle avec ses permissions
        """
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        # Assigner les permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
            for permission in permissions:
                role.add_permission(permission)
        
        return role


class RoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour de rôles
    """
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des permissions à assigner au rôle"
    )
    
    class Meta:
        model = Role
        fields = [
            'name',
            'description',
            'permission_ids',
            'is_active',
        ]
    
    def validate_name(self, value):
        """
        Valide l'unicité du nom du rôle
        """
        if self.instance and Role.objects.filter(name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Un rôle avec ce nom existe déjà.")
        return value
    
    def update(self, instance, validated_data):
        """
        Met à jour le rôle et ses permissions
        """
        permission_ids = validated_data.pop('permission_ids', None)
        
        # Mettre à jour les champs du rôle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les permissions si fournies
        if permission_ids is not None:
            # Supprimer toutes les permissions existantes
            instance.permissions.clear()
            
            # Ajouter les nouvelles permissions
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
                for permission in permissions:
                    instance.add_permission(permission)
        
        return instance


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les permissions de rôles
    """
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id',
            'role',
            'role_name',
            'permission',
            'permission_name',
            'permission_codename',
            'granted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de rôles
    """
    permission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'permission_count',
            'is_active',
            'is_system',
        ]
    
    def get_permission_count(self, obj):
        """
        Retourne le nombre de permissions du rôle
        """
        return obj.get_permission_count()


class RoleStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des rôles
    """
    total_roles = serializers.IntegerField()
    system_roles = serializers.IntegerField()
    custom_roles = serializers.IntegerField()
    active_roles = serializers.IntegerField()
    roles_with_permissions = serializers.IntegerField()
