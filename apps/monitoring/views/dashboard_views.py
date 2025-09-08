"""
Vues API pour la gestion des tableaux de bord
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.monitoring.models import Dashboard, DashboardWidget
from apps.monitoring.serializers import (
    DashboardSerializer, DashboardWidgetSerializer
)
from apps.monitoring.services import DashboardService
from core.permissions import IsStaffOrReadOnly


class DashboardListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des tableaux de bord"""
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['visibility', 'is_active', 'owner']
    
    def get_queryset(self):
        """Filtre les tableaux de bord selon les permissions"""
        queryset = super().get_queryset()
        
        # Les utilisateurs voient leurs propres tableaux de bord et les partagés/publics
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(owner=self.request.user) |
                models.Q(visibility__in=['shared', 'public'])
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Assigne le propriétaire lors de la création"""
        serializer.save(owner=self.request.user)


class DashboardRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, mettre à jour et supprimer un tableau de bord"""
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les tableaux de bord selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(owner=self.request.user) |
                models.Q(visibility__in=['shared', 'public'])
            )
        
        return queryset


class DashboardWidgetListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des widgets de tableau de bord"""
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['widget_type', 'is_active', 'dashboard']
    
    def get_queryset(self):
        """Filtre les widgets selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par tableau de bord si spécifié
        dashboard_id = self.request.query_params.get('dashboard_id')
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
        
        # Vérifier les permissions sur le tableau de bord
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                dashboard__owner=self.request.user
            )
        
        return queryset.order_by('position')


class DashboardWidgetRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour récupérer, mettre à jour et supprimer un widget"""
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les widgets selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                dashboard__owner=self.request.user
            )
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data_view(request, dashboard_id):
    """Vue pour récupérer les données d'un tableau de bord"""
    dashboard_service = DashboardService()
    
    dashboard = dashboard_service.get_dashboard(dashboard_id, request.user)
    if not dashboard:
        return Response(
            {'error': 'Dashboard not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = dashboard_service.get_dashboard_data(dashboard)
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_widget_view(request, dashboard_id):
    """Vue pour ajouter un widget à un tableau de bord"""
    dashboard_service = DashboardService()
    
    dashboard = dashboard_service.get_dashboard(dashboard_id, request.user)
    if not dashboard:
        return Response(
            {'error': 'Dashboard not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'utilisateur est le propriétaire
    if dashboard.owner != request.user and not request.user.is_staff:
        return Response(
            {'error': 'Only the owner can add widgets'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    widget_type = request.data.get('widget_type')
    title = request.data.get('title')
    config = request.data.get('config', {})
    
    if not all([widget_type, title]):
        return Response(
            {'error': 'widget_type and title are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    widget = dashboard_service.add_widget(
        dashboard=dashboard,
        widget_type=widget_type,
        title=title,
        config=config,
        position=request.data.get('position'),
        description=request.data.get('description', ''),
        size=request.data.get('size', {'width': 6, 'height': 4}),
        metadata=request.data.get('metadata', {}),
    )
    
    serializer = DashboardWidgetSerializer(widget)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_widgets_view(request, dashboard_id):
    """Vue pour réorganiser les widgets d'un tableau de bord"""
    dashboard_service = DashboardService()
    
    dashboard = dashboard_service.get_dashboard(dashboard_id, request.user)
    if not dashboard:
        return Response(
            {'error': 'Dashboard not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'utilisateur est le propriétaire
    if dashboard.owner != request.user and not request.user.is_staff:
        return Response(
            {'error': 'Only the owner can reorder widgets'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    widget_positions = request.data.get('widget_positions', {})
    
    if not widget_positions:
        return Response(
            {'error': 'widget_positions is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    dashboard_service.reorder_widgets(dashboard, widget_positions)
    
    return Response({'message': 'Widgets reordered successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clone_dashboard_view(request, dashboard_id):
    """Vue pour cloner un tableau de bord"""
    dashboard_service = DashboardService()
    
    source_dashboard = dashboard_service.get_dashboard(dashboard_id, request.user)
    if not source_dashboard:
        return Response(
            {'error': 'Dashboard not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_name = request.data.get('name')
    if not new_name:
        return Response(
            {'error': 'name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    new_dashboard = dashboard_service.clone_dashboard(
        source_dashboard=source_dashboard,
        new_name=new_name,
        new_owner=request.user
    )
    
    serializer = DashboardSerializer(new_dashboard)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboards_view(request):
    """Vue pour récupérer les tableaux de bord d'un utilisateur"""
    dashboard_service = DashboardService()
    
    include_shared = request.query_params.get('include_shared', 'true').lower() == 'true'
    dashboards = dashboard_service.get_user_dashboards(
        user=request.user,
        include_shared=include_shared
    )
    
    serializer = DashboardSerializer(dashboards, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_dashboards_view(request):
    """Vue pour récupérer les tableaux de bord publics"""
    dashboard_service = DashboardService()
    
    dashboards = dashboard_service.get_public_dashboards()
    serializer = DashboardSerializer(dashboards, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def dashboard_statistics_view(request):
    """Vue pour les statistiques des tableaux de bord"""
    dashboard_service = DashboardService()
    
    stats = dashboard_service.get_dashboard_statistics()
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def widget_data_view(request, widget_id):
    """Vue pour récupérer les données d'un widget spécifique"""
    dashboard_service = DashboardService()
    
    try:
        widget = DashboardWidget.objects.get(id=widget_id)
        
        # Vérifier les permissions
        if not request.user.is_staff and widget.dashboard.owner != request.user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = dashboard_service._get_widget_data(widget)
        
        return Response(data)
        
    except DashboardWidget.DoesNotExist:
        return Response(
            {'error': 'Widget not found'},
            status=status.HTTP_404_NOT_FOUND
        )
