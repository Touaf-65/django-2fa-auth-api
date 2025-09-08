"""
Sérialiseurs pour les relations entre utilisateurs
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import UserFollow, UserBlock

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'affichage des utilisateurs dans les listes
    """
    profile = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_verified',
            'two_factor_enabled',
            'created_at',
            'last_activity',
            'profile',
            'followers_count',
            'following_count',
            'is_following',
            'is_followed_by',
            'is_blocked',
        ]
        read_only_fields = [
            'id',
            'email',
            'is_verified',
            'two_factor_enabled',
            'created_at',
            'last_activity',
            'profile',
            'followers_count',
            'following_count',
            'is_following',
            'is_followed_by',
            'is_blocked',
        ]
    
    def get_profile(self, obj):
        """Retourne les informations du profil"""
        try:
            from .user_profile_serializers import UserProfileSummarySerializer
            profile = obj.user_profile
            return UserProfileSummarySerializer(profile, context=self.context).data
        except:
            return None
    
    def get_followers_count(self, obj):
        """Retourne le nombre d'abonnés"""
        return UserFollow.get_followers_count(obj)
    
    def get_following_count(self, obj):
        """Retourne le nombre d'utilisateurs suivis"""
        return UserFollow.get_following_count(obj)
    
    def get_is_following(self, obj):
        """Vérifie si l'utilisateur connecté suit cet utilisateur"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.is_following(request.user, obj)
        return False
    
    def get_is_followed_by(self, obj):
        """Vérifie si cet utilisateur suit l'utilisateur connecté"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.is_following(obj, request.user)
        return False
    
    def get_is_blocked(self, obj):
        """Vérifie si l'utilisateur est bloqué"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserBlock.is_blocked(request.user, obj)
        return False


class UserFollowSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les relations de suivi
    """
    follower_email = serializers.EmailField(source='follower.email', read_only=True)
    follower_name = serializers.SerializerMethodField()
    following_email = serializers.EmailField(source='following.email', read_only=True)
    following_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFollow
        fields = [
            'id',
            'follower',
            'follower_email',
            'follower_name',
            'following',
            'following_email',
            'following_name',
            'created_at',
            'is_active',
        ]
        read_only_fields = [
            'id',
            'follower',
            'follower_email',
            'follower_name',
            'following_email',
            'following_name',
            'created_at',
        ]
    
    def get_follower_name(self, obj):
        """Retourne le nom complet du follower"""
        if obj.follower.first_name and obj.follower.last_name:
            return f"{obj.follower.first_name} {obj.follower.last_name}"
        return obj.follower.email
    
    def get_following_name(self, obj):
        """Retourne le nom complet de l'utilisateur suivi"""
        if obj.following.first_name and obj.following.last_name:
            return f"{obj.following.first_name} {obj.following.last_name}"
        return obj.following.email
    
    def validate_following(self, value):
        """Valide que l'utilisateur ne peut pas se suivre lui-même"""
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("Vous ne pouvez pas vous suivre vous-même.")
        return value
    
    def create(self, validated_data):
        """Crée une relation de suivi"""
        follower = validated_data.get('follower')
        following = validated_data.get('following')
        
        # Vérifier si l'utilisateur est bloqué
        if UserBlock.is_blocked(follower, following):
            raise serializers.ValidationError("Vous ne pouvez pas suivre cet utilisateur.")
        
        # Créer ou réactiver la relation de suivi
        follow, created = UserFollow.follow_user(follower, following)
        
        # Enregistrer l'activité
        request = self.context.get('request')
        if request:
            from ..models import UserActivity
            UserActivity.log_activity(
                user=follower,
                activity_type='login',  # Utiliser un type existant
                description=f'A commencé à suivre {following.email}',
                request=request
            )
        
        return follow


class UserBlockSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les blocages d'utilisateurs
    """
    blocker_email = serializers.EmailField(source='blocker.email', read_only=True)
    blocker_name = serializers.SerializerMethodField()
    blocked_email = serializers.EmailField(source='blocked.email', read_only=True)
    blocked_name = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = UserBlock
        fields = [
            'id',
            'blocker',
            'blocker_email',
            'blocker_name',
            'blocked',
            'blocked_email',
            'blocked_name',
            'reason',
            'reason_display',
            'description',
            'created_at',
            'is_active',
        ]
        read_only_fields = [
            'id',
            'blocker',
            'blocker_email',
            'blocker_name',
            'blocked_email',
            'blocked_name',
            'reason_display',
            'created_at',
        ]
    
    def get_blocker_name(self, obj):
        """Retourne le nom complet du blocker"""
        if obj.blocker.first_name and obj.blocker.last_name:
            return f"{obj.blocker.first_name} {obj.blocker.last_name}"
        return obj.blocker.email
    
    def get_blocked_name(self, obj):
        """Retourne le nom complet de l'utilisateur bloqué"""
        if obj.blocked.first_name and obj.blocked.last_name:
            return f"{obj.blocked.first_name} {obj.blocked.last_name}"
        return obj.blocked.email
    
    def validate_blocked(self, value):
        """Valide que l'utilisateur ne peut pas se bloquer lui-même"""
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("Vous ne pouvez pas vous bloquer vous-même.")
        return value
    
    def validate_description(self, value):
        """Valide la description du blocage"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La description doit contenir au moins 10 caractères."
            )
        return value
    
    def create(self, validated_data):
        """Crée un blocage d'utilisateur"""
        blocker = validated_data.get('blocker')
        blocked = validated_data.get('blocked')
        reason = validated_data.get('reason', 'other')
        description = validated_data.get('description', '')
        
        # Créer le blocage
        block = UserBlock.block_user(blocker, blocked, reason, description)
        
        # Enregistrer l'activité
        request = self.context.get('request')
        if request:
            from ..models import UserActivity
            UserActivity.log_activity(
                user=blocker,
                activity_type='security_alert',
                description=f'A bloqué {blocked.email}',
                request=request
            )
        
        return block


class UserSearchSerializer(serializers.Serializer):
    """
    Sérialiseur pour la recherche d'utilisateurs
    """
    query = serializers.CharField(
        max_length=100,
        help_text="Terme de recherche (nom, email, etc.)"
    )
    limit = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text="Nombre maximum de résultats"
    )
    include_blocked = serializers.BooleanField(
        default=False,
        help_text="Inclure les utilisateurs bloqués"
    )
    
    def validate_query(self, value):
        """Valide le terme de recherche"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le terme de recherche doit contenir au moins 2 caractères."
            )
        return value.strip()


class UserStatsSerializer(serializers.Serializer):
    """
    Sérialiseur pour les statistiques d'un utilisateur
    """
    user_id = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    blocked_count = serializers.IntegerField(read_only=True)
    blocked_by_count = serializers.IntegerField(read_only=True)
    profile_views = serializers.IntegerField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)
    account_age_days = serializers.IntegerField(read_only=True)
    
    def to_representation(self, instance):
        """Calcule les statistiques de l'utilisateur"""
        from django.utils import timezone
        
        data = {
            'user_id': instance.id,
            'user_email': instance.email,
            'followers_count': UserFollow.get_followers_count(instance),
            'following_count': UserFollow.get_following_count(instance),
            'blocked_count': len(UserBlock.get_blocked_users(instance)),
            'blocked_by_count': len(UserBlock.get_blocked_by_users(instance)),
            'profile_views': 0,  # À implémenter si nécessaire
            'last_activity': instance.last_activity,
        }
        
        # Calculer l'âge du compte
        if instance.created_at:
            account_age = timezone.now() - instance.created_at
            data['account_age_days'] = account_age.days
        else:
            data['account_age_days'] = 0
        
        return data

