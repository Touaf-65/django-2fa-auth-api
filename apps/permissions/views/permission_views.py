"""
Vues pour la gestion des permissions
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from core.schemas.permissions_schemas import (
    permission_list_schema, permission_create_schema, permission_stats_schema
)
from ..models import Permission, ConditionalPermission
from ..serializers import (
    PermissionSerializer,
    PermissionCreateSerializer,
    PermissionUpdateSerializer,
    PermissionListSerializer,
    PermissionStatsSerializer,
    ConditionalPermissionSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive
from ..utils import get_permission_statistics

User = get_user_model()


@permission_list_schema
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.view')
@audit_required
def permission_list(request):
    """
    Liste toutes les permissions
    """
    permissions = Permission.objects.all()
    
    # Filtres
    app_label = request.GET.get('app_label')
    if app_label:
        permissions = permissions.filter(app_label=app_label)
    
    model = request.GET.get('model')
    if model:
        permissions = permissions.filter(model=model)
    
    action = request.GET.get('action')
    if action:
        permissions = permissions.filter(action=action)
    
    is_custom = request.GET.get('is_custom')
    if is_custom is not None:
        permissions = permissions.filter(is_custom=is_custom.lower() == 'true')
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        permissions = permissions.filter(is_active=is_active.lower() == 'true')
    
    search = request.GET.get('search')
    if search:
        permissions = permissions.filter(
            Q(name__icontains=search) |
            Q(codename__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Tri
    ordering = request.GET.get('ordering', 'app_label,model,action')
    permissions = permissions.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = permissions.count()
    permissions_page = permissions[start:end]
    
    serializer = PermissionListSerializer(permissions_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.view')
@audit_required
def permission_detail(request, pk):
    """
    Détails d'une permission
    """
    try:
        permission = Permission.objects.get(pk=pk)
    except Permission.DoesNotExist:
        return Response(
            {'error': 'Permission non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PermissionSerializer(permission)
    return Response(serializer.data)


@permission_create_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.add')
@audit_sensitive
def permission_create(request):
    """
    Crée une nouvelle permission
    """
    serializer = PermissionCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter l'utilisateur créateur
        permission = serializer.save(created_by=request.user)
        
        response_serializer = PermissionSerializer(permission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.change')
@audit_sensitive
def permission_update(request, pk):
    """
    Met à jour une permission
    """
    try:
        permission = Permission.objects.get(pk=pk)
    except Permission.DoesNotExist:
        return Response(
            {'error': 'Permission non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si c'est une permission système
    if not permission.is_custom:
        return Response(
            {'error': 'Impossible de modifier une permission système'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    partial = request.method == 'PATCH'
    serializer = PermissionUpdateSerializer(permission, data=request.data, partial=partial)
    
    if serializer.is_valid():
        permission = serializer.save()
        
        response_serializer = PermissionSerializer(permission)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.delete')
@audit_sensitive
def permission_delete(request, pk):
    """
    Supprime une permission
    """
    try:
        permission = Permission.objects.get(pk=pk)
    except Permission.DoesNotExist:
        return Response(
            {'error': 'Permission non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si c'est une permission système
    if not permission.is_custom:
        return Response(
            {'error': 'Impossible de supprimer une permission système'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Vérifier si la permission est utilisée
    if permission.roles.exists():
        return Response(
            {'error': 'Impossible de supprimer une permission utilisée par des rôles'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    permission.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@permission_stats_schema
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.view')
@audit_required
def permission_stats(request):
    """
    Statistiques des permissions
    """
    stats = get_permission_statistics()
    
    # Statistiques supplémentaires
    stats['permissions']['by_action'] = dict(
        Permission.objects.values_list('action').annotate(count=Count('id'))
    )
    
    stats['permissions']['by_field'] = dict(
        Permission.objects.exclude(field_name='').values_list('field_name').annotate(count=Count('id'))
    )
    
    serializer = PermissionStatsSerializer(stats['permissions'])
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.view')
@audit_required
def conditional_permission_list(request):
    """
    Liste toutes les permissions conditionnelles
    """
    conditional_permissions = ConditionalPermission.objects.all()
    
    # Filtres
    permission_id = request.GET.get('permission_id')
    if permission_id:
        conditional_permissions = conditional_permissions.filter(permission_id=permission_id)
    
    condition_type = request.GET.get('condition_type')
    if condition_type:
        conditional_permissions = conditional_permissions.filter(condition_type=condition_type)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        conditional_permissions = conditional_permissions.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'permission,condition_type')
    conditional_permissions = conditional_permissions.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = conditional_permissions.count()
    conditional_permissions_page = conditional_permissions[start:end]
    
    serializer = ConditionalPermissionSerializer(conditional_permissions_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.permission.view')
@audit_required
def conditional_permission_detail(request, pk):
    """
    Détails d'une permission conditionnelle
    """
    try:
        conditional_permission = ConditionalPermission.objects.get(pk=pk)
    except ConditionalPermission.DoesNotExist:
        return Response(
            {'error': 'Permission conditionnelle non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ConditionalPermissionSerializer(conditional_permission)
    return Response(serializer.data)
