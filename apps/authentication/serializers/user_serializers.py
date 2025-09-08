"""
Sérialiseurs pour les utilisateurs et l'authentification
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les informations utilisateur
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'avatar',
            'is_verified',
            'two_factor_enabled',
            'language',
            'timezone',
            'email_notifications',
            'created_at',
            'last_activity',
        ]
        read_only_fields = [
            'id',
            'is_verified',
            'two_factor_enabled',
            'created_at',
            'last_activity',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'inscription d'un nouvel utilisateur
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Mot de passe (minimum 8 caractères)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmation du mot de passe"
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'phone',
            'language',
            'timezone',
        ]
    
    def validate_email(self, value):
        """Valide l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value
    
    def validate_password(self, value):
        """Valide le mot de passe"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Valide que les mots de passe correspondent"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Les mots de passe ne correspondent pas."
            })
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur"""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Sérialiseur pour la connexion utilisateur
    """
    email = serializers.EmailField(
        help_text="Adresse email de l'utilisateur"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Mot de passe de l'utilisateur"
    )
    
    def validate(self, attrs):
        """Valide les identifiants de connexion"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Vérifier si l'utilisateur existe
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Identifiants invalides.",
                    code='authorization'
                )
            
            # Vérifier si le compte est verrouillé
            if user.is_account_locked():
                raise serializers.ValidationError(
                    "Votre compte est temporairement verrouillé. Veuillez réessayer plus tard.",
                    code='authorization'
                )
            
            # Authentifier l'utilisateur
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                # Incrémenter les tentatives échouées
                try:
                    user_obj = User.objects.get(email=email)
                    user_obj.increment_failed_attempts()
                    
                    # Vérifier si on doit verrouiller le compte
                    from django.conf import settings
                    max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
                    if user_obj.failed_login_attempts >= max_attempts:
                        lockout_duration = getattr(settings, 'LOCKOUT_DURATION', 900)
                        user_obj.lock_account(lockout_duration // 60)  # Convertir en minutes
                        
                except User.DoesNotExist:
                    pass
                
                raise serializers.ValidationError(
                    "Identifiants invalides.",
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    "Ce compte a été désactivé.",
                    code='authorization'
                )
            
            # Réinitialiser les tentatives échouées en cas de succès
            user.reset_failed_attempts()
            
            attrs['user'] = user
            return attrs
        
        else:
            raise serializers.ValidationError(
                "Email et mot de passe requis.",
                code='authorization'
            )

