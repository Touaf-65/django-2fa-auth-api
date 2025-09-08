"""
Vues pour la gestion des gestionnaires de permissions
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from ..models import PermissionManager
from ..serializers import (
    PermissionManagerSerializer,
    PermissionManagerCreateSerializer,
    PermissionManagerUpdateSerializer,
    PermissionManagerListSerializer,
    PermissionManagerStatsSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.view')
@audit_required
def permission_manager_list(request):
    """
    Liste tous les gestionnaires de permissions
    """
    managers = PermissionManager.objects.all()
    
    # Filtres
    user_id = request.GET.get('user_id')
    if user_id:
        managers = managers.filter(user_id=user_id)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        managers = managers.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'user')
    managers = managers.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = managers.count()
    managers_page = managers[start:end]
    
    serializer = PermissionManagerListSerializer(managers_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.view')
@audit_required
def permission_manager_detail(request, pk):
    """
    Détails d'un gestionnaire de permissions
    """
    try:
        manager = PermissionManager.objects.get(pk=pk)
    except PermissionManager.DoesNotExist:
        return Response(
            {'error': 'Gestionnaire de permissions non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PermissionManagerSerializer(manager)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.add')
@audit_sensitive
def permission_manager_create(request):
    """
    Crée un nouveau gestionnaire de permissions
    """
    serializer = PermissionManagerCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter l'utilisateur assignateur
        manager = serializer.save(assigned_by=request.user)
        
        response_serializer = PermissionManagerSerializer(manager)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.change')
@audit_sensitive
def permission_manager_update(request, pk):
    """
    Met à jour un gestionnaire de permissions
    """
    try:
        manager = PermissionManager.objects.get(pk=pk)
    except PermissionManager.DoesNotExist:
        return Response(
            {'error': 'Gestionnaire de permissions non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    partial = request.method == 'PATCH'
    serializer = PermissionManagerUpdateSerializer(manager, data=request.data, partial=partial)
    
    if serializer.is_valid():
        manager = serializer.save()
        
        response_serializer = PermissionManagerSerializer(manager)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.delete')
@audit_sensitive
def permission_manager_delete(request, pk):
    """
    Supprime un gestionnaire de permissions
    """
    try:
        manager = PermissionManager.objects.get(pk=pk)
    except PermissionManager.DoesNotExist:
        return Response(
            {'error': 'Gestionnaire de permissions non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    manager.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permissionmanager.view')
@audit_required
def permission_manager_stats(request):
    """
    Statistiques des gestionnaires de permissions
    """
    stats = {
        'total_managers': PermissionManager.objects.count(),
        'active_managers': PermissionManager.objects.filter(is_active=True).count(),
        'managers_with_delegation_rights': PermissionManager.objects.filter(
            Q(can_delegate_permissions=True) | Q(can_delegate_roles=True)
        ).count(),
        'managers_with_role_management': PermissionManager.objects.filter(
            Q(can_create_roles=True) | Q(can_modify_roles=True) | Q(can_delete_roles=True)
        ).count(),
        'managers_with_group_management': PermissionManager.objects.filter(
            Q(can_create_groups=True) | Q(can_modify_groups=True) | Q(can_delete_groups=True)
        ).count(),
    }
    
    serializer = PermissionManagerStatsSerializer(stats)
    return Response(serializer.data)



