"""
Vues pour la gestion des délégations
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.schemas.permissions_schemas import delegation_create_schema
from ..models import PermissionDelegation, RoleDelegation
from ..serializers import (
    PermissionDelegationSerializer,
    PermissionDelegationCreateSerializer,
    RoleDelegationSerializer,
    RoleDelegationCreateSerializer,
    DelegationStatsSerializer,
)
from ..decorators import permission_required, audit_required, audit_sensitive

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.view')
@audit_required
def permission_delegation_list(request):
    """
    Liste toutes les délégations de permissions
    """
    delegations = PermissionDelegation.objects.all()
    
    # Filtres
    delegator_id = request.GET.get('delegator_id')
    if delegator_id:
        delegations = delegations.filter(delegator_id=delegator_id)
    
    delegatee_id = request.GET.get('delegatee_id')
    if delegatee_id:
        delegations = delegations.filter(delegatee_id=delegatee_id)
    
    permission_id = request.GET.get('permission_id')
    if permission_id:
        delegations = delegations.filter(permission_id=permission_id)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        delegations = delegations.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'delegator,delegatee')
    delegations = delegations.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = delegations.count()
    delegations_page = delegations[start:end]
    
    serializer = PermissionDelegationSerializer(delegations_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.view')
@audit_required
def permission_delegation_detail(request, pk):
    """
    Détails d'une délégation de permission
    """
    try:
        delegation = PermissionDelegation.objects.get(pk=pk)
    except PermissionDelegation.DoesNotExist:
        return Response(
            {'error': 'Délégation de permission non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PermissionDelegationSerializer(delegation)
    return Response(serializer.data)


@delegation_create_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.add')
@audit_sensitive
def permission_delegation_create(request):
    """
    Crée une nouvelle délégation de permission
    """
    serializer = PermissionDelegationCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter le déléguant
        delegation = serializer.save(delegator=request.user)
        
        response_serializer = PermissionDelegationSerializer(delegation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.change')
@audit_sensitive
def permission_delegation_revoke(request, pk):
    """
    Révoque une délégation de permission
    """
    try:
        delegation = PermissionDelegation.objects.get(pk=pk)
    except PermissionDelegation.DoesNotExist:
        return Response(
            {'error': 'Délégation de permission non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'utilisateur peut révoquer cette délégation
    if delegation.delegator != request.user and not request.user.is_superuser:
        return Response(
            {'error': 'Vous ne pouvez pas révoquer cette délégation'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    delegation.is_active = False
    delegation.save()
    
    return Response({'message': 'Délégation révoquée avec succès'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.view')
@audit_required
def role_delegation_list(request):
    """
    Liste toutes les délégations de rôles
    """
    delegations = RoleDelegation.objects.all()
    
    # Filtres
    delegator_id = request.GET.get('delegator_id')
    if delegator_id:
        delegations = delegations.filter(delegator_id=delegator_id)
    
    delegatee_id = request.GET.get('delegatee_id')
    if delegatee_id:
        delegations = delegations.filter(delegatee_id=delegatee_id)
    
    role_id = request.GET.get('role_id')
    if role_id:
        delegations = delegations.filter(role_id=role_id)
    
    is_active = request.GET.get('is_active')
    if is_active is not None:
        delegations = delegations.filter(is_active=is_active.lower() == 'true')
    
    # Tri
    ordering = request.GET.get('ordering', 'delegator,delegatee')
    delegations = delegations.order_by(*ordering.split(','))
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = delegations.count()
    delegations_page = delegations[start:end]
    
    serializer = RoleDelegationSerializer(delegations_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.view')
@audit_required
def role_delegation_detail(request, pk):
    """
    Détails d'une délégation de rôle
    """
    try:
        delegation = RoleDelegation.objects.get(pk=pk)
    except RoleDelegation.DoesNotExist:
        return Response(
            {'error': 'Délégation de rôle non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RoleDelegationSerializer(delegation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.add')
@audit_sensitive
def role_delegation_create(request):
    """
    Crée une nouvelle délégation de rôle
    """
    serializer = RoleDelegationCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Ajouter le déléguant
        delegation = serializer.save(delegator=request.user)
        
        response_serializer = RoleDelegationSerializer(delegation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.change')
@audit_sensitive
def role_delegation_revoke(request, pk):
    """
    Révoque une délégation de rôle
    """
    try:
        delegation = RoleDelegation.objects.get(pk=pk)
    except RoleDelegation.DoesNotExist:
        return Response(
            {'error': 'Délégation de rôle non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'utilisateur peut révoquer cette délégation
    if delegation.delegator != request.user and not request.user.is_superuser:
        return Response(
            {'error': 'Vous ne pouvez pas révoquer cette délégation'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    delegation.is_active = False
    delegation.save()
    
    return Response({'message': 'Délégation révoquée avec succès'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required('permissions.delegation.view')
@audit_required
def delegation_stats(request):
    """
    Statistiques des délégations
    """
    stats = {
        'total_permission_delegations': PermissionDelegation.objects.count(),
        'active_permission_delegations': PermissionDelegation.objects.filter(is_active=True).count(),
        'expired_permission_delegations': PermissionDelegation.objects.filter(
            end_date__lt=timezone.now()
        ).count(),
        'total_role_delegations': RoleDelegation.objects.count(),
        'active_role_delegations': RoleDelegation.objects.filter(is_active=True).count(),
        'expired_role_delegations': RoleDelegation.objects.filter(
            end_date__lt=timezone.now()
        ).count(),
    }
    
    # Statistiques par permission
    permission_stats = {}
    for delegation in PermissionDelegation.objects.select_related('permission'):
        permission_name = delegation.permission.name
        if permission_name not in permission_stats:
            permission_stats[permission_name] = 0
        permission_stats[permission_name] += 1
    
    stats['delegations_by_permission'] = permission_stats
    
    # Statistiques par rôle
    role_stats = {}
    for delegation in RoleDelegation.objects.select_related('role'):
        role_name = delegation.role.name
        if role_name not in role_stats:
            role_stats[role_name] = 0
        role_stats[role_name] += 1
    
    stats['delegations_by_role'] = role_stats
    
    serializer = DelegationStatsSerializer(stats)
    return Response(serializer.data)
