"""
Vues pour la gestion des rôles utilisateur
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import UserRole
from ..serializers import (
    UserRoleSerializer,
    UserRoleCreateSerializer,
    UserRoleUpdateSerializer,
    UserRoleListSerializer,
    UserRoleStatsSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.view')
@audit_required
def user_role_list(request):
    """
    Liste tous les rôles utilisateur
    """
    user_roles = UserRole.objects.all()
    
    # Filtres
    user_id = request.GET.get('user_id')
    if user_id:
        user_roles = user_roles.filter(user_id=user_id)
    
    role_id = request.GET.get('role_id')
    if role_id:
        user_roles = user_roles.filter(role_id=role_id)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        user_roles = user_roles.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'user,role')
    user_roles = user_roles.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = user_roles.count()
    user_roles_page = user_roles[start:end]
    
    serializer = UserRoleListSerializer(user_roles_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.view')
@audit_required
def user_role_detail(request, pk):
    """
    Détails d'un rôle utilisateur
    """
    try:
        user_role = UserRole.objects.get(pk=pk)
    except UserRole.DoesNotExist:
        return Response(
            {'error': 'Rôle utilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UserRoleSerializer(user_role)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.add')
@audit_sensitive
def user_role_create(request):
    """
    Crée un nouveau rôle utilisateur
    """
    serializer = UserRoleCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter l'utilisateur assignateur
        user_role = serializer.save(assigned_by=request.user)
        
        response_serializer = UserRoleSerializer(user_role)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.change')
@audit_sensitive
def user_role_update(request, pk):
    """
    Met à jour un rôle utilisateur
    """
    try:
        user_role = UserRole.objects.get(pk=pk)
    except UserRole.DoesNotExist:
        return Response(
            {'error': 'Rôle utilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    partial = request.method == 'PATCH'
    serializer = UserRoleUpdateSerializer(user_role, data=request.data, partial=partial)
    
    if serializer.is_valid():
        user_role = serializer.save()
        
        response_serializer = UserRoleSerializer(user_role)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.delete')
@audit_sensitive
def user_role_delete(request, pk):
    """
    Supprime un rôle utilisateur
    """
    try:
        user_role = UserRole.objects.get(pk=pk)
    except UserRole.DoesNotExist:
        return Response(
            {'error': 'Rôle utilisateur non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user_role.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.userrole.view')
@audit_required
def user_role_stats(request):
    """
    Statistiques des rôles utilisateur
    """
    stats = {
        'total_assignments': UserRole.objects.count(),
        'active_assignments': UserRole.objects.filter(is_active=True).count(),
        'expired_assignments': UserRole.objects.filter(
            expires_at__lt=timezone.now()
        ).count(),
        'users_with_roles': UserRole.objects.values('user').distinct().count(),
    }
    
    # Statistiques par rôle
    role_stats = {}
    for user_role in UserRole.objects.select_related('role'):
        role_name = user_role.role.name
        if role_name not in role_stats:
            role_stats[role_name] = 0
        role_stats[role_name] += 1
    
    stats['assignments_by_role'] = role_stats
    
    serializer = UserRoleStatsSerializer(stats)
    return Response(serializer.data)
