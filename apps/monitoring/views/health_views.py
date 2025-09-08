"""
Vues API pour la gestion de la santé du système
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.monitoring.models import SystemHealth, HealthCheck, HealthCheckResult
from apps.monitoring.serializers import (
    SystemHealthSerializer, HealthCheckSerializer, HealthCheckResultSerializer
)
from apps.monitoring.services import HealthService
from core.permissions import IsStaffOrReadOnly


class SystemHealthListView(generics.ListAPIView):
    """Vue pour lister les enregistrements de santé du système"""
    queryset = SystemHealth.objects.all()
    serializer_class = SystemHealthSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'created_at']
    
    def get_queryset(self):
        """Filtre les enregistrements selon les permissions"""
        queryset = super().get_queryset()
        return queryset.order_by('-created_at')


class SystemHealthRetrieveView(generics.RetrieveAPIView):
    """Vue pour récupérer un enregistrement de santé du système"""
    queryset = SystemHealth.objects.all()
    serializer_class = SystemHealthSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class HealthCheckListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des vérifications de santé"""
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['check_type', 'is_active']


class HealthCheckRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, mettre à jour et supprimer une vérification de santé"""
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class HealthCheckResultListView(generics.ListAPIView):
    """Vue pour lister les résultats de vérifications de santé"""
    queryset = HealthCheckResult.objects.all()
    serializer_class = HealthCheckResultSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['health_check', 'status', 'created_at']
    
    def get_queryset(self):
        """Filtre les résultats selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par vérification de santé si spécifiée
        health_check_id = self.request.query_params.get('health_check_id')
        if health_check_id:
            queryset = queryset.filter(health_check_id=health_check_id)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def current_system_health_view(request):
    """Vue pour récupérer la santé actuelle du système"""
    health_service = HealthService()
    
    system_health = health_service.get_system_health()
    serializer = SystemHealthSerializer(system_health)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def run_health_check_view(request, health_check_id):
    """Vue pour exécuter une vérification de santé spécifique"""
    health_service = HealthService()
    
    try:
        health_check = HealthCheck.objects.get(id=health_check_id)
    except HealthCheck.DoesNotExist:
        return Response(
            {'error': 'Health check not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    result = health_service.run_health_check(health_check)
    serializer = HealthCheckResultSerializer(result)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def run_all_health_checks_view(request):
    """Vue pour exécuter toutes les vérifications de santé"""
    health_service = HealthService()
    
    results = health_service.run_all_health_checks()
    serializer = HealthCheckResultSerializer(results, many=True)
    
    return Response({
        'results': serializer.data,
        'total_checks': len(results),
        'passed_checks': len([r for r in results if r.status == 'pass']),
        'failed_checks': len([r for r in results if r.status == 'fail']),
        'warning_checks': len([r for r in results if r.status == 'warn']),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def health_statistics_view(request):
    """Vue pour les statistiques de santé"""
    health_service = HealthService()
    hours = int(request.query_params.get('hours', 24))
    
    stats = health_service.get_health_statistics(hours=hours)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def database_health_view(request):
    """Vue pour vérifier la santé de la base de données"""
    health_service = HealthService()
    
    db_health = health_service.check_database_health()
    
    return Response({
        'component': 'database',
        'health': db_health
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def cache_health_view(request):
    """Vue pour vérifier la santé du cache"""
    health_service = HealthService()
    
    cache_health = health_service.check_cache_health()
    
    return Response({
        'component': 'cache',
        'health': cache_health
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def storage_health_view(request):
    """Vue pour vérifier la santé du stockage"""
    health_service = HealthService()
    
    storage_health = health_service.check_storage_health()
    
    return Response({
        'component': 'storage',
        'health': storage_health
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def external_services_health_view(request):
    """Vue pour vérifier la santé des services externes"""
    health_service = HealthService()
    
    external_health = health_service.check_external_services_health()
    
    return Response({
        'component': 'external_services',
        'health': external_health
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def health_check_success_rate_view(request, health_check_id):
    """Vue pour le taux de succès d'une vérification de santé"""
    try:
        health_check = HealthCheck.objects.get(id=health_check_id)
    except HealthCheck.DoesNotExist:
        return Response(
            {'error': 'Health check not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    hours = int(request.query_params.get('hours', 24))
    success_rate = health_check.get_success_rate(hours=hours)
    
    return Response({
        'health_check_id': health_check.id,
        'health_check_name': health_check.name,
        'success_rate': success_rate,
        'period_hours': hours
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def health_check_latest_result_view(request, health_check_id):
    """Vue pour le dernier résultat d'une vérification de santé"""
    try:
        health_check = HealthCheck.objects.get(id=health_check_id)
    except HealthCheck.DoesNotExist:
        return Response(
            {'error': 'Health check not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    latest_result = health_check.get_latest_result()
    
    if not latest_result:
        return Response(
            {'error': 'No results found for this health check'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = HealthCheckResultSerializer(latest_result)
    return Response(serializer.data)
