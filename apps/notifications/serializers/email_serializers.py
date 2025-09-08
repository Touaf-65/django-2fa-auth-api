"""
Sérialiseurs pour les notifications email
"""

from rest_framework import serializers
from ..models import EmailNotification, EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les templates d'emails
    """
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id',
            'name',
            'subject',
            'html_content',
            'text_content',
            'from_email',
            'from_name',
            'reply_to',
            'available_variables',
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
    
    def validate_subject(self, value):
        """Valide le sujet de l'email"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le sujet doit contenir au moins 5 caractères.")
        return value.strip()
    
    def validate_html_content(self, value):
        """Valide le contenu HTML"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le contenu HTML doit contenir au moins 10 caractères.")
        return value.strip()


class EmailNotificationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les notifications email
    """
    notification_id = serializers.IntegerField(source='notification.id', read_only=True)
    user_email = serializers.EmailField(source='notification.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    template_name = serializers.CharField(source='template.name', read_only=True)
    status = serializers.CharField(source='notification.status', read_only=True)
    status_display = serializers.CharField(source='notification.get_status_display', read_only=True)
    
    class Meta:
        model = EmailNotification
        fields = [
            'id',
            'notification_id',
            'user_email',
            'user_name',
            'template',
            'template_name',
            'to_email',
            'to_name',
            'from_email',
            'from_name',
            'reply_to',
            'subject',
            'html_content',
            'text_content',
            'attachments',
            'sendgrid_message_id',
            'sendgrid_status',
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
            'template_name',
            'status',
            'status_display',
            'sendgrid_message_id',
            'sendgrid_status',
            'created_at',
            'updated_at',
        ]
    
    def get_user_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        if obj.notification.user.first_name and obj.notification.user.last_name:
            return f"{obj.notification.user.first_name} {obj.notification.user.last_name}"
        return obj.notification.user.email
    
    def validate_to_email(self, value):
        """Valide l'email destinataire"""
        if not value or not value.strip():
            raise serializers.ValidationError("L'email destinataire est requis.")
        return value.strip()
    
    def validate_subject(self, value):
        """Valide le sujet de l'email"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le sujet est requis.")
        return value.strip()
    
    def validate_html_content(self, value):
        """Valide le contenu HTML"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le contenu HTML est requis.")
        return value.strip()


class EmailSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi d'emails
    """
    user_id = serializers.IntegerField(required=True)
    to_email = serializers.EmailField(required=False, allow_blank=True)
    subject = serializers.CharField(max_length=200, required=True)
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
    attachments = serializers.JSONField(required=False, default=list)
    
    def validate_user_id(self, value):
        """Valide l'ID de l'utilisateur"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")
        return value
    
    def validate_subject(self, value):
        """Valide le sujet"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le sujet doit contenir au moins 5 caractères.")
        return value.strip()
    
    def validate_content(self, value):
        """Valide le contenu"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le contenu doit contenir au moins 10 caractères.")
        return value.strip()


class EmailBulkSendSerializer(serializers.Serializer):
    """
    Sérialiseur pour l'envoi d'emails en masse
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    subject = serializers.CharField(max_length=200, required=True)
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
    
    def validate_subject(self, value):
        """Valide le sujet"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le sujet doit contenir au moins 5 caractères.")
        return value.strip()
    
    def validate_content(self, value):
        """Valide le contenu"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le contenu doit contenir au moins 10 caractères.")
        return value.strip()



