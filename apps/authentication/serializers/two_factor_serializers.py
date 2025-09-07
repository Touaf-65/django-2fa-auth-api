"""
Sérialiseurs pour l'authentification à deux facteurs
"""

from rest_framework import serializers
from ..models import TwoFactorAuth


class TwoFactorSetupSerializer(serializers.Serializer):
    """
    Sérialiseur pour la configuration de la 2FA
    """
    
    def to_representation(self, instance):
        """Retourne les données de configuration 2FA"""
        if not instance:
            return {}
        
        return {
            'qr_code': instance.generate_qr_code(),
            'secret_key': instance.secret_key,
            'backup_codes': instance.backup_codes,
            'totp_uri': instance.get_totp_uri(),
        }


class TwoFactorVerifySerializer(serializers.Serializer):
    """
    Sérialiseur pour la vérification des codes 2FA
    """
    code = serializers.CharField(
        max_length=8,
        min_length=6,
        help_text="Code TOTP à 6 chiffres ou code de secours à 8 caractères"
    )
    
    def validate_code(self, value):
        """Valide le format du code"""
        # Code TOTP (6 chiffres)
        if value.isdigit() and len(value) == 6:
            return value
        
        # Code de secours (8 caractères alphanumériques)
        if len(value) == 8 and value.isalnum():
            return value
        
        raise serializers.ValidationError(
            "Le code doit être un code TOTP à 6 chiffres ou un code de secours à 8 caractères."
        )
    
    def validate(self, attrs):
        """Valide le code 2FA"""
        user = self.context['request'].user
        code = attrs['code']
        
        try:
            two_factor_auth = user.two_factor_auth
        except TwoFactorAuth.DoesNotExist:
            raise serializers.ValidationError(
                "L'authentification à deux facteurs n'est pas configurée pour cet utilisateur."
            )
        
        # Vérifier le code TOTP
        if code.isdigit() and len(code) == 6:
            if two_factor_auth.verify_totp_code(code):
                two_factor_auth.update_last_used()
                attrs['verification_method'] = 'totp'
                return attrs
        
        # Vérifier le code de secours
        elif len(code) == 8 and code.isalnum():
            if two_factor_auth.verify_backup_code(code):
                attrs['verification_method'] = 'backup'
                return attrs
        
        raise serializers.ValidationError(
            "Code invalide. Veuillez vérifier et réessayer."
        )


class TwoFactorDisableSerializer(serializers.Serializer):
    """
    Sérialiseur pour désactiver la 2FA
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Mot de passe de l'utilisateur pour confirmer la désactivation"
    )
    
    def validate_password(self, value):
        """Valide le mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe incorrect.")
        return value
