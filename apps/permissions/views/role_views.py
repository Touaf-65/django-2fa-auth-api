"""
Vues pour la gestion des rôles
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from core.schemas.permissions_schemas import role_create_schema
from ..models import Role, RolePermission, Permission
from ..serializers import (
    RoleSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    RoleListSerializer,
    RoleStatsSerializer,
    RolePermissionSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive
from ..utils import get_permission_statistics

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.view')
@audit_required
def role_list(request):
    """
    Liste tous les rôles
    """
    roles = Role.objects.all()
    
    # Filtres
    is_system = request.GET.get('is_system')
    if is_system is not None:
        roles = roles.filter(is_system=is_system.lower() == 'true')
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        roles = roles.filter(is_active=is_active.lower() == 'true')
    
    search = request.GET.get('search')
    if search:
        roles = roles.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Tri
    ordering = request.GET.get('ordering', 'name')
    roles = roles.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = roles.count()
    roles_page = roles[start:end]
    
    serializer = RoleListSerializer(roles_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.view')
@audit_required
def role_detail(request, pk):
    """
    Détails d'un rôle
    """
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response(
            {'error': 'Rôle non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RoleSerializer(role)
    return Response(serializer.data)


@role_create_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.add')
@audit_sensitive
def role_create(request):
    """
    Crée un nouveau rôle
    """
    serializer = RoleCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter l'utilisateur créateur
        role = serializer.save(created_by=request.user)
        
        response_serializer = RoleSerializer(role)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.change')
@audit_sensitive
def role_update(request, pk):
    """
    Met à jour un rôle
    """
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response(
            {'error': 'Rôle non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si c'est un rôle système
    if role.is_system:
        return Response(
            {'error': 'Impossible de modifier un rôle système'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    partial = request.method == 'PATCH'
    serializer = RoleUpdateSerializer(role, data=request.data, partial=partial)
    
    if serializer.is_valid():
        role = serializer.save()
        
        response_serializer = RoleSerializer(role)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.delete')
@audit_sensitive
def role_delete(request, pk):
    """
    Supprime un rôle
    """
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response(
            {'error': 'Rôle non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si c'est un rôle système
    if role.is_system:
        return Response(
            {'error': 'Impossible de supprimer un rôle système'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Vérifier si le rôle est utilisé
    if role.user_roles.exists() or role.groups.exists():
        return Response(
            {'error': 'Impossible de supprimer un rôle utilisé par des utilisateurs ou des groupes'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    role.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.view')
@audit_required
def role_stats(request):
    """
    Statistiques des rôles
    """
    stats = get_permission_statistics()
    
    # Statistiques supplémentaires
    stats['roles']['with_permissions'] = Role.objects.annotate(
        permission_count=Count('permissions')
    ).filter(permission_count__gt=0).count()
    
    stats['roles']['with_users'] = Role.objects.annotate(
        user_count=Count('user_roles')
    ).filter(user_count__gt=0).count()
    
    serializer = RoleStatsSerializer(stats['roles'])
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.view')
@audit_required
def role_permission_list(request, role_pk):
    """
    Liste les permissions d'un rôle
    """
    try:
        role = Role.objects.get(pk=role_pk)
    except Role.DoesNotExist:
        return Response(
            {'error': 'Rôle non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    role_permissions = RolePermission.objects.filter(role=role)
    
    # Filtres
    granted = request.GET.get('granted')
    if granted is not None:
        role_permissions = role_permissions.filter(granted=granted.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'permission__app_label,permission__model,permission__action')
    role_permissions = role_permissions.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = role_permissions.count()
    role_permissions_page = role_permissions[start:end]
    
    serializer = RolePermissionSerializer(role_permissions_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.role.view')
@audit_required
def role_permission_detail(request, role_pk, permission_pk):
    """
    Détails d'une permission de rôle
    """
    try:
        role_permission = RolePermission.objects.get(role_id=role_pk, permission_id=permission_pk)
    except RolePermission.DoesNotExist:
        return Response(
            {'error': 'Permission de rôle non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RolePermissionSerializer(role_permission)
    return Response(serializer.data)
