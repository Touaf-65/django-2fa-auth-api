"""
Vues API pour la gestion des métriques
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv
import json

from apps.monitoring.models import Metric, MetricValue
from apps.monitoring.serializers import MetricSerializer, MetricValueSerializer
from apps.monitoring.services import MetricsService
from core.permissions import IsStaffOrReadOnly


class MetricListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des métriques"""
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['metric_type', 'unit', 'is_active', 'is_public']
    
    def get_queryset(self):
        """Filtre les métriques selon les permissions"""
        queryset = super().get_queryset()
        
        # Les utilisateurs non-staff ne voient que les métriques publiques
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        
        return queryset.order_by('name')


class MetricRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Vue pour récupérer et mettre à jour une métrique"""
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtre les métriques selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        
        return queryset


class MetricValueListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des valeurs de métriques"""
    queryset = MetricValue.objects.all()
    serializer_class = MetricValueSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['metric', 'user', 'timestamp']
    
    def get_queryset(self):
        """Filtre les valeurs selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par métrique si spécifiée
        metric_name = self.request.query_params.get('metric_name')
        if metric_name:
            queryset = queryset.filter(metric__name=metric_name)
        
        # Les utilisateurs non-staff ne voient que les métriques publiques
        if not self.request.user.is_staff:
            queryset = queryset.filter(metric__is_public=True)
        
        return queryset.order_by('-timestamp')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_metric_view(request):
    """Vue pour enregistrer une valeur de métrique"""
    metrics_service = MetricsService()
    
    metric_name = request.data.get('metric_name')
    value = request.data.get('value')
    labels = request.data.get('labels', {})
    metadata = request.data.get('metadata', {})
    
    if not metric_name or value is None:
        return Response(
            {'error': 'metric_name and value are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return Response(
            {'error': 'value must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Enregistrer la métrique
    metric_value = metrics_service.record_metric(
        metric_name=metric_name,
        value=value,
        labels=labels,
        metadata=metadata,
        user=request.user,
        request=request,
    )
    
    serializer = MetricValueSerializer(metric_value)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_counter_view(request):
    """Vue pour incrémenter un compteur"""
    metrics_service = MetricsService()
    
    metric_name = request.data.get('metric_name')
    value = request.data.get('value', 1)
    labels = request.data.get('labels', {})
    
    if not metric_name:
        return Response(
            {'error': 'metric_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return Response(
            {'error': 'value must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Incrémenter le compteur
    metric_value = metrics_service.increment_counter(
        metric_name=metric_name,
        value=value,
        labels=labels,
        user=request.user,
        request=request,
    )
    
    serializer = MetricValueSerializer(metric_value)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_gauge_view(request):
    """Vue pour définir un gauge"""
    metrics_service = MetricsService()
    
    metric_name = request.data.get('metric_name')
    value = request.data.get('value')
    labels = request.data.get('labels', {})
    
    if not metric_name or value is None:
        return Response(
            {'error': 'metric_name and value are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return Response(
            {'error': 'value must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Définir le gauge
    metric_value = metrics_service.set_gauge(
        metric_name=metric_name,
        value=value,
        labels=labels,
        user=request.user,
        request=request,
    )
    
    serializer = MetricValueSerializer(metric_value)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def metric_statistics_view(request):
    """Vue pour les statistiques des métriques"""
    metrics_service = MetricsService()
    hours = int(request.query_params.get('hours', 24))
    
    stats = metrics_service.get_metrics_summary(hours=hours)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def metric_value_statistics_view(request, metric_name):
    """Vue pour les statistiques d'une métrique spécifique"""
    metrics_service = MetricsService()
    
    hours = int(request.query_params.get('hours', 24))
    labels = request.query_params.get('labels')
    
    if labels:
        try:
            labels = json.loads(labels)
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid labels JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    from datetime import timedelta
    from django.utils import timezone
    
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)
    
    stats = metrics_service.get_metric_statistics(
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        labels=labels
    )
    
    if stats is None:
        return Response(
            {'error': 'Metric not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def metric_export_view(request):
    """Vue pour exporter les métriques"""
    metrics_service = MetricsService()
    
    # Paramètres d'export
    metric_name = request.query_params.get('metric_name')
    hours = int(request.query_params.get('hours', 24))
    format_type = request.query_params.get('format', 'csv')
    
    if not metric_name:
        return Response(
            {'error': 'metric_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from datetime import timedelta
    from django.utils import timezone
    
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Récupérer les valeurs
    values = metrics_service.get_metric_values(
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time
    )
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{metric_name}_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Value', 'Labels', 'Metadata'])
        
        for value in values:
            writer.writerow([
                value.timestamp.isoformat(),
                value.value,
                json.dumps(value.labels),
                json.dumps(value.metadata),
            ])
        
        return response
    
    elif format_type == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{metric_name}_export.json"'
        
        values_data = []
        for value in values:
            values_data.append({
                'timestamp': value.timestamp.isoformat(),
                'value': value.value,
                'labels': value.labels,
                'metadata': value.metadata,
            })
        
        response.write(json.dumps(values_data, indent=2))
        return response
    
    else:
        return Response(
            {'error': 'Unsupported format. Use csv or json.'},
            status=status.HTTP_400_BAD_REQUEST
        )


