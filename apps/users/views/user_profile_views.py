"""
Vues pour la gestion des profils utilisateur
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import UserProfile, UserPreference, UserActivity
from ..serializers import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserPreferenceSerializer,
    UserActivitySerializer,
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id=None):
    """
    Récupère le profil d'un utilisateur
    
    GET /api/users/profile/
    GET /api/users/profile/{user_id}/
    """
    if user_id:
        # Profil d'un autre utilisateur
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier si l'utilisateur est bloqué
        from ..models import UserBlock
        if UserBlock.is_blocked(request.user, user):
            return Response({
                'error': 'Vous ne pouvez pas voir le profil de cet utilisateur.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier la visibilité du profil
        try:
            profile = user.user_profile
            if profile.profile_visibility == 'private' and request.user != user:
                return Response({
                    'error': 'Ce profil est privé.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profil non trouvé.'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        # Profil de l'utilisateur connecté
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
    
    serializer = UserProfileSerializer(profile, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile_update(request):
    """
    Met à jour le profil de l'utilisateur connecté
    
    PUT/PATCH /api/users/profile/update/
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    serializer = UserProfileUpdateSerializer(
        profile,
        data=request.data,
        partial=request.method == 'PATCH',
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès.',
            'profile': UserProfileSerializer(profile, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """
    Gère les préférences de l'utilisateur connecté
    
    GET /api/users/preferences/
    PUT/PATCH /api/users/preferences/
    """
    preferences, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserPreferenceSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserPreferenceSerializer(
            preferences,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Préférences mises à jour avec succès.',
                'preferences': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity(request, user_id=None):
    """
    Récupère l'historique des activités d'un utilisateur
    
    GET /api/users/activity/
    GET /api/users/activity/{user_id}/
    """
    if user_id:
        # Activités d'un autre utilisateur (seulement si c'est un ami ou public)
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier les permissions
        if request.user != user:
            from ..models import UserFollow, UserBlock
            if UserBlock.is_blocked(request.user, user):
                return Response({
                    'error': 'Vous ne pouvez pas voir les activités de cet utilisateur.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Seuls les amis peuvent voir les activités détaillées
            if not UserFollow.is_following(request.user, user):
                return Response({
                    'error': 'Vous devez suivre cet utilisateur pour voir ses activités.'
                }, status=status.HTTP_403_FORBIDDEN)
    else:
        # Activités de l'utilisateur connecté
        user = request.user
    
    # Récupérer les activités
    activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:50]
    
    serializer = UserActivitySerializer(activities, many=True, context={'request': request})
    return Response({
        'activities': serializer.data,
        'count': len(serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_profile(request):
    """
    Crée un profil utilisateur (pour les nouveaux utilisateurs)
    
    POST /api/users/profile/create/
    """
    # Vérifier si le profil existe déjà
    if hasattr(request.user, 'user_profile'):
        return Response({
            'error': 'Le profil existe déjà.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileUpdateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        profile = serializer.save(user=request.user)
        
        # Créer aussi les préférences par défaut
        UserPreference.objects.get_or_create(user=request.user)
        
        # Enregistrer l'activité
        UserActivity.log_activity(
            user=request.user,
            activity_type='profile_update',
            description='Profil créé',
            request=request
        )
        
        return Response({
            'message': 'Profil créé avec succès.',
            'profile': UserProfileSerializer(profile, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_profile(request):
    """
    Supprime le profil de l'utilisateur connecté
    
    DELETE /api/users/profile/delete/
    """
    try:
        profile = request.user.user_profile
        profile.delete()
        
        # Enregistrer l'activité
        UserActivity.log_activity(
            user=request.user,
            activity_type='profile_update',
            description='Profil supprimé',
            request=request
        )
        
        return Response({
            'message': 'Profil supprimé avec succès.'
        }, status=status.HTTP_200_OK)
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profil non trouvé.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_stats(request, user_id=None):
    """
    Récupère les statistiques d'un profil utilisateur
    
    GET /api/users/profile/stats/
    GET /api/users/profile/stats/{user_id}/
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier les permissions
        from ..models import UserBlock
        if UserBlock.is_blocked(request.user, user):
            return Response({
                'error': 'Vous ne pouvez pas voir les statistiques de cet utilisateur.'
            }, status=status.HTTP_403_FORBIDDEN)
    else:
        user = request.user
    
    # Calculer les statistiques
    from ..models import UserFollow
    stats = {
        'user_id': user.id,
        'user_email': user.email,
        'followers_count': UserFollow.get_followers_count(user),
        'following_count': UserFollow.get_following_count(user),
        'profile_views': 0,  # À implémenter si nécessaire
        'last_activity': user.last_activity,
        'account_created': user.created_at,
        'is_verified': user.is_verified,
        'two_factor_enabled': user.two_factor_enabled,
    }
    
    # Calculer l'âge du compte
    from django.utils import timezone
    if user.created_at:
        account_age = timezone.now() - user.created_at
        stats['account_age_days'] = account_age.days
    else:
        stats['account_age_days'] = 0
    
    return Response(stats, status=status.HTTP_200_OK)
