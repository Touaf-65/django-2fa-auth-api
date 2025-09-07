"""
Sérialiseurs pour les notifications push
"""

from rest_framework import serializers
from ..models import PushNotification, PushToken


class PushTokenSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les tokens push
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    
    class Meta:
        model = PushToken
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'token',
            'device_type',
            'device_type_display',
            'device_id',
            'device_name',
            'app_version',
            'is_active',
            'created_at',
            'updated_at',
            'last_used_at',
        ]
        read_only_fields = [
            'id',
            'user_email',
            'user_name',
            'device_type_display',
            'created_at',
            'updated_at',
            'last_used_at',
        ]
    
    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email
    
    def validate_token(self, value):
        """Valide le token push"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le token push est requis.")
        
        if len(value.strip()) < 100:
            raise serializers.ValidationError("Le token push semble invalide.")
        
        return value.strip()
    
    def validate_device_type(self, value):
        """Valide le type de device"""
        valid_types = ['ios', 'android', 'web']
        if value not in valid_types:
            raise serializers.ValidationError(f"Type de device invalide. Types valides: {', '.join(valid_types)}")
        return value


class PushNotificationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les notifications push
    """
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    user_email = serializers.EmailField(source='push_token.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    device_type = serializers.CharField(source='push_token.device_type', read_only=True)
    device_name = serializers.CharField(source='push_token.device_name', read_only=True)
    status = serializers.CharField(source='notification.status', read_only=True)
    status_display = serializers.CharField(source='notification.get_status_display', read_only=True)
    
    class Meta:
        model = PushNotification
        fields = [
            'id',
            'notification_id',
            'user_email',
            'user_name',
            'push_token',
            'device_type',
            'device_name',
            'title',
            'body',
            'data',
            'sound',
            'badge',
            'fcm_message_id',
            'fcm_status',
            'context',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'notification_id',
            'user_email',
            'user_name',
            'device_type',
            'device_name',
            'status',
            'status_display',
            'fcm_message_id',
            'fcm_status',
            'created_at',
            'updated_at',
        ]
    
    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        if obj.push_token.user.first_name and obj.push_token.user.last_name:
            return f"{obj.push_token.user.first_name} {obj.push_token.user.last_name}"
        return obj.push_token.user.email
    
    def validate_title(self, value):
        """Valide le titre"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le titre est requis.")
        
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères.")
        
        if len(value) > 100:
            raise serializers.ValidationError("Le titre ne peut pas dépasser 100 caractères.")
        
        return value.strip()
    
    def validate_body(self, value):
        """Valide le corps du message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le corps du message est requis.")
        
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le corps du message doit contenir au moins 5 caractères.")
        
        if len(value) > 200:
            raise serializers.ValidationError("Le corps du message ne peut pas dépasser 200 caractères.")
        
        return value.strip()
    
    def validate_sound(self, value):
        """Valide le son"""
        if value and len(value) > 50:
            raise serializers.ValidationError("Le nom du son ne peut pas dépasser 50 caractères.")
        return value
    
    def validate_badge(self, value):
        """Valide le badge"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Le badge ne peut pas être négatif.")
        return value


class PushSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi de notifications push
    """
    user_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=100, required=True)
    body = serializers.CharField(max_length=200, required=True)
    data = serializers.JSONField(required=False, default=dict)
    sound = serializers.CharField(max_length=50, required=False, default='default')
    badge = serializers.IntegerField(required=False, allow_null=True)
    priority = serializers.ChoiceField(
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normal'),
            ('high', 'Élevé'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_user_id(self, value):
        """Valide l'ID de l'utilisateur"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")
        return value
    
    def validate_title(self, value):
        """Valide le titre"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_body(self, value):
        """Valide le corps du message"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le corps du message doit contenir au moins 5 caractères.")
        return value.strip()
    
    def validate(self, data):
        """Validation globale"""
        user_id = data.get('user_id')
        
        # Vérifier que l'utilisateur a des tokens push actifs
        from ..models import PushToken
        active_tokens = PushToken.objects.filter(
            user_id=user_id,
            is_active=True
        ).exists()
        
        if not active_tokens:
            raise serializers.ValidationError("L'utilisateur n'a aucun token push actif.")
        
        return data


class PushBulkSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi de notifications push en masse
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    title = serializers.CharField(max_length=100, required=True)
    body = serializers.CharField(max_length=200, required=True)
    data = serializers.JSONField(required=False, default=dict)
    sound = serializers.CharField(max_length=50, required=False, default='default')
    badge = serializers.IntegerField(required=False, allow_null=True)
    priority = serializers.ChoiceField(
        choices=[
            ('low', 'Faible'),
            ('normal', 'Normal'),
            ('high', 'Élevé'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_user_ids(self, value):
        """Valide les IDs des utilisateurs"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Vérifier que tous les utilisateurs existent
        existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_users)
        
        if missing_ids:
            raise serializers.ValidationError(f"Utilisateurs non trouvés: {list(missing_ids)}")
        
        return value
    
    def validate_title(self, value):
        """Valide le titre"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_body(self, value):
        """Valide le corps du message"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le corps du message doit contenir au moins 5 caractères.")
        return value.strip()


class PushTokenCreateSerializer(serializers.Serializer):
    """
    Sérialiseur pour la création de tokens push
    """
    token = serializers.CharField(required=True)
    device_type = serializers.ChoiceField(
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web'),
        ],
        required=True
    )
    device_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    device_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    app_version = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_token(self, value):
        """Valide le token push"""
        if len(value.strip()) < 100:
            raise serializers.ValidationError("Le token push semble invalide.")
        return value.strip()
    
    def validate_device_type(self, value):
        """Valide le type de device"""
        valid_types = ['ios', 'android', 'web']
        if value not in valid_types:
            raise serializers.ValidationError(f"Type de device invalide. Types valides: {', '.join(valid_types)}")
        return value
