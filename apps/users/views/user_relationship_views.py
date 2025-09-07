"""
Vues pour les relations entre utilisateurs
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from ..models import UserFollow, UserBlock, UserProfile
from ..serializers import (
    UserListSerializer,
    UserSearchSerializer,
    UserFollowSerializer,
    UserBlockSerializer,
    UserStatsSerializer,
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """
    Liste les utilisateurs avec pagination
    
    GET /api/users/
    """
    # Paramètres de pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    search = request.GET.get('search', '')
    
    # Construire la requête
    users_query = User.objects.select_related('user_profile').all()
    
    # Filtrage par recherche
    if search:
        users_query = users_query.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Exclure les utilisateurs bloqués
    blocked_users = UserBlock.objects.filter(
        blocker=request.user,
        is_active=True
    ).values_list('blocked_id', flat=True)
    users_query = users_query.exclude(id__in=blocked_users)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    users = users_query[start:end]
    
    serializer = UserListSerializer(users, many=True, context={'request': request})
    
    return Response({
        'users': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': users_query.count(),
            'has_next': end < users_query.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_search(request):
    """
    Recherche avancée d'utilisateurs
    
    POST /api/users/search/
    """
    serializer = UserSearchSerializer(data=request.data)
    
    if serializer.is_valid():
        query = serializer.validated_data['query']
        limit = serializer.validated_data['limit']
        include_blocked = serializer.validated_data['include_blocked']
        
        # Construire la requête de recherche
        users_query = User.objects.select_related('user_profile').filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(user_profile__bio__icontains=query) |
            Q(user_profile__location__icontains=query) |
            Q(user_profile__job_title__icontains=query) |
            Q(user_profile__company__icontains=query)
        )
        
        # Exclure les utilisateurs bloqués si demandé
        if not include_blocked:
            blocked_users = UserBlock.objects.filter(
                blocker=request.user,
                is_active=True
            ).values_list('blocked_id', flat=True)
            users_query = users_query.exclude(id__in=blocked_users)
        
        # Limiter les résultats
        users = users_query[:limit]
        
        serializer = UserListSerializer(users, many=True, context={'request': request})
        
        return Response({
            'users': serializer.data,
            'query': query,
            'count': len(serializer.data),
            'total_found': users_query.count()
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_follow(request, user_id):
    """
    Suit un utilisateur
    
    POST /api/users/{user_id}/follow/
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # Vérifier si l'utilisateur ne se suit pas lui-même
    if request.user == user_to_follow:
        return Response({
            'error': 'Vous ne pouvez pas vous suivre vous-même.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier si l'utilisateur est bloqué
    if UserBlock.is_blocked(request.user, user_to_follow):
        return Response({
            'error': 'Vous ne pouvez pas suivre cet utilisateur.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Créer la relation de suivi
    serializer = UserFollowSerializer(
        data={'follower': request.user.id, 'following': user_to_follow.id},
        context={'request': request}
    )
    
    if serializer.is_valid():
        follow = serializer.save()
        return Response({
            'message': f'Vous suivez maintenant {user_to_follow.email}.',
            'follow': UserFollowSerializer(follow, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_unfollow(request, user_id):
    """
    Arrête de suivre un utilisateur
    
    DELETE /api/users/{user_id}/follow/
    """
    user_to_unfollow = get_object_or_404(User, id=user_id)
    
    # Supprimer la relation de suivi
    success = UserFollow.unfollow_user(request.user, user_to_unfollow)
    
    if success:
        return Response({
            'message': f'Vous ne suivez plus {user_to_unfollow.email}.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Vous ne suivez pas cet utilisateur.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_followers(request, user_id=None):
    """
    Récupère la liste des abonnés d'un utilisateur
    
    GET /api/users/followers/
    GET /api/users/{user_id}/followers/
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier les permissions
        if request.user != user:
            from ..models import UserBlock
            if UserBlock.is_blocked(request.user, user):
                return Response({
                    'error': 'Vous ne pouvez pas voir les abonnés de cet utilisateur.'
                }, status=status.HTTP_403_FORBIDDEN)
    else:
        user = request.user
    
    # Récupérer les abonnés
    followers = UserFollow.objects.filter(
        following=user,
        is_active=True
    ).select_related('follower', 'follower__user_profile')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    followers_page = followers[start:end]
    serializer = UserFollowSerializer(followers_page, many=True, context={'request': request})
    
    return Response({
        'followers': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': followers.count(),
            'has_next': end < followers.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_following(request, user_id=None):
    """
    Récupère la liste des utilisateurs suivis
    
    GET /api/users/following/
    GET /api/users/{user_id}/following/
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier les permissions
        if request.user != user:
            from ..models import UserBlock
            if UserBlock.is_blocked(request.user, user):
                return Response({
                    'error': 'Vous ne pouvez pas voir les utilisateurs suivis par cet utilisateur.'
                }, status=status.HTTP_403_FORBIDDEN)
    else:
        user = request.user
    
    # Récupérer les utilisateurs suivis
    following = UserFollow.objects.filter(
        follower=user,
        is_active=True
    ).select_related('following', 'following__user_profile')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    following_page = following[start:end]
    serializer = UserFollowSerializer(following_page, many=True, context={'request': request})
    
    return Response({
        'following': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': following.count(),
            'has_next': end < following.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_block(request, user_id):
    """
    Bloque un utilisateur
    
    POST /api/users/{user_id}/block/
    """
    user_to_block = get_object_or_404(User, id=user_id)
    
    # Vérifier si l'utilisateur ne se bloque pas lui-même
    if request.user == user_to_block:
        return Response({
            'error': 'Vous ne pouvez pas vous bloquer vous-même.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Créer le blocage
    serializer = UserBlockSerializer(
        data={
            'blocker': request.user.id,
            'blocked': user_to_block.id,
            'reason': request.data.get('reason', 'other'),
            'description': request.data.get('description', '')
        },
        context={'request': request}
    )
    
    if serializer.is_valid():
        block = serializer.save()
        return Response({
            'message': f'Vous avez bloqué {user_to_block.email}.',
            'block': UserBlockSerializer(block, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_unblock(request, user_id):
    """
    Débloque un utilisateur
    
    DELETE /api/users/{user_id}/block/
    """
    user_to_unblock = get_object_or_404(User, id=user_id)
    
    # Supprimer le blocage
    success = UserBlock.unblock_user(request.user, user_to_unblock)
    
    if success:
        return Response({
            'message': f'Vous avez débloqué {user_to_unblock.email}.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Vous n\'avez pas bloqué cet utilisateur.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_blocked(request):
    """
    Récupère la liste des utilisateurs bloqués
    
    GET /api/users/blocked/
    """
    # Récupérer les utilisateurs bloqués
    blocked = UserBlock.objects.filter(
        blocker=request.user,
        is_active=True
    ).select_related('blocked', 'blocked__user_profile')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    blocked_page = blocked[start:end]
    serializer = UserBlockSerializer(blocked_page, many=True, context={'request': request})
    
    return Response({
        'blocked': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': blocked.count(),
            'has_next': end < blocked.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request, user_id=None):
    """
    Récupère les statistiques d'un utilisateur
    
    GET /api/users/stats/
    GET /api/users/{user_id}/stats/
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
    
    serializer = UserStatsSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
