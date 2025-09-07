"""
Vues pour la gestion des notifications push
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import PushNotification, PushToken
from ..serializers import (
    PushNotificationSerializer,
    PushSendSerializer,
    PushBulkSendSerializer,
    PushTokenSerializer,
    PushTokenCreateSerializer,
)
from ..services import NotificationService

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def push_notification_list(request):
    """
    Liste les notifications push de l'utilisateur connecté
    
    GET /api/notifications/push/
    """
    # Paramètres de filtrage
    status_filter = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Construire la requête
    push_notifications = PushNotification.objects.filter(
        push_token__user=request.user
    ).select_related('notification', 'push_token')
    
    if status_filter:
        push_notifications = push_notifications.filter(notification__status=status_filter)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    push_page = push_notifications.order_by('-created_at')[start:end]
    
    serializer = PushNotificationSerializer(push_page, many=True, context={'request': request})
    
    return Response({
        'push_notifications': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': push_notifications.count(),
            'has_next': end < push_notifications.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def push_notification_detail(request, push_id):
    """
    Récupère les détails d'une notification push
    
    GET /api/notifications/push/{push_id}/
    """
    push_notification = get_object_or_404(
        PushNotification,
        id=push_id,
        push_token__user=request.user
    )
    
    serializer = PushNotificationSerializer(push_notification, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def push_send(request):
    """
    Envoie une notification push
    
    POST /api/notifications/push/send/
    """
    serializer = PushSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer l'utilisateur
        user = User.objects.get(id=data['user_id'])
        
        # Envoyer la notification push via le service
        notification_service = NotificationService()
        notification = notification_service.send_push(
            user=user,
            title=data['title'],
            body=data['body'],
            data=data.get('data', {}),
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': 'Notification push envoyée avec succès.',
            'notification': {
                'id': notification.id,
                'status': notification.status,
                'title': notification.subject,
                'body': notification.content
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def push_bulk_send(request):
    """
    Envoie des notifications push en masse
    
    POST /api/notifications/push/bulk-send/
    """
    serializer = PushBulkSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer les utilisateurs
        users = User.objects.filter(id__in=data['user_ids'])
        
        # Envoyer les notifications push via le service
        notification_service = NotificationService()
        notifications = notification_service.send_bulk_notifications(
            users=users,
            notification_type='push',
            subject=data['title'],
            content=data['body'],
            context={'data': data.get('data', {})},
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': f'{len(notifications)} notifications push envoyées avec succès.',
            'notifications_count': len(notifications),
            'notifications': [
                {
                    'id': n.id,
                    'user_email': n.user.email,
                    'status': n.status
                } for n in notifications
            ]
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def push_token_list(request):
    """
    Liste les tokens push de l'utilisateur connecté
    
    GET /api/notifications/push/tokens/
    """
    tokens = PushToken.objects.filter(user=request.user, is_active=True)
    
    serializer = PushTokenSerializer(tokens, many=True, context={'request': request})
    
    return Response({
        'tokens': serializer.data,
        'count': len(serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def push_token_create(request):
    """
    Crée un nouveau token push
    
    POST /api/notifications/push/tokens/create/
    """
    serializer = PushTokenCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Créer ou mettre à jour le token
        token, created = PushToken.objects.update_or_create(
            user=request.user,
            token=data['token'],
            defaults={
                'device_type': data['device_type'],
                'device_id': data.get('device_id', ''),
                'device_name': data.get('device_name', ''),
                'app_version': data.get('app_version', ''),
                'is_active': True
            }
        )
        
        action = 'créé' if created else 'mis à jour'
        
        return Response({
            'message': f'Token push {action} avec succès.',
            'token': PushTokenSerializer(token, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def push_token_delete(request, token_id):
    """
    Supprime un token push
    
    DELETE /api/notifications/push/tokens/{token_id}/delete/
    """
    token = get_object_or_404(PushToken, id=token_id, user=request.user)
    
    token.delete()
    
    return Response({
        'message': 'Token push supprimé avec succès.'
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def push_token_update(request, token_id):
    """
    Met à jour un token push
    
    PUT/PATCH /api/notifications/push/tokens/{token_id}/update/
    """
    token = get_object_or_404(PushToken, id=token_id, user=request.user)
    
    serializer = PushTokenSerializer(
        token,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        token = serializer.save()
        
        return Response({
            'message': 'Token push mis à jour avec succès.',
            'token': PushTokenSerializer(token, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def push_stats(request):
    """
    Récupère les statistiques des notifications push
    
    GET /api/notifications/push/stats/
    """
    # Statistiques pour l'utilisateur connecté
    user_push = PushNotification.objects.filter(push_token__user=request.user)
    
    stats = {
        'total_push': user_push.count(),
        'sent_push': user_push.filter(notification__status='sent').count(),
        'failed_push': user_push.filter(notification__status='failed').count(),
        'pending_push': user_push.filter(notification__status='pending').count(),
        'active_tokens': PushToken.objects.filter(user=request.user, is_active=True).count(),
    }
    
    # Calculer le taux de succès
    total = stats['total_push']
    if total > 0:
        stats['success_rate'] = round((stats['sent_push'] / total) * 100, 2)
    else:
        stats['success_rate'] = 0.0
    
    return Response(stats, status=status.HTTP_200_OK)
