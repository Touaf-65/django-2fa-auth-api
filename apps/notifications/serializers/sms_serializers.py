"""
Sérialiseurs pour les notifications SMS
"""

from rest_framework import serializers
from ..models import SMSNotification


class SMSNotificationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les notifications SMS
    """
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    user_email = serializers.EmailField(source='notification.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    status = serializers.CharField(source='notification.status', read_only=True)
    status_display = serializers.CharField(source='notification.get_status_display', read_only=True)
    
    class Meta:
        model = SMSNotification
        fields = [
            'id',
            'notification_id',
            'user_email',
            'user_name',
            'to_phone',
            'message',
            'twilio_sid',
            'twilio_status',
            'twilio_error_code',
            'twilio_error_message',
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
            'status',
            'status_display',
            'twilio_sid',
            'twilio_status',
            'twilio_error_code',
            'twilio_error_message',
            'created_at',
            'updated_at',
        ]
    
    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        if obj.notification.user.first_name and obj.notification.user.last_name:
            return f"{obj.notification.user.first_name} {obj.notification.user.last_name}"
        return obj.notification.user.email
    
    def validate_to_phone(self, value):
        """Valide le numéro de téléphone"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le numéro de téléphone est requis.")
        
        # Validation basique du format
        import re
        cleaned = re.sub(r'[^\d+]', '', value)
        if len(cleaned) < 10:
            raise serializers.ValidationError("Le numéro de téléphone doit contenir au moins 10 chiffres.")
        
        return value.strip()
    
    def validate_message(self, value):
        """Valide le message SMS"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le message est requis.")
        
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le message doit contenir au moins 5 caractères.")
        
        if len(value) > 1600:
            raise serializers.ValidationError("Le message ne peut pas dépasser 1600 caractères.")
        
        return value.strip()


class SMSSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi de SMS
    """
    user_id = serializers.IntegerField(required=True)
    to_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    message = serializers.CharField(max_length=1600, required=True)
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
    
    def validate_to_phone(self, value):
        """Valide le numéro de téléphone"""
        if value:
            import re
            cleaned = re.sub(r'[^\d+]', '', value)
            if len(cleaned) < 10:
                raise serializers.ValidationError("Le numéro de téléphone doit contenir au moins 10 chiffres.")
        return value
    
    def validate_message(self, value):
        """Valide le message"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le message doit contenir au moins 5 caractères.")
        
        if len(value) > 1600:
            raise serializers.ValidationError("Le message ne peut pas dépasser 1600 caractères.")
        
        return value.strip()
    
    def validate(self, data):
        """Validation globale"""
        user_id = data.get('user_id')
        to_phone = data.get('to_phone')
        
        # Si pas de numéro fourni, vérifier que l'utilisateur en a un
        if not to_phone:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                if not user.phone:
                    raise serializers.ValidationError("Aucun numéro de téléphone fourni et l'utilisateur n'en a pas de configuré.")
            except User.DoesNotExist:
                pass
        
        return data


class SMSBulkSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi de SMS en masse
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    message = serializers.CharField(max_length=1600, required=True)
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
    
    def validate_message(self, value):
        """Valide le message"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le message doit contenir au moins 5 caractères.")
        
        if len(value) > 1600:
            raise serializers.ValidationError("Le message ne peut pas dépasser 1600 caractères.")
        
        return value.strip()
    
    def validate(self, data):
        """Validation globale"""
        user_ids = data.get('user_ids')
        
        # Vérifier que tous les utilisateurs ont un numéro de téléphone
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users_without_phone = User.objects.filter(
            id__in=user_ids,
            phone__isnull=True
        ).values_list('id', flat=True)
        
        if users_without_phone:
            raise serializers.ValidationError(
                f"Les utilisateurs suivants n'ont pas de numéro de téléphone: {list(users_without_phone)}"
            )
        
        return data
