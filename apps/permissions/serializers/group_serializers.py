"""
Serializers pour les groupes
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Group, GroupMembership, GroupRole, Role

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer pour les groupes
    """
    created_by_username = serializers.CharField(source='created_by.email', read_only=True)
    user_count = serializers.SerializerMethodField()
    role_count = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'description',
            'users',
            'roles',
            'user_count',
            'role_count',
            'is_active',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """
        Retourne le nombre d'utilisateurs du groupe
        """
        return obj.get_user_count()
    
    def get_role_count(self, obj):
        """
        Retourne le nombre de rôles du groupe
        """
        return obj.get_roles().count()
    
    def get_users(self, obj):
        """
        Retourne les utilisateurs du groupe
        """
        users = obj.get_users()
        return [{'id': user.id, 'email': user.email, 'username': getattr(user, 'username', user.email)} for user in users]
    
    def get_roles(self, obj):
        """
        Retourne les rôles du groupe
        """
        roles = obj.get_roles()
        return [{'id': role.id, 'name': role.name, 'description': role.description} for role in roles]


class GroupCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de groupes
    """
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des rôles à assigner au groupe"
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des utilisateurs à ajouter au groupe"
    )
    
    class Meta:
        model = Group
        fields = [
            'name',
            'description',
            'role_ids',
            'user_ids',
        ]
    
    def validate_name(self, value):
        """
        Valide l'unicité du nom du groupe
        """
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("Un groupe avec ce nom existe déjà.")
        return value
    
    def create(self, validated_data):
        """
        Crée le groupe avec ses rôles et utilisateurs
        """
        role_ids = validated_data.pop('role_ids', [])
        user_ids = validated_data.pop('user_ids', [])
        
        group = Group.objects.create(**validated_data)
        
        # Assigner les rôles
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids, is_active=True)
            for role in roles:
                group.add_role(role)
        
        # Ajouter les utilisateurs
        if user_ids:
            users = User.objects.filter(id__in=user_ids, is_active=True)
            for user in users:
                group.add_user(user)
        
        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour de groupes
    """
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des rôles à assigner au groupe"
    )
    
    class Meta:
        model = Group
        fields = [
            'name',
            'description',
            'role_ids',
            'is_active',
        ]
    
    def validate_name(self, value):
        """
        Valide l'unicité du nom du groupe
        """
        if self.instance and Group.objects.filter(name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Un groupe avec ce nom existe déjà.")
        return value
    
    def update(self, instance, validated_data):
        """
        Met à jour le groupe et ses rôles
        """
        role_ids = validated_data.pop('role_ids', None)
        
        # Mettre à jour les champs du groupe
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les rôles si fournis
        if role_ids is not None:
            # Supprimer tous les rôles existants
            instance.roles.clear()
            
            # Ajouter les nouveaux rôles
            if role_ids:
                roles = Role.objects.filter(id__in=role_ids, is_active=True)
                for role in roles:
                    instance.add_role(role)
        
        return instance


class GroupMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer pour les adhésions aux groupes
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    joined_by_username = serializers.CharField(source='joined_by.email', read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'group',
            'group_name',
            'is_active',
            'joined_by',
            'joined_by_username',
            'joined_at',
        ]
        read_only_fields = ['id', 'joined_at']


class GroupRoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rôles de groupes
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_description = serializers.CharField(source='role.description', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.email', read_only=True)
    
    class Meta:
        model = GroupRole
        fields = [
            'id',
            'group',
            'group_name',
            'role',
            'role_name',
            'role_description',
            'assigned_by',
            'assigned_by_username',
            'assigned_at',
        ]
        read_only_fields = ['id', 'assigned_at']


class GroupListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les listes de groupes
    """
    user_count = serializers.SerializerMethodField()
    role_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'description',
            'user_count',
            'role_count',
            'is_active',
        ]
    
    def get_user_count(self, obj):
        """
        Retourne le nombre d'utilisateurs du groupe
        """
        return obj.get_user_count()
    
    def get_role_count(self, obj):
        """
        Retourne le nombre de rôles du groupe
        """
        return obj.get_roles().count()


class GroupStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des groupes
    """
    total_groups = serializers.IntegerField()
    active_groups = serializers.IntegerField()
    groups_with_members = serializers.IntegerField()
    groups_with_roles = serializers.IntegerField()
    total_memberships = serializers.IntegerField()



