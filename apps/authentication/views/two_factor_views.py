"""
Vues pour l'authentification à deux facteurs
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import TwoFactorAuth, UserSession
from ..serializers import (
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    TwoFactorDisableSerializer,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_setup(request):
    """
    Configurer l'authentification à deux facteurs
    
    POST /api/auth/2fa/setup/
    """
    user = request.user
    
    # Vérifier si la 2FA est déjà activée
    if user.has_2fa_enabled():
        return Response({
            'error': 'L\'authentification à deux facteurs est déjà activée.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Créer ou récupérer la configuration 2FA
    try:
        two_factor_auth = user.two_factor_auth
    except TwoFactorAuth.DoesNotExist:
        two_factor_auth = TwoFactorAuth.create_for_user(user)
    
    # Générer les données de configuration
    serializer = TwoFactorSetupSerializer(two_factor_auth)
    
    return Response({
        'message': 'Configuration 2FA générée. Scannez le QR code avec votre application d\'authentification.',
        'setup_data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_verify_setup(request):
    """
    Vérifier et activer la configuration 2FA
    
    POST /api/auth/2fa/verify-setup/
    """
    user = request.user
    
    try:
        two_factor_auth = user.two_factor_auth
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'error': 'Configuration 2FA non trouvée. Veuillez d\'abord configurer la 2FA.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = TwoFactorVerifySerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Activer la 2FA
        two_factor_auth.enable()
        
        return Response({
            'message': 'Authentification à deux facteurs activée avec succès.',
            'verification_method': serializer.validated_data['verification_method']
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_verify_login(request):
    """
    Vérifier le code 2FA lors de la connexion
    
    POST /api/auth/2fa/verify-login/
    """
    user = request.user
    
    # Vérifier si la 2FA est activée
    if not user.has_2fa_enabled():
        return Response({
            'error': 'L\'authentification à deux facteurs n\'est pas activée.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = TwoFactorVerifySerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Créer une session utilisateur
        UserSession.create_session(user, request.session.session_key, request)
        
        # Mettre à jour la dernière activité et l'IP
        user.update_last_activity()
        user.last_login_ip = UserSession._get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        return Response({
            'message': 'Connexion réussie avec authentification à deux facteurs.',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'two_factor_enabled': user.two_factor_enabled,
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            },
            'verification_method': serializer.validated_data['verification_method']
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_disable(request):
    """
    Désactiver l'authentification à deux facteurs
    
    POST /api/auth/2fa/disable/
    """
    user = request.user
    
    # Vérifier si la 2FA est activée
    if not user.has_2fa_enabled():
        return Response({
            'error': 'L\'authentification à deux facteurs n\'est pas activée.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = TwoFactorDisableSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            two_factor_auth = user.two_factor_auth
            two_factor_auth.disable()
            
            return Response({
                'message': 'Authentification à deux facteurs désactivée avec succès.'
            }, status=status.HTTP_200_OK)
            
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'error': 'Configuration 2FA non trouvée.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def two_factor_status(request):
    """
    Récupérer le statut de la 2FA
    
    GET /api/auth/2fa/status/
    """
    user = request.user
    
    try:
        two_factor_auth = user.two_factor_auth
        backup_codes_count = len(two_factor_auth.backup_codes)
    except TwoFactorAuth.DoesNotExist:
        two_factor_auth = None
        backup_codes_count = 0
    
    return Response({
        'is_enabled': user.has_2fa_enabled(),
        'is_configured': two_factor_auth is not None,
        'backup_codes_count': backup_codes_count,
        'last_used': two_factor_auth.last_used if two_factor_auth else None,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_regenerate_backup_codes(request):
    """
    Régénérer les codes de secours
    
    POST /api/auth/2fa/regenerate-backup-codes/
    """
    user = request.user
    
    # Vérifier si la 2FA est activée
    if not user.has_2fa_enabled():
        return Response({
            'error': 'L\'authentification à deux facteurs n\'est pas activée.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        two_factor_auth = user.two_factor_auth
        new_backup_codes = two_factor_auth.generate_backup_codes()
        
        return Response({
            'message': 'Codes de secours régénérés avec succès.',
            'backup_codes': new_backup_codes
        }, status=status.HTTP_200_OK)
        
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'error': 'Configuration 2FA non trouvée.'
        }, status=status.HTTP_400_BAD_REQUEST)

