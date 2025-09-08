"""
Serializers pour les gestionnaires de permissions
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import PermissionManager

User = get_user_model()


class PermissionManagerSerializer(serializers.ModelSerializer):
    """
    Serializer pour les gestionnaires de permissions
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.email', read_only=True)
    permissions_summary = serializers.SerializerMethodField()
    delegation_constraints = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionManager
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'can_create_permissions',
            'can_modify_permissions',
            'can_delete_permissions',
            'can_create_roles',
            'can_modify_roles',
            'can_delete_roles',
            'can_assign_roles',
            'can_create_groups',
            'can_modify_groups',
            'can_delete_groups',
            'can_manage_groups',
            'can_delegate_permissions',
            'can_delegate_roles',
            'max_delegation_duration_days',
            'max_delegation_uses',
            'allowed_apps',
            'allowed_models',
            'is_active',
            'assigned_by',
            'assigned_by_username',
            'assigned_at',
            'updated_at',
            'permissions_summary',
            'delegation_constraints',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']
    
    def get_permissions_summary(self, obj):
        """
        Retourne un résumé des permissions du gestionnaire
        """
        return obj.get_permissions_summary()
    
    def get_delegation_constraints(self, obj):
        """
        Retourne les contraintes de délégation
        """
        return obj.get_delegation_constraints()


class PermissionManagerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des gestionnaires de permissions
    """
    class Meta:
        model = PermissionManager
        fields = [
            'can_create_permissions',
            'can_modify_permissions',
            'can_delete_permissions',
            'can_create_roles',
            'can_modify_roles',
            'can_delete_roles',
            'can_assign_roles',
            'can_create_groups',
            'can_modify_groups',
            'can_delete_groups',
            'can_manage_groups',
            'can_delegate_permissions',
            'can_delegate_roles',
            'max_delegation_duration_days',
            'max_delegation_uses',
            'allowed_apps',
            'allowed_models',
            'is_active',
        ]
    
    def validate_max_delegation_duration_days(self, value):
        """
        Valide la durée maximale de délégation
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("La durée maximale doit être positive.")
        return value
    
    def validate_max_delegation_uses(self, value):
        """
        Valide le nombre maximum d'utilisations de délégation
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Le nombre maximum d'utilisations doit être positif.")
        return value
    
    def validate_allowed_apps(self, value):
        """
        Valide la liste des applications autorisées
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Les applications autorisées doivent être une liste.")
        
        for app in value:
            if not isinstance(app, str) or not app.strip():
                raise serializers.ValidationError("Chaque application doit être une chaîne non vide.")
        
        return value
    
    def validate_allowed_models(self, value):
        """
        Valide la liste des modèles autorisés
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Les modèles autorisés doivent être une liste.")
        
        for model in value:
            if not isinstance(model, str) or not model.strip():
                raise serializers.ValidationError("Chaque modèle doit être une chaîne non vide.")
        
        return value


class PermissionManagerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de gestionnaires de permissions
    """
    class Meta:
        model = PermissionManager
        fields = [
            'user',
            'can_create_permissions',
            'can_modify_permissions',
            'can_delete_permissions',
            'can_create_roles',
            'can_modify_roles',
            'can_delete_roles',
            'can_assign_roles',
            'can_create_groups',
            'can_modify_groups',
            'can_delete_groups',
            'can_manage_groups',
            'can_delegate_permissions',
            'can_delegate_roles',
            'max_delegation_duration_days',
            'max_delegation_uses',
            'allowed_apps',
            'allowed_models',
        ]
    
    def validate_user(self, value):
        """
        Valide que l'utilisateur est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("L'utilisateur doit être actif.")
        return value
    
    def validate(self, data):
        """
        Validation globale
        """
        # Vérifier qu'il n'y a pas déjà un gestionnaire pour cet utilisateur
        user = data.get('user')
        if user and PermissionManager.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "Cet utilisateur a déjà un profil de gestionnaire de permissions."
            )
        
        return data


class PermissionManagerListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de gestionnaires de permissions
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PermissionManager
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'can_create_permissions',
            'can_modify_permissions',
            'can_delete_permissions',
            'can_create_roles',
            'can_modify_roles',
            'can_delete_roles',
            'can_assign_roles',
            'can_create_groups',
            'can_modify_groups',
            'can_delete_groups',
            'can_manage_groups',
            'can_delegate_permissions',
            'can_delegate_roles',
            'is_active',
        ]


class PermissionManagerStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des gestionnaires de permissions
    """
    total_managers = serializers.IntegerField()
    active_managers = serializers.IntegerField()
    managers_with_delegation_rights = serializers.IntegerField()
    managers_with_role_management = serializers.IntegerField()
    managers_with_group_management = serializers.IntegerField()

