"""
Vues API pour les tableaux de bord Analytics
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.analytics.models import AnalyticsDashboard, DashboardWidget
from apps.analytics.serializers import (
    AnalyticsDashboardSerializer, AnalyticsDashboardCreateSerializer,
    DashboardWidgetSerializer, DashboardWidgetCreateSerializer,
    DashboardDataSerializer, DashboardShareSerializer, DashboardLayoutSerializer,
    DashboardSummarySerializer
)
# from apps.analytics.services import DashboardService  # Service supprimé


class AnalyticsDashboardListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des tableaux de bord"""
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les tableaux de bord selon les permissions"""
        user = self.request.user
        
        # L'utilisateur voit ses propres tableaux de bord et ceux partagés avec lui
        queryset = AnalyticsDashboard.objects.filter(
            Q(owner=user) | Q(shared_with=user) | Q(is_public=True)
        ).distinct()
        
        # Filtrer par type si spécifié
        dashboard_type = self.request.query_params.get('type')
        if dashboard_type:
            queryset = queryset.filter(dashboard_type=dashboard_type)
        
        # Filtrer par propriétaire si spécifié
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner__email=owner)
        
        # Filtrer par visibilité si spécifié
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Associe l'utilisateur propriétaire"""
        serializer.save(owner=self.request.user)


class AnalyticsDashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'un tableau de bord"""
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les tableaux de bord selon les permissions"""
        user = self.request.user
        return AnalyticsDashboard.objects.filter(
            Q(owner=user) | Q(shared_with=user) | Q(is_public=True)
        ).distinct()
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.owner != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres tableaux de bord")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Vérifie les permissions de suppression"""
        if instance.owner != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres tableaux de bord")
        instance.delete()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_data(request, dashboard_id):
    """Récupère les données d'un tableau de bord"""
    try:
        dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id
        )
        
        # Vérifier les permissions
        user = request.user
        if not (dashboard.owner == user or user in dashboard.shared_with.all() or dashboard.is_public):
            return Response(
                {'error': 'Accès non autorisé à ce tableau de bord'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer les données des widgets
        widgets = dashboard.widgets.all()
        widgets_data = []
        
        for widget in widgets:
            widget_data = {
                'id': widget.id,
                'name': widget.name,
                'type': widget.widget_type,
                'config': widget.config,
                'data': []  # Données simulées pour l'instant
            }
            widgets_data.append(widget_data)
        
        data = {
            'dashboard': AnalyticsDashboardSerializer(dashboard).data,
            'widgets': widgets_data
        }
        
        return Response(data)
        
    except AnalyticsDashboard.DoesNotExist:
        return Response(
            {'error': 'Tableau de bord non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_dashboard(request, dashboard_id):
    """Partage un tableau de bord avec d'autres utilisateurs"""
    try:
        dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id,
            owner=request.user
        )
        
        serializer = DashboardShareSerializer(data=request.data)
        if serializer.is_valid():
            user_emails = serializer.validated_data['user_emails']
            
            # Ajouter les utilisateurs au partage
            from apps.users.models import User
            users_to_share = User.objects.filter(email__in=user_emails)
            dashboard.shared_with.add(*users_to_share)
            
            return Response(
                {'message': f'Tableau de bord partagé avec {len(user_emails)} utilisateurs'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except AnalyticsDashboard.DoesNotExist:
        return Response(
            {'error': 'Tableau de bord non trouvé ou accès non autorisé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_dashboard_layout(request, dashboard_id):
    """Met à jour la mise en page d'un tableau de bord"""
    try:
        dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id,
            owner=request.user
        )
        
        serializer = DashboardLayoutSerializer(data=request.data)
        if serializer.is_valid():
            widgets_data = serializer.validated_data['widgets']
            
            # Mettre à jour la position de chaque widget
            for widget_data in widgets_data:
                widget = get_object_or_404(
                    DashboardWidget,
                    id=widget_data['id'],
                    dashboard=dashboard
                )
                widget.position_x = widget_data['position_x']
                widget.position_y = widget_data['position_y']
                widget.width = widget_data['width']
                widget.height = widget_data['height']
                widget.save()
            
            return Response(
                {'message': 'Mise en page mise à jour avec succès'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except AnalyticsDashboard.DoesNotExist:
        return Response(
            {'error': 'Tableau de bord non trouvé ou accès non autorisé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DashboardWidgetListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des widgets de tableau de bord"""
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les widgets selon les permissions"""
        dashboard_id = self.kwargs.get('dashboard_id')
        user = self.request.user
        
        # Vérifier que l'utilisateur peut accéder au tableau de bord
        dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id
        )
        
        if not (dashboard.owner == user or user in dashboard.shared_with.all() or dashboard.is_public):
            raise permissions.PermissionDenied("Accès non autorisé à ce tableau de bord")
        
        return DashboardWidget.objects.filter(dashboard=dashboard)
    
    def perform_create(self, serializer):
        """Associe le widget au tableau de bord"""
        dashboard_id = self.kwargs.get('dashboard_id')
        dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id,
            owner=self.request.user
        )
        serializer.save(dashboard=dashboard)


class DashboardWidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'un widget de tableau de bord"""
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les widgets selon les permissions"""
        user = self.request.user
        return DashboardWidget.objects.filter(
            dashboard__owner=user
        )
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.dashboard.owner != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres widgets")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Vérifie les permissions de suppression"""
        if instance.dashboard.owner != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres widgets")
        instance.delete()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def widget_data(request, widget_id):
    """Récupère les données d'un widget"""
    try:
        widget = get_object_or_404(DashboardWidget, id=widget_id)
        
        # Vérifier les permissions
        user = request.user
        dashboard = widget.dashboard
        
        if not (dashboard.owner == user or user in dashboard.shared_with.all() or dashboard.is_public):
            return Response(
                {'error': 'Accès non autorisé à ce widget'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Données simulées pour le widget
        data = {
            'widget_id': widget.id,
            'name': widget.name,
            'type': widget.widget_type,
            'config': widget.config,
            'data': []  # Données simulées pour l'instant
        }
        
        return Response(data)
        
    except DashboardWidget.DoesNotExist:
        return Response(
            {'error': 'Widget non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    """Récupère un résumé des tableaux de bord de l'utilisateur"""
    try:
        user = request.user
        
        # Tableaux de bord de l'utilisateur
        user_dashboards = AnalyticsDashboard.objects.filter(owner=user)
        
        # Tableaux de bord partagés avec l'utilisateur
        shared_dashboards = AnalyticsDashboard.objects.filter(shared_with=user)
        
        # Tableaux de bord publics
        public_dashboards = AnalyticsDashboard.objects.filter(is_public=True)
        
        summary = {
            'total_dashboards': user_dashboards.count(),
            'public_dashboards': user_dashboards.filter(is_public=True).count(),
            'private_dashboards': user_dashboards.filter(is_public=False).count(),
            'total_widgets': DashboardWidget.objects.filter(
                dashboard__in=user_dashboards
            ).count(),
            'most_viewed_dashboard': user_dashboards.order_by('-view_count').first().name if user_dashboards.exists() else None,
            'recent_dashboards': AnalyticsDashboardSerializer(
                user_dashboards.order_by('-created_at')[:5], many=True
            ).data
        }
        
        return Response(summary)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_dashboard(request, dashboard_id):
    """Duplique un tableau de bord"""
    try:
        original_dashboard = get_object_or_404(
            AnalyticsDashboard,
            id=dashboard_id
        )
        
        # Vérifier les permissions
        user = request.user
        if not (original_dashboard.owner == user or user in original_dashboard.shared_with.all() or original_dashboard.is_public):
            return Response(
                {'error': 'Accès non autorisé à ce tableau de bord'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Créer une copie du tableau de bord
        new_dashboard = AnalyticsDashboard.objects.create(
            name=f"{original_dashboard.name} (Copie)",
            description=original_dashboard.description,
            dashboard_type=original_dashboard.dashboard_type,
            layout_config=original_dashboard.layout_config,
            refresh_interval=original_dashboard.refresh_interval,
            is_public=False,  # Les copies sont privées par défaut
            owner=user
        )
        
        # Copier les widgets
        for widget in original_dashboard.widgets.all():
            DashboardWidget.objects.create(
                dashboard=new_dashboard,
                name=widget.name,
                widget_type=widget.widget_type,
                config=widget.config,
                data_source=widget.data_source,
                query=widget.query,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                chart_type=widget.chart_type,
                x_axis=widget.x_axis,
                y_axis=widget.y_axis,
                filters=widget.filters,
                refresh_interval=widget.refresh_interval,
                is_visible=widget.is_visible
            )
        
        serializer = AnalyticsDashboardSerializer(new_dashboard)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except AnalyticsDashboard.DoesNotExist:
        return Response(
            {'error': 'Tableau de bord non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

