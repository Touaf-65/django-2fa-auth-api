"""
Vues API pour la gestion des performances
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.monitoring.models import PerformanceMetric, PerformanceReport
from apps.monitoring.serializers import (
    PerformanceMetricSerializer, PerformanceReportSerializer
)
from apps.monitoring.services import PerformanceService
from core.permissions import IsStaffOrReadOnly


class PerformanceMetricListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des métriques de performance"""
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']


class PerformanceMetricRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, mettre à jour et supprimer une métrique de performance"""
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class PerformanceReportListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des rapports de performance"""
    queryset = PerformanceReport.objects.all()
    serializer_class = PerformanceReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'is_generated', 'generated_by']
    
    def get_queryset(self):
        """Filtre les rapports selon les permissions"""
        queryset = super().get_queryset()
        
        # Les utilisateurs non-staff ne voient que leurs propres rapports
        if not self.request.user.is_staff:
            queryset = queryset.filter(generated_by=self.request.user)
        
        return queryset.order_by('-created_at')


class PerformanceReportRetrieveView(generics.RetrieveAPIView):
    """Vue pour récupérer un rapport de performance"""
    queryset = PerformanceReport.objects.all()
    serializer_class = PerformanceReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtre les rapports selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(generated_by=self.request.user)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_response_time_view(request):
    """Vue pour enregistrer le temps de réponse d'un endpoint"""
    performance_service = PerformanceService()
    
    endpoint = request.data.get('endpoint')
    method = request.data.get('method', 'GET')
    response_time = request.data.get('response_time')
    status_code = request.data.get('status_code')
    
    if not endpoint or response_time is None:
        return Response(
            {'error': 'endpoint and response_time are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        response_time = float(response_time)
    except (ValueError, TypeError):
        return Response(
            {'error': 'response_time must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Enregistrer le temps de réponse
    metric_value = performance_service.record_response_time(
        endpoint=endpoint,
        method=method,
        response_time=response_time,
        status_code=status_code,
        user=request.user,
        request=request,
    )
    
    return Response({
        'endpoint': endpoint,
        'method': method,
        'response_time': response_time,
        'status_code': status_code,
        'recorded': True
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_throughput_view(request):
    """Vue pour enregistrer le débit d'un endpoint"""
    performance_service = PerformanceService()
    
    endpoint = request.data.get('endpoint')
    method = request.data.get('method', 'GET')
    count = request.data.get('count', 1)
    
    if not endpoint:
        return Response(
            {'error': 'endpoint is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        count = int(count)
    except (ValueError, TypeError):
        return Response(
            {'error': 'count must be an integer'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Enregistrer le débit
    metric_value = performance_service.record_throughput(
        endpoint=endpoint,
        method=method,
        count=count,
        user=request.user,
        request=request,
    )
    
    return Response({
        'endpoint': endpoint,
        'method': method,
        'count': count,
        'recorded': True
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_error_rate_view(request):
    """Vue pour enregistrer le taux d'erreur d'un endpoint"""
    performance_service = PerformanceService()
    
    endpoint = request.data.get('endpoint')
    method = request.data.get('method', 'GET')
    error_count = request.data.get('error_count', 0)
    total_count = request.data.get('total_count', 1)
    
    if not endpoint:
        return Response(
            {'error': 'endpoint is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        error_count = int(error_count)
        total_count = int(total_count)
    except (ValueError, TypeError):
        return Response(
            {'error': 'error_count and total_count must be integers'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Enregistrer le taux d'erreur
    metric_value = performance_service.record_error_rate(
        endpoint=endpoint,
        method=method,
        error_count=error_count,
        total_count=total_count,
        user=request.user,
        request=request,
    )
    
    return Response({
        'endpoint': endpoint,
        'method': method,
        'error_count': error_count,
        'total_count': total_count,
        'error_rate': (error_count / total_count) * 100 if total_count > 0 else 0,
        'recorded': True
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def performance_summary_view(request):
    """Vue pour le résumé des performances"""
    performance_service = PerformanceService()
    hours = int(request.query_params.get('hours', 24))
    
    summary = performance_service.get_performance_summary(hours=hours)
    
    return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def performance_trends_view(request, metric_name):
    """Vue pour les tendances de performance d'une métrique"""
    performance_service = PerformanceService()
    hours = int(request.query_params.get('hours', 24))
    
    trends = performance_service.get_performance_trends(metric_name, hours=hours)
    
    if trends is None:
        return Response(
            {'error': 'Metric not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(trends)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def slow_endpoints_view(request):
    """Vue pour récupérer les endpoints les plus lents"""
    performance_service = PerformanceService()
    hours = int(request.query_params.get('hours', 24))
    limit = int(request.query_params.get('limit', 10))
    
    slow_endpoints = performance_service.get_slow_endpoints(hours=hours, limit=limit)
    
    return Response({
        'slow_endpoints': slow_endpoints,
        'period_hours': hours,
        'limit': limit
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def error_endpoints_view(request):
    """Vue pour récupérer les endpoints avec le plus d'erreurs"""
    performance_service = PerformanceService()
    hours = int(request.query_params.get('hours', 24))
    limit = int(request.query_params.get('limit', 10))
    
    error_endpoints = performance_service.get_error_endpoints(hours=hours, limit=limit)
    
    return Response({
        'error_endpoints': error_endpoints,
        'period_hours': hours,
        'limit': limit
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def generate_performance_report_view(request):
    """Vue pour générer un rapport de performance"""
    performance_service = PerformanceService()
    
    name = request.data.get('name')
    report_type = request.data.get('report_type', 'custom')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    metric_ids = request.data.get('metric_ids', [])
    
    if not all([name, period_start, period_end]):
        return Response(
            {'error': 'name, period_start, and period_end are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from django.utils.dateparse import parse_datetime
        period_start = parse_datetime(period_start)
        period_end = parse_datetime(period_end)
        
        if not period_start or not period_end:
            raise ValueError("Invalid datetime format")
        
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid datetime format for period_start or period_end'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Récupérer les métriques
    metrics = None
    if metric_ids:
        try:
            metrics = PerformanceMetric.objects.filter(id__in=metric_ids)
        except PerformanceMetric.DoesNotExist:
            return Response(
                {'error': 'One or more metrics not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Générer le rapport
    report = performance_service.generate_performance_report(
        name=name,
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        metrics=metrics,
    )
    
    # Marquer comme généré par l'utilisateur
    report.mark_generated(request.user)
    
    serializer = PerformanceReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def performance_statistics_view(request):
    """Vue pour les statistiques de performance"""
    performance_service = PerformanceService()
    hours = int(request.query_params.get('hours', 24))
    
    summary = performance_service.get_performance_summary(hours=hours)
    
    return Response(summary)
