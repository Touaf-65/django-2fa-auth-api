"""
Vues API pour la gestion des alertes
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.monitoring.models import Alert, AlertRule, AlertNotification
from apps.monitoring.serializers import (
    AlertSerializer, AlertRuleSerializer, AlertNotificationSerializer
)
from apps.monitoring.services import AlertService
from core.permissions import IsStaffOrReadOnly


class AlertRuleListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des règles d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['severity', 'status', 'is_enabled', 'metric']


class AlertRuleRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, mettre à jour et supprimer une règle d'alerte"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AlertListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des alertes"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'severity', 'rule', 'created_at']
    
    def get_queryset(self):
        """Filtre les alertes selon les permissions"""
        queryset = super().get_queryset()
        
        # Les utilisateurs non-staff ne voient que les alertes de leurs métriques
        if not self.request.user.is_staff:
            queryset = queryset.filter(rule__metric__is_public=True)
        
        return queryset.order_by('-created_at')


class AlertRetrieveView(generics.RetrieveAPIView):
    """Vue pour récupérer une alerte spécifique"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtre les alertes selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(rule__metric__is_public=True)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def acknowledge_alert_view(request, alert_id):
    """Vue pour acquitter une alerte"""
    alert_service = AlertService()
    
    try:
        alert = Alert.objects.get(id=alert_id)
        
        # Vérifier les permissions
        if not request.user.is_staff and not alert.rule.metric.is_public:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert = alert_service.acknowledge_alert(alert, request.user)
        serializer = AlertSerializer(alert)
        
        return Response(serializer.data)
        
    except Alert.DoesNotExist:
        return Response(
            {'error': 'Alert not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def resolve_alert_view(request, alert_id):
    """Vue pour résoudre une alerte"""
    alert_service = AlertService()
    
    try:
        alert = Alert.objects.get(id=alert_id)
        alert = alert_service.resolve_alert(alert)
        serializer = AlertSerializer(alert)
        
        return Response(serializer.data)
        
    except Alert.DoesNotExist:
        return Response(
            {'error': 'Alert not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def active_alerts_view(request):
    """Vue pour récupérer les alertes actives"""
    alert_service = AlertService()
    
    severity = request.query_params.get('severity')
    rule_id = request.query_params.get('rule_id')
    
    if rule_id:
        try:
            from apps.monitoring.models import AlertRule
            rule = AlertRule.objects.get(id=rule_id)
        except AlertRule.DoesNotExist:
            return Response(
                {'error': 'Alert rule not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        rule = None
    
    alerts = alert_service.get_active_alerts(severity=severity, rule=rule)
    
    # Filtrer selon les permissions
    if not request.user.is_staff:
        alerts = alerts.filter(rule__metric__is_public=True)
    
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def alert_statistics_view(request):
    """Vue pour les statistiques des alertes"""
    alert_service = AlertService()
    hours = int(request.query_params.get('hours', 24))
    
    stats = alert_service.get_alert_statistics(hours=hours)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def alert_trends_view(request):
    """Vue pour les tendances des alertes"""
    alert_service = AlertService()
    days = int(request.query_params.get('days', 7))
    
    trends = alert_service.get_alert_trends(days=days)
    
    return Response(trends)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_alert_rule_view(request):
    """Vue pour créer une règle d'alerte"""
    alert_service = AlertService()
    
    name = request.data.get('name')
    metric_id = request.data.get('metric_id')
    condition = request.data.get('condition')
    threshold = request.data.get('threshold')
    
    if not all([name, metric_id, condition, threshold]):
        return Response(
            {'error': 'name, metric_id, condition, and threshold are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from apps.monitoring.models import Metric
        metric = Metric.objects.get(id=metric_id)
    except Metric.DoesNotExist:
        return Response(
            {'error': 'Metric not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        threshold = float(threshold)
    except (ValueError, TypeError):
        return Response(
            {'error': 'threshold must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rule = alert_service.create_alert_rule(
        name=name,
        metric=metric,
        condition=condition,
        threshold=threshold,
        description=request.data.get('description', ''),
        duration=request.data.get('duration', 0),
        severity=request.data.get('severity', 'medium'),
        status=request.data.get('status', 'active'),
        is_enabled=request.data.get('is_enabled', True),
        notification_channels=request.data.get('notification_channels', []),
        notification_template=request.data.get('notification_template', ''),
        tags=request.data.get('tags', []),
        metadata=request.data.get('metadata', {}),
    )
    
    serializer = AlertRuleSerializer(rule)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def test_alert_rule_view(request, rule_id):
    """Vue pour tester une règle d'alerte"""
    alert_service = AlertService()
    
    try:
        rule = AlertRule.objects.get(id=rule_id)
    except AlertRule.DoesNotExist:
        return Response(
            {'error': 'Alert rule not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    test_value = request.data.get('test_value')
    if test_value is None:
        return Response(
            {'error': 'test_value is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        test_value = float(test_value)
    except (ValueError, TypeError):
        return Response(
            {'error': 'test_value must be a number'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = alert_service.test_alert_rule(rule, test_value)
    
    return Response({
        'rule_id': rule.id,
        'rule_name': rule.name,
        'test_value': test_value,
        'threshold': rule.threshold,
        'condition': rule.condition,
        'would_trigger': result,
        'message': f"Value {test_value} {rule.condition} {rule.threshold} = {result}"
    })


class AlertNotificationListView(generics.ListAPIView):
    """Vue pour lister les notifications d'alerte"""
    queryset = AlertNotification.objects.all()
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel', 'status', 'alert', 'created_at']
    
    def get_queryset(self):
        """Filtre les notifications selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par alerte si spécifiée
        alert_id = self.request.query_params.get('alert_id')
        if alert_id:
            queryset = queryset.filter(alert_id=alert_id)
        
        return queryset.order_by('-created_at')


