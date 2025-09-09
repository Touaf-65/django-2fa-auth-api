"""
Vues API pour les métriques Analytics
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from apps.analytics.models import AnalyticsMetric, MetricValue
from apps.analytics.serializers import (
    AnalyticsMetricSerializer, AnalyticsMetricCreateSerializer,
    MetricValueSerializer, MetricValueCreateSerializer,
    MetricTrendSerializer, MetricComparisonSerializer, MetricAlertSerializer,
    MetricSummarySerializer, MetricCalculationSerializer, MetricBulkUpdateSerializer
)
from apps.analytics.services import AnalyticsService


class AnalyticsMetricListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des métriques analytiques"""
    serializer_class = AnalyticsMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les métriques selon les permissions"""
        queryset = AnalyticsMetric.objects.filter(is_active=True)
        
        # Filtrer par catégorie si spécifié
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtrer par type si spécifié
        metric_type = self.request.query_params.get('type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        # Filtrer par alertes activées si spécifié
        alert_enabled = self.request.query_params.get('alert_enabled')
        if alert_enabled is not None:
            queryset = queryset.filter(alert_enabled=alert_enabled.lower() == 'true')
        
        return queryset.order_by('category', 'name')


class AnalyticsMetricDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'une métrique analytique"""
    serializer_class = AnalyticsMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les métriques selon les permissions"""
        return AnalyticsMetric.objects.filter(is_active=True)
    
    def perform_destroy(self, instance):
        """Marque la métrique comme inactive au lieu de la supprimer"""
        instance.is_active = False
        instance.save()


class MetricValueListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des valeurs de métriques"""
    serializer_class = MetricValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les valeurs de métriques"""
        queryset = MetricValue.objects.all()
        
        # Filtrer par métrique si spécifié
        metric_id = self.request.query_params.get('metric_id')
        if metric_id:
            queryset = queryset.filter(metric_id=metric_id)
        
        # Filtrer par nom de métrique si spécifié
        metric_name = self.request.query_params.get('metric_name')
        if metric_name:
            queryset = queryset.filter(metric__name=metric_name)
        
        # Filtrer par date si spécifié
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        # Limiter le nombre de résultats
        limit = self.request.query_params.get('limit', 100)
        try:
            limit = int(limit)
            if limit > 1000:  # Limite maximale
                limit = 1000
        except ValueError:
            limit = 100
        
        return queryset.order_by('-timestamp')[:limit]


class MetricValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'une valeur de métrique"""
    serializer_class = MetricValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les valeurs de métriques"""
        return MetricValue.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def calculate_metric(request, metric_name):
    """Calcule une métrique spécifique"""
    try:
        analytics_service = AnalyticsService()
        
        # Récupérer les paramètres de la requête
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        labels = request.data.get('labels', {})
        
        # Convertir les dates si fournies
        if start_date:
            start_date = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Calculer la métrique
        start_time = timezone.now()
        result = analytics_service.calculate_metric(metric_name, start_date, end_date, labels)
        calculation_time = (timezone.now() - start_time).total_seconds()
        
        response_data = {
            'metric_name': metric_name,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'labels': labels,
            'result': result,
            'calculation_time': calculation_time,
            'cached': False  # TODO: Implémenter la détection du cache
        }
        
        return Response(response_data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def metric_trend(request, metric_name):
    """Récupère la tendance d'une métrique"""
    try:
        analytics_service = AnalyticsService()
        
        # Récupérer les paramètres de la requête
        days = int(request.query_params.get('days', 30))
        granularity = request.query_params.get('granularity', 'day')
        
        # Valider les paramètres
        if days < 1 or days > 365:
            return Response(
                {'error': 'Le nombre de jours doit être entre 1 et 365'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if granularity not in ['hour', 'day', 'week']:
            return Response(
                {'error': 'La granularité doit être hour, day ou week'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer la tendance
        trend_data = analytics_service.get_metric_trend(metric_name, days, granularity)
        
        response_data = {
            'metric_name': metric_name,
            'period_days': days,
            'granularity': granularity,
            'data': trend_data
        }
        
        return Response(response_data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def top_metrics(request):
    """Récupère les métriques les plus importantes"""
    try:
        analytics_service = AnalyticsService()
        
        # Récupérer les paramètres de la requête
        category = request.query_params.get('category')
        limit = int(request.query_params.get('limit', 10))
        
        # Valider les paramètres
        if limit < 1 or limit > 50:
            return Response(
                {'error': 'La limite doit être entre 1 et 50'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les métriques
        metrics = analytics_service.get_top_metrics(category, limit)
        
        return Response(metrics)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_metric(request):
    """Crée une nouvelle métrique"""
    try:
        serializer = AnalyticsMetricCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        analytics_service = AnalyticsService()
        metric = analytics_service.create_metric(**serializer.validated_data)
        
        response_serializer = AnalyticsMetricSerializer(metric)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_metric(request, metric_name):
    """Met à jour une métrique existante"""
    try:
        analytics_service = AnalyticsService()
        
        # Récupérer les données de mise à jour
        update_data = request.data
        
        # Mettre à jour la métrique
        metric = analytics_service.update_metric(metric_name, **update_data)
        
        serializer = AnalyticsMetricSerializer(metric)
        return Response(serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_metric(request, metric_name):
    """Supprime une métrique"""
    try:
        analytics_service = AnalyticsService()
        analytics_service.delete_metric(metric_name)
        
        return Response(
            {'message': f'Métrique {metric_name} supprimée avec succès'},
            status=status.HTTP_200_OK
        )
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_metrics(request):
    """Met à jour plusieurs métriques en lot"""
    try:
        serializer = MetricBulkUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        analytics_service = AnalyticsService()
        updated_metrics = []
        
        for metric_data in serializer.validated_data['metrics']:
            try:
                metric_name = metric_data.pop('name')
                metric = analytics_service.update_metric(metric_name, **metric_data)
                updated_metrics.append(metric)
            except Exception as e:
                # Continuer avec les autres métriques même si une échoue
                continue
        
        response_serializer = AnalyticsMetricSerializer(updated_metrics, many=True)
        return Response(response_serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def metric_summary(request):
    """Récupère un résumé des métriques"""
    try:
        # Statistiques générales
        total_metrics = AnalyticsMetric.objects.filter(is_active=True).count()
        active_metrics = AnalyticsMetric.objects.filter(is_active=True).count()
        
        # Métriques par catégorie
        metrics_by_category = {}
        for category, _ in AnalyticsMetric.CATEGORY_CHOICES:
            count = AnalyticsMetric.objects.filter(
                category=category, is_active=True
            ).count()
            metrics_by_category[category] = count
        
        # Métriques par type
        metrics_by_type = {}
        for metric_type, _ in AnalyticsMetric.TYPE_CHOICES:
            count = AnalyticsMetric.objects.filter(
                metric_type=metric_type, is_active=True
            ).count()
            metrics_by_type[metric_type] = count
        
        # Alertes déclenchées (exemple)
        alerts_triggered = 0  # TODO: Implémenter la logique des alertes
        
        # Top métriques
        top_metrics = AnalyticsMetric.objects.filter(
            is_active=True
        ).order_by('-last_calculated')[:5]
        
        summary = {
            'total_metrics': total_metrics,
            'active_metrics': active_metrics,
            'metrics_by_category': metrics_by_category,
            'metrics_by_type': metrics_by_type,
            'alerts_triggered': alerts_triggered,
            'top_metrics': AnalyticsMetricSerializer(top_metrics, many=True).data
        }
        
        return Response(summary)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

