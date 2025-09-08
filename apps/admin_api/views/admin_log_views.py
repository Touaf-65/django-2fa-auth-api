"""
Vues API pour AdminLog
"""
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import AdminLog
from apps.admin_api.serializers import AdminLogSerializer, AdminLogListSerializer


class AdminLogListAPIView(generics.ListAPIView):
    """Liste des logs d'administration"""
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['level', 'admin_user', 'action', 'target_model']
    search_fields = ['message', 'action']
    ordering_fields = ['created_at', 'level']
    ordering = ['-created_at']


class AdminLogRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un log d'administration"""
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_log_stats(request):
    """Statistiques des logs d'administration"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Logs par niveau
    level_stats = AdminLog.objects.values('level').annotate(count=Count('id'))
    
    # Logs par action
    action_stats = AdminLog.objects.values('action').annotate(count=Count('id'))
    
    # Logs récents (24 heures)
    recent_cutoff = timezone.now() - timedelta(hours=24)
    recent_logs = AdminLog.objects.filter(created_at__gte=recent_cutoff).count()
    
    # Logs d'erreur récents
    error_logs = AdminLog.objects.filter(level='error', created_at__gte=recent_cutoff).count()
    
    return Response({
        'level_stats': list(level_stats),
        'action_stats': list(action_stats),
        'recent_logs_24h': recent_logs,
        'error_logs_24h': error_logs,
    })

