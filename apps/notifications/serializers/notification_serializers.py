"""
Sérialiseurs pour les notifications générales
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Notification, NotificationTemplate, NotificationLog

User = get_user_model()


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les templates de notifications
    """
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id',
            'name',
            'notification_type',
            'subject',
            'content',
            'html_content',
            'available_variables',
            'priority',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Valide le nom du template"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom doit contenir au moins 3 caractères.")
        return value.strip()
    
    def validate_content(self, value):
        """Valide le contenu du template"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le contenu doit contenir au moins 10 caractères.")
        return value.strip()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les notifications
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'notification_type',
            'notification_type_display',
            'template',
            'template_name',
            'subject',
            'content',
            'html_content',
            'recipient_email',
            'recipient_phone',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'scheduled_at',
            'sent_at',
            'delivered_at',
            'context',
            'metadata',
            'retry_count',
            'max_retries',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user_email',
            'user_name',
            'template_name',
            'status_display',
            'priority_display',
            'notification_type_display',
            'sent_at',
            'delivered_at',
            'retry_count',
            'created_at',
            'updated_at',
        ]
    
    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email
    
    def validate_recipient_email(self, value):
        """Valide l'email destinataire"""
        if value and not value.strip():
            raise serializers.ValidationError("L'email destinataire ne peut pas être vide.")
        return value.strip() if value else value
    
    def validate_recipient_phone(self, value):
        """Valide le téléphone destinataire"""
        if value and not value.strip():
            raise serializers.ValidationError("Le téléphone destinataire ne peut pas être vide.")
        return value.strip() if value else value
    
    def validate_scheduled_at(self, value):
        """Valide la date de planification"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date de planification doit être dans le futur.")
        return value


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les logs de notifications
    """
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id',
            'notification_id',
            'action',
            'action_display',
            'message',
            'details',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'notification_id',
            'action_display',
            'created_at',
        ]


class NotificationCreateSerializer(serializers.Serializer):
    """
    Sérialiseur pour la création de notifications
    """
    user_id = serializers.IntegerField(required=True)
    notification_type = serializers.ChoiceField(
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('push', 'Push'),
            ('in_app', 'In-App'),
        ],
        required=True
    )
    subject = serializers.CharField(max_length=200, required=False, allow_blank=True)
    content = serializers.CharField(required=True)
    template_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    context = serializers.JSONField(required=False, default=dict)
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
    recipient_email = serializers.EmailField(required=False, allow_blank=True)
    recipient_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_user_id(self, value):
        """Valide l'ID de l'utilisateur"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")
        return value
    
    def validate(self, data):
        """Validation globale"""
        notification_type = data.get('notification_type')
        recipient_email = data.get('recipient_email')
        recipient_phone = data.get('recipient_phone')
        
        # Vérifier que les champs requis sont présents selon le type
        if notification_type == 'email' and not recipient_email:
            raise serializers.ValidationError("L'email destinataire est requis pour les notifications email.")
        
        if notification_type == 'sms' and not recipient_phone:
            raise serializers.ValidationError("Le téléphone destinataire est requis pour les notifications SMS.")
        
        return data


class NotificationStatsSerializer(serializers.Serializer):
    """
    Sérialiseur pour les statistiques de notifications
    """
    total_notifications = serializers.IntegerField()
    sent_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    email_notifications = serializers.IntegerField()
    sms_notifications = serializers.IntegerField()
    push_notifications = serializers.IntegerField()
    success_rate = serializers.FloatField()
    
    def to_representation(self, instance):
        """Formate les statistiques"""
        data = super().to_representation(instance)
        
        # Calculer le taux de succès
        total = data['total_notifications']
        if total > 0:
            data['success_rate'] = round((data['sent_notifications'] / total) * 100, 2)
        else:
            data['success_rate'] = 0.0
        
        return data



