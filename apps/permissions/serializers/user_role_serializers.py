"""
Serializers pour les rôles utilisateur
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import UserRole, Role

User = get_user_model()


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rôles utilisateur
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_description = serializers.CharField(source='role.description', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.email', read_only=True)
    is_expired = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'role',
            'role_name',
            'role_description',
            'is_active',
            'expires_at',
            'is_expired',
            'remaining_time',
            'assigned_by',
            'assigned_by_username',
            'assigned_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """
        Retourne si le rôle est expiré
        """
        return obj.is_expired()
    
    def get_remaining_time(self, obj):
        """
        Retourne le temps restant avant expiration
        """
        remaining = obj.get_remaining_time()
        if remaining:
            return {
                'days': remaining.days,
                'hours': remaining.seconds // 3600,
                'total_seconds': int(remaining.total_seconds())
            }
        return None


class UserRoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de rôles utilisateur
    """
    class Meta:
        model = UserRole
        fields = [
            'user',
            'role',
            'expires_at',
        ]
    
    def validate_user(self, value):
        """
        Valide que l'utilisateur est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("L'utilisateur doit être actif.")
        return value
    
    def validate_role(self, value):
        """
        Valide que le rôle est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("Le rôle doit être actif.")
        return value
    
    def validate_expires_at(self, value):
        """
        Valide la date d'expiration
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date d'expiration doit être dans le futur.")
        return value
    
    def validate(self, data):
        """
        Validation globale
        """
        user = data.get('user')
        role = data.get('role')
        
        # Vérifier qu'il n'y a pas déjà une assignation active
        if user and role:
            existing = UserRole.objects.filter(
                user=user,
                role=role,
                is_active=True
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    "Cet utilisateur a déjà ce rôle assigné."
                )
        
        return data


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour de rôles utilisateur
    """
    class Meta:
        model = UserRole
        fields = [
            'is_active',
            'expires_at',
        ]
    
    def validate_expires_at(self, value):
        """
        Valide la date d'expiration
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date d'expiration doit être dans le futur.")
        return value


class UserRoleListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de rôles utilisateur
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id',
            'user',
            'user_email',
            'role',
            'role_name',
            'is_active',
            'expires_at',
            'is_expired',
            'assigned_at',
        ]
    
    def get_is_expired(self, obj):
        """
        Retourne si le rôle est expiré
        """
        return obj.is_expired()


class UserRoleStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des rôles utilisateur
    """
    total_assignments = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    expired_assignments = serializers.IntegerField()
    assignments_by_role = serializers.DictField()
    users_with_roles = serializers.IntegerField()

