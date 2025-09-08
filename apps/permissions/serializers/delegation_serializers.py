"""
Serializers pour les délégations
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import PermissionDelegation, RoleDelegation, Permission, Role

User = get_user_model()


class PermissionDelegationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les délégations de permissions
    """
    delegator_email = serializers.CharField(source='delegator.email', read_only=True)
    delegatee_email = serializers.CharField(source='delegatee.email', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    is_valid = serializers.SerializerMethodField()
    remaining_uses = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionDelegation
        fields = [
            'id',
            'delegator',
            'delegator_email',
            'delegatee',
            'delegatee_email',
            'permission',
            'permission_name',
            'permission_codename',
            'start_date',
            'end_date',
            'max_uses',
            'current_uses',
            'allowed_ips',
            'allowed_actions',
            'conditions',
            'is_active',
            'is_valid',
            'remaining_uses',
            'remaining_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    
    def get_is_valid(self, obj):
        """
        Retourne si la délégation est valide
        """
        return obj.is_valid()
    
    def get_remaining_uses(self, obj):
        """
        Retourne le nombre d'utilisations restantes
        """
        return obj.get_remaining_uses()
    
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


class PermissionDelegationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de délégations de permissions
    """
    class Meta:
        model = PermissionDelegation
        fields = [
            'delegatee',
            'permission',
            'start_date',
            'end_date',
            'max_uses',
            'allowed_ips',
            'allowed_actions',
            'conditions',
        ]
    
    def validate_delegatee(self, value):
        """
        Valide que le délégué est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("Le délégué doit être actif.")
        return value
    
    def validate_permission(self, value):
        """
        Valide que la permission est active
        """
        if not value.is_active:
            raise serializers.ValidationError("La permission doit être active.")
        return value
    
    def validate_start_date(self, value):
        """
        Valide la date de début
        """
        if value and value < timezone.now():
            raise serializers.ValidationError("La date de début ne peut pas être dans le passé.")
        return value
    
    def validate_end_date(self, value):
        """
        Valide la date de fin
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date de fin doit être dans le futur.")
        return value
    
    def validate(self, data):
        """
        Validation globale
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        return data


class RoleDelegationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les délégations de rôles
    """
    delegator_email = serializers.CharField(source='delegator.email', read_only=True)
    delegatee_email = serializers.CharField(source='delegatee.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_description = serializers.CharField(source='role.description', read_only=True)
    excluded_permissions = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    remaining_uses = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = RoleDelegation
        fields = [
            'id',
            'delegator',
            'delegator_email',
            'delegatee',
            'delegatee_email',
            'role',
            'role_name',
            'role_description',
            'excluded_permissions',
            'start_date',
            'end_date',
            'max_uses',
            'current_uses',
            'allowed_ips',
            'is_active',
            'is_valid',
            'remaining_uses',
            'remaining_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    
    def get_excluded_permissions(self, obj):
        """
        Retourne les permissions exclues
        """
        return [{'id': p.id, 'name': p.name, 'codename': p.codename} for p in obj.excluded_permissions.all()]
    
    def get_is_valid(self, obj):
        """
        Retourne si la délégation est valide
        """
        return obj.is_valid()
    
    def get_remaining_uses(self, obj):
        """
        Retourne le nombre d'utilisations restantes
        """
        return obj.get_remaining_uses()
    
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


class RoleDelegationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de délégations de rôles
    """
    excluded_permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des permissions à exclure de la délégation"
    )
    
    class Meta:
        model = RoleDelegation
        fields = [
            'delegatee',
            'role',
            'excluded_permission_ids',
            'start_date',
            'end_date',
            'max_uses',
            'allowed_ips',
        ]
    
    def validate_delegatee(self, value):
        """
        Valide que le délégué est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("Le délégué doit être actif.")
        return value
    
    def validate_role(self, value):
        """
        Valide que le rôle est actif
        """
        if not value.is_active:
            raise serializers.ValidationError("Le rôle doit être actif.")
        return value
    
    def validate_start_date(self, value):
        """
        Valide la date de début
        """
        if value and value < timezone.now():
            raise serializers.ValidationError("La date de début ne peut pas être dans le passé.")
        return value
    
    def validate_end_date(self, value):
        """
        Valide la date de fin
        """
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date de fin doit être dans le futur.")
        return value
    
    def validate(self, data):
        """
        Validation globale
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        return data
    
    def create(self, validated_data):
        """
        Crée la délégation avec les permissions exclues
        """
        excluded_permission_ids = validated_data.pop('excluded_permission_ids', [])
        
        delegation = RoleDelegation.objects.create(**validated_data)
        
        # Ajouter les permissions exclues
        if excluded_permission_ids:
            permissions = Permission.objects.filter(id__in=excluded_permission_ids, is_active=True)
            delegation.excluded_permissions.set(permissions)
        
        return delegation


class DelegationStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des délégations
    """
    total_permission_delegations = serializers.IntegerField()
    active_permission_delegations = serializers.IntegerField()
    expired_permission_delegations = serializers.IntegerField()
    total_role_delegations = serializers.IntegerField()
    active_role_delegations = serializers.IntegerField()
    expired_role_delegations = serializers.IntegerField()
    delegations_by_permission = serializers.DictField()
    delegations_by_role = serializers.DictField()

