"""
Vues pour la gestion des groupes
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from ..models import Group, GroupMembership, GroupRole
from ..serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupListSerializer,
    GroupStatsSerializer,
    GroupMembershipSerializer,
    GroupRoleSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive
from ..utils import get_permission_statistics

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_list(request):
    """
    Liste tous les groupes
    """
    groups = Group.objects.all()
    
    # Filtres
    is_active = request.GET.get('is_active')
    if is_active is not None:
        groups = groups.filter(is_active=is_active.lower() == 'true')
    
    search = request.GET.get('search')
    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Tri
    ordering = request.GET.get('ordering', 'name')
    groups = groups.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = groups.count()
    groups_page = groups[start:end]
    
    serializer = GroupListSerializer(groups_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_detail(request, pk):
    """
    Détails d'un groupe
    """
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response(
            {'error': 'Groupe non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = GroupSerializer(group)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.add')
@audit_sensitive
def group_create(request):
    """
    Crée un nouveau groupe
    """
    serializer = GroupCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter l'utilisateur créateur
        group = serializer.save(created_by=request.user)
        
        response_serializer = GroupSerializer(group)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.change')
@audit_sensitive
def group_update(request, pk):
    """
    Met à jour un groupe
    """
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response(
            {'error': 'Groupe non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    partial = request.method == 'PATCH'
    serializer = GroupUpdateSerializer(group, data=request.data, partial=partial)
    
    if serializer.is_valid():
        group = serializer.save()
        
        response_serializer = GroupSerializer(group)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.delete')
@audit_sensitive
def group_delete(request, pk):
    """
    Supprime un groupe
    """
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response(
            {'error': 'Groupe non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si le groupe est utilisé
    if group.users.exists():
        return Response(
            {'error': 'Impossible de supprimer un groupe avec des utilisateurs'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    group.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_stats(request):
    """
    Statistiques des groupes
    """
    stats = get_permission_statistics()
    
    # Statistiques supplémentaires
    stats['groups']['with_members'] = Group.objects.annotate(
        user_count=Count('users')
    ).filter(user_count__gt=0).count()
    
    stats['groups']['with_roles'] = Group.objects.annotate(
        role_count=Count('roles')
    ).filter(role_count__gt=0).count()
    
    serializer = GroupStatsSerializer(stats['groups'])
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_membership_list(request):
    """
    Liste toutes les adhésions aux groupes
    """
    memberships = GroupMembership.objects.all()
    
    # Filtres
    group_id = request.GET.get('group_id')
    if group_id:
        memberships = memberships.filter(group_id=group_id)
    
    user_id = request.GET.get('user_id')
    if user_id:
        memberships = memberships.filter(user_id=user_id)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        memberships = memberships.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'group,user')
    memberships = memberships.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = memberships.count()
    memberships_page = memberships[start:end]
    
    serializer = GroupMembershipSerializer(memberships_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_membership_detail(request, pk):
    """
    Détails d'une adhésion à un groupe
    """
    try:
        membership = GroupMembership.objects.get(pk=pk)
    except GroupMembership.DoesNotExist:
        return Response(
            {'error': 'Adhésion au groupe non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = GroupMembershipSerializer(membership)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_role_list(request):
    """
    Liste tous les rôles de groupes
    """
    group_roles = GroupRole.objects.all()
    
    # Filtres
    group_id = request.GET.get('group_id')
    if group_id:
        group_roles = group_roles.filter(group_id=group_id)
    
    role_id = request.GET.get('role_id')
    if role_id:
        group_roles = group_roles.filter(role_id=role_id)
    
    # Tri
    ordering = request.GET.get('ordering', 'group,role')
    group_roles = group_roles.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = group_roles.count()
    group_roles_page = group_roles[start:end]
    
    serializer = GroupRoleSerializer(group_roles_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.group.view')
@audit_required
def group_role_detail(request, pk):
    """
    Détails d'un rôle de groupe
    """
    try:
        group_role = GroupRole.objects.get(pk=pk)
    except GroupRole.DoesNotExist:
        return Response(
            {'error': 'Rôle de groupe non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = GroupRoleSerializer(group_role)
    return Response(serializer.data)

