"""
Vues pour l'authentification des utilisateurs
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as DRFTokenRefreshView
from django.contrib.auth import login, logout
from django.utils import timezone

from ..models import User, UserSession
from ..serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    """
    Inscription d'un nouvel utilisateur
    
    POST /api/auth/signup/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Créer une session utilisateur
        UserSession.create_session(user, request.session.session_key, request)
        
        # Mettre à jour la dernière activité
        user.update_last_activity()
        
        return Response({
            'message': 'Compte créé avec succès. Bienvenue !',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    Connexion d'un utilisateur
    
    POST /api/auth/signin/
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Vérifier si la 2FA est activée
        requires_2fa = user.has_2fa_enabled()
        
        if requires_2fa:
            # Pour la 2FA, on ne génère pas encore les tokens
            # L'utilisateur devra d'abord vérifier son code 2FA
            return Response({
                'message': 'Authentification à deux facteurs requise.',
                'user': UserSerializer(user).data,
                'requires_2fa': True,
                'two_factor_enabled': True,
            }, status=status.HTTP_200_OK)
        
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
            'message': 'Connexion réussie.',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            },
            'requires_2fa': False,
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    Déconnexion d'un utilisateur
    
    POST /api/auth/logout/
    """
    try:
        # Récupérer le token de rafraîchissement depuis le body
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            # Blacklister le token de rafraîchissement
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Désactiver la session actuelle
        session_key = request.session.session_key
        if session_key:
            try:
                user_session = UserSession.objects.get(
                    user=request.user,
                    session_key=session_key
                )
                user_session.deactivate()
            except UserSession.DoesNotExist:
                pass
        
        # Déconnexion Django
        logout(request)
        
        return Response({
            'message': 'Déconnexion réussie.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la déconnexion.',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(DRFTokenRefreshView):
    """
    Rafraîchissement des tokens JWT
    
    POST /api/auth/token/refresh/
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Mettre à jour la dernière activité de l'utilisateur
            if hasattr(request, 'user') and request.user.is_authenticated:
                request.user.update_last_activity()
        
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Récupérer le profil de l'utilisateur connecté
    
    GET /api/auth/profile/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Mettre à jour le profil de l'utilisateur connecté
    
    PUT/PATCH /api/auth/profile/
    """
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
