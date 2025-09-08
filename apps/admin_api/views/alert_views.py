"""
Vues API pour les alertes système
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import AlertRule, SystemAlert, AlertNotification
from apps.admin_api.services import AlertService, MonitoringService
from apps.admin_api.serializers import (
    AlertRuleSerializer,
    AlertRuleListSerializer,
    AlertRuleCreateSerializer,
    SystemAlertSerializer,
    SystemAlertListSerializer,
    AlertNotificationSerializer,
    AlertNotificationListSerializer,
)


class AlertRuleListAPIView(generics.ListAPIView):
    """Liste des règles d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'status', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'severity', 'name']
    ordering = ['-created_at']


class AlertRuleCreateAPIView(generics.CreateAPIView):
    """Créer une règle d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleCreateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AlertRuleRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une règle d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AlertRuleUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour une règle d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AlertRuleDestroyAPIView(generics.DestroyAPIView):
    """Supprimer une règle d'alerte"""
    queryset = AlertRule.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class SystemAlertListAPIView(generics.ListAPIView):
    """Liste des alertes système"""
    queryset = SystemAlert.objects.all()
    serializer_class = SystemAlertListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'severity', 'alert_rule__alert_type']
    search_fields = ['title', 'message']
    ordering_fields = ['triggered_at', 'severity', 'status']
    ordering = ['-triggered_at']


class SystemAlertRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une alerte système"""
    queryset = SystemAlert.objects.all()
    serializer_class = SystemAlertSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def acknowledge_alert(request, alert_id):
    """Reconnaître une alerte"""
    try:
        alert = SystemAlert.objects.get(id=alert_id)
        alert_service = AlertService()
        alert_service.acknowledge_alert(alert, request.user)
        
        return Response({
            'message': 'Alerte reconnue avec succès',
            'alert_id': alert.id,
            'status': alert.status
        })
    except SystemAlert.DoesNotExist:
        return Response({'error': 'Alerte non trouvée'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def resolve_alert(request, alert_id):
    """Résoudre une alerte"""
    try:
        alert = SystemAlert.objects.get(id=alert_id)
        alert_service = AlertService()
        alert_service.resolve_alert(alert, request.user)
        
        return Response({
            'message': 'Alerte résolue avec succès',
            'alert_id': alert.id,
            'status': alert.status
        })
    except SystemAlert.DoesNotExist:
        return Response({'error': 'Alerte non trouvée'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def alert_statistics(request):
    """Statistiques des alertes"""
    alert_service = AlertService()
    stats = alert_service.get_alert_statistics()
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def check_alerts(request):
    """Vérifier toutes les alertes (manuel)"""
    alert_service = AlertService()
    alert_service.check_all_alerts()
    
    return Response({
        'message': 'Vérification des alertes terminée',
        'timestamp': timezone.now().isoformat()
    })


class AlertNotificationListAPIView(generics.ListAPIView):
    """Liste des notifications d'alerte"""
    queryset = AlertNotification.objects.all()
    serializer_class = AlertNotificationListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['channel_type', 'status', 'alert__severity']
    search_fields = ['subject', 'message']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']


class AlertNotificationRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une notification d'alerte"""
    queryset = AlertNotification.objects.all()
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def system_metrics(request):
    """Métriques système en temps réel"""
    monitoring_service = MonitoringService()
    metrics = monitoring_service.get_cached_metrics()
    
    return Response(metrics)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def system_health(request):
    """Santé du système"""
    monitoring_service = MonitoringService()
    health_score = monitoring_service.get_system_health_score()
    
    health_status = 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical'
    
    return Response({
        'health_score': health_score,
        'status': health_status,
        'timestamp': timezone.now().isoformat()
    })
