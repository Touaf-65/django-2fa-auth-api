"""
Sérialiseurs pour les profils utilisateur
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import UserProfile, UserPreference, UserActivity

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'affichage des profils utilisateur
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    user_created_at = serializers.DateTimeField(source='user.created_at', read_only=True)
    user_is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    user_two_factor_enabled = serializers.BooleanField(source='user.two_factor_enabled', read_only=True)
    
    # Champs calculés
    display_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            # Informations de base
            'user_email',
            'user_first_name', 
            'user_last_name',
            'user_avatar',
            'user_created_at',
            'user_is_verified',
            'user_two_factor_enabled',
            'display_name',
            'age',
            
            # Informations personnelles
            'bio',
            'birth_date',
            'gender',
            'location',
            'website',
            
            # Informations professionnelles
            'job_title',
            'company',
            'industry',
            
            # Réseaux sociaux
            'linkedin_url',
            'twitter_handle',
            'github_username',
            
            # Paramètres de confidentialité
            'profile_visibility',
            'show_email',
            'show_phone',
            'show_birth_date',
            
            # Métadonnées
            'created_at',
            'updated_at',
            'last_profile_update',
        ]
        read_only_fields = [
            'user_email',
            'user_first_name',
            'user_last_name', 
            'user_avatar',
            'user_created_at',
            'user_is_verified',
            'user_two_factor_enabled',
            'display_name',
            'age',
            'created_at',
            'updated_at',
            'last_profile_update',
        ]
    
    def get_display_name(self, obj):
        """Retourne le nom d'affichage complet"""
        return obj.get_display_name()
    
    def get_age(self, obj):
        """Retourne l'âge de l'utilisateur"""
        return obj.get_age()
    
    def to_representation(self, instance):
        """Filtre les champs selon la visibilité du profil"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Si c'est le propriétaire du profil, afficher toutes les informations
        if request and request.user == instance.user:
            return data
        
        # Sinon, respecter les paramètres de confidentialité
        if not instance.show_email:
            data.pop('user_email', None)
        if not instance.show_birth_date:
            data.pop('birth_date', None)
            data.pop('age', None)
        
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour des profils utilisateur
    """
    
    class Meta:
        model = UserProfile
        fields = [
            # Informations personnelles
            'bio',
            'birth_date',
            'gender',
            'location',
            'website',
            
            # Informations professionnelles
            'job_title',
            'company',
            'industry',
            
            # Réseaux sociaux
            'linkedin_url',
            'twitter_handle',
            'github_username',
            
            # Paramètres de confidentialité
            'profile_visibility',
            'show_email',
            'show_phone',
            'show_birth_date',
        ]
    
    def validate_bio(self, value):
        """Valide la biographie"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La biographie doit contenir au moins 10 caractères."
            )
        return value
    
    def validate_website(self, value):
        """Valide l'URL du site web"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "L'URL doit commencer par http:// ou https://"
            )
        return value
    
    def validate_linkedin_url(self, value):
        """Valide l'URL LinkedIn"""
        if value and 'linkedin.com' not in value:
            raise serializers.ValidationError(
                "L'URL doit être une URL LinkedIn valide"
            )
        return value
    
    def validate_twitter_handle(self, value):
        """Valide le handle Twitter"""
        if value and not value.startswith('@'):
            value = f'@{value}'
        return value
    
    def update(self, instance, validated_data):
        """Met à jour le profil et enregistre l'activité"""
        # Mettre à jour le profil
        instance = super().update(instance, validated_data)
        
        # Enregistrer l'activité
        request = self.context.get('request')
        if request:
            UserActivity.log_activity(
                user=instance.user,
                activity_type='profile_update',
                description='Profil mis à jour',
                request=request
            )
        
        # Mettre à jour la date de dernière modification
        instance.update_last_profile_update()
        
        return instance


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les préférences utilisateur
    """
    
    class Meta:
        model = UserPreference
        fields = [
            # Préférences d'interface
            'theme',
            'language',
            'timezone',
            
            # Préférences de notification
            'email_notifications',
            'push_notifications',
            'sms_notifications',
            
            # Types de notifications
            'notify_new_followers',
            'notify_new_messages',
            'notify_system_updates',
            'notify_security_alerts',
            
            # Préférences de confidentialité
            'allow_search_engines',
            'show_online_status',
            'allow_friend_requests',
            
            # Métadonnées
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_language(self, value):
        """Valide la langue"""
        valid_languages = ['en', 'fr', 'es', 'de']
        if value not in valid_languages:
            raise serializers.ValidationError(
                f"Langue non supportée. Langues disponibles: {', '.join(valid_languages)}"
            )
        return value
    
    def validate_theme(self, value):
        """Valide le thème"""
        valid_themes = ['light', 'dark', 'auto']
        if value not in valid_themes:
            raise serializers.ValidationError(
                f"Thème non supporté. Thèmes disponibles: {', '.join(valid_themes)}"
            )
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'historique des activités utilisateur
    """
    activity_type_display = serializers.CharField(
        source='get_activity_type_display',
        read_only=True
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id',
            'user_email',
            'activity_type',
            'activity_type_display',
            'description',
            'ip_address',
            'device_info',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user_email',
            'activity_type_display',
            'ip_address',
            'device_info',
            'created_at',
        ]
    
    def to_representation(self, instance):
        """Formate les données pour l'affichage"""
        data = super().to_representation(instance)
        
        # Formater la date
        if data.get('created_at'):
            data['created_at'] = instance.created_at.strftime('%d/%m/%Y %H:%M')
        
        # Formater les informations du device
        device_info = data.get('device_info', {})
        if device_info:
            data['device_summary'] = f"{device_info.get('browser', 'Unknown')} sur {device_info.get('os', 'Unknown')}"
        else:
            data['device_summary'] = 'Unknown'
        
        return data


class UserProfileSummarySerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour un résumé de profil utilisateur (pour les listes)
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    user_is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    
    display_name = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'user_first_name',
            'user_last_name', 
            'user_avatar',
            'user_is_verified',
            'display_name',
            'bio',
            'location',
            'job_title',
            'company',
            'profile_visibility',
            'followers_count',
            'following_count',
            'created_at',
        ]
        read_only_fields = [
            'user_email',
            'user_first_name',
            'user_last_name',
            'user_avatar', 
            'user_is_verified',
            'display_name',
            'followers_count',
            'following_count',
            'created_at',
        ]
    
    def get_display_name(self, obj):
        """Retourne le nom d'affichage complet"""
        return obj.get_display_name()
    
    def get_followers_count(self, obj):
        """Retourne le nombre d'abonnés"""
        from ..models import UserFollow
        return UserFollow.get_followers_count(obj.user)
    
    def get_following_count(self, obj):
        """Retourne le nombre d'utilisateurs suivis"""
        from ..models import UserFollow
        return UserFollow.get_following_count(obj.user)



