"""
Vues API pour la gestion des utilisateurs par l'admin
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.permissions import IsStaffOrReadOnly
from apps.authentication.serializers import UserSerializer
from apps.admin_api.models import AdminAction, AdminLog

User = get_user_model()


class AdminUserListAPIView(generics.ListAPIView):
    """Liste des utilisateurs pour l'admin"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'email']
    ordering = ['-date_joined']


class AdminUserCreateAPIView(generics.CreateAPIView):
    """Créer un utilisateur (admin)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Log de l'action
        AdminLog.objects.create(
            admin_user=self.request.user,
            action='user_create',
            target_model='User',
            target_id=str(user.id),
            message=f'Utilisateur créé: {user.email}',
            level='info'
        )


class AdminUserRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un utilisateur (admin)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminUserUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour un utilisateur (admin)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def perform_update(self, serializer):
        user = serializer.save()
        # Log de l'action
        AdminLog.objects.create(
            admin_user=self.request.user,
            action='user_update',
            target_model='User',
            target_id=str(user.id),
            message=f'Utilisateur modifié: {user.email}',
            level='info'
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_user_activate(request, user_id):
    """Activer un utilisateur"""
    try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        
        # Log de l'action
        AdminLog.objects.create(
            admin_user=request.user,
            action='user_activate',
            target_model='User',
            target_id=str(user.id),
            message=f'Utilisateur activé: {user.email}',
            level='info'
        )
        
        return Response({'message': 'Utilisateur activé avec succès'})
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_user_deactivate(request, user_id):
    """Désactiver un utilisateur"""
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        
        # Log de l'action
        AdminLog.objects.create(
            admin_user=request.user,
            action='user_deactivate',
            target_model='User',
            target_id=str(user.id),
            message=f'Utilisateur désactivé: {user.email}',
            level='warning'
        )
        
        return Response({'message': 'Utilisateur désactivé avec succès'})
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_user_suspend(request, user_id):
    """Suspendre un utilisateur"""
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        
        # Log de l'action
        AdminLog.objects.create(
            admin_user=request.user,
            action='user_suspend',
            target_model='User',
            target_id=str(user.id),
            message=f'Utilisateur suspendu: {user.email}',
            level='warning'
        )
        
        return Response({'message': 'Utilisateur suspendu avec succès'})
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_user_stats(request):
    """Statistiques des utilisateurs"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Utilisateurs par statut
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Nouveaux utilisateurs (7 derniers jours)
    recent_cutoff = timezone.now() - timedelta(days=7)
    new_users = User.objects.filter(date_joined__gte=recent_cutoff).count()
    
    # Utilisateurs connectés récemment (7 derniers jours)
    recent_login = User.objects.filter(last_login__gte=recent_cutoff).count()
    
    return Response({
        'total_users': User.objects.count(),
        'active_users': active_users,
        'inactive_users': inactive_users,
        'staff_users': staff_users,
        'superusers': superusers,
        'new_users_week': new_users,
        'recent_login_week': recent_login,
    })

