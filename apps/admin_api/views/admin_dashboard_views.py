"""
Vues API pour AdminDashboard
"""
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import AdminDashboard
from apps.admin_api.serializers import AdminDashboardSerializer, AdminDashboardListSerializer


class AdminDashboardListAPIView(generics.ListAPIView):
    """Liste des dashboards d'administration"""
    queryset = AdminDashboard.objects.filter(is_active=True)
    serializer_class = AdminDashboardListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminDashboardRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un dashboard d'administration"""
    queryset = AdminDashboard.objects.all()
    serializer_class = AdminDashboardSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_dashboard_stats(request):
    """Statistiques pour le dashboard d'administration"""
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    User = get_user_model()
    
    # Statistiques générales
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Utilisateurs récents
    recent_cutoff = timezone.now() - timedelta(days=7)
    new_users = User.objects.filter(date_joined__gte=recent_cutoff).count()
    
    # Actions récentes
    from apps.admin_api.models import AdminAction, AdminLog
    recent_actions = AdminAction.objects.filter(created_at__gte=recent_cutoff).count()
    recent_logs = AdminLog.objects.filter(created_at__gte=recent_cutoff).count()
    
    return Response({
        'users': {
            'total': total_users,
            'active': active_users,
            'staff': staff_users,
            'new_week': new_users,
        },
        'activity': {
            'actions_week': recent_actions,
            'logs_week': recent_logs,
        },
        'system': {
            'dashboards': AdminDashboard.objects.filter(is_active=True).count(),
        }
    })

