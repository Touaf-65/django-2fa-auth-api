"""
Vues API pour AdminAction
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import AdminAction
from apps.admin_api.serializers import (
    AdminActionSerializer,
    AdminActionListSerializer,
    AdminActionCreateSerializer,
    AdminActionUpdateSerializer,
)


class AdminActionListAPIView(generics.ListAPIView):
    """Liste des actions d'administration"""
    queryset = AdminAction.objects.all()
    serializer_class = AdminActionListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'status', 'priority', 'admin_user', 'target_user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'started_at', 'completed_at', 'priority']
    ordering = ['-created_at']


class AdminActionCreateAPIView(generics.CreateAPIView):
    """Créer une action d'administration"""
    queryset = AdminAction.objects.all()
    serializer_class = AdminActionCreateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminActionRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une action d'administration"""
    queryset = AdminAction.objects.all()
    serializer_class = AdminActionSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminActionUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour une action d'administration"""
    queryset = AdminAction.objects.all()
    serializer_class = AdminActionUpdateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminActionDestroyAPIView(generics.DestroyAPIView):
    """Supprimer une action d'administration"""
    queryset = AdminAction.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_action_stats(request):
    """Statistiques des actions d'administration"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Actions par statut
    status_stats = AdminAction.objects.values('status').annotate(count=Count('id'))
    
    # Actions par type
    type_stats = AdminAction.objects.values('action_type').annotate(count=Count('id'))
    
    # Actions récentes (7 derniers jours)
    recent_cutoff = timezone.now() - timedelta(days=7)
    recent_actions = AdminAction.objects.filter(created_at__gte=recent_cutoff).count()
    
    # Actions en cours
    in_progress = AdminAction.objects.filter(status='in_progress').count()
    
    # Actions échouées
    failed_actions = AdminAction.objects.filter(status='failed').count()
    
    return Response({
        'status_stats': list(status_stats),
        'type_stats': list(type_stats),
        'recent_actions': recent_actions,
        'in_progress_actions': in_progress,
        'failed_actions': failed_actions,
    })

