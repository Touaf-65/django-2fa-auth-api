"""
Vues pour la gestion des notifications SMS
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import SMSNotification
from ..serializers import (
    SMSNotificationSerializer,
    SMSSendSerializer,
    SMSBulkSendSerializer,
)
from ..services import NotificationService

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sms_notification_list(request):
    """
    Liste les notifications SMS de l'utilisateur connecté
    
    GET /api/notifications/sms/
    """
    # Paramètres de filtrage
    status_filter = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Construire la requête
    sms_notifications = SMSNotification.objects.filter(
        notification__user=request.user
    ).select_related('notification')
    
    if status_filter:
        sms_notifications = sms_notifications.filter(notification__status=status_filter)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    sms_page = sms_notifications.order_by('-created_at')[start:end]
    
    serializer = SMSNotificationSerializer(sms_page, many=True, context={'request': request})
    
    return Response({
        'sms': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': sms_notifications.count(),
            'has_next': end < sms_notifications.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sms_notification_detail(request, sms_id):
    """
    Récupère les détails d'une notification SMS
    
    GET /api/notifications/sms/{sms_id}/
    """
    sms_notification = get_object_or_404(
        SMSNotification,
        id=sms_id,
        notification__user=request.user
    )
    
    serializer = SMSNotificationSerializer(sms_notification, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sms_send(request):
    """
    Envoie un SMS
    
    POST /api/notifications/sms/send/
    """
    serializer = SMSSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer l'utilisateur
        user = User.objects.get(id=data['user_id'])
        
        # Envoyer le SMS via le service
        notification_service = NotificationService()
        notification = notification_service.send_sms(
            user=user,
            message=data['message'],
            to_phone=data.get('to_phone'),
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': 'SMS envoyé avec succès.',
            'notification': {
                'id': notification.id,
                'status': notification.status,
                'message': notification.content,
                'recipient_phone': notification.recipient_phone
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sms_bulk_send(request):
    """
    Envoie des SMS en masse
    
    POST /api/notifications/sms/bulk-send/
    """
    serializer = SMSBulkSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer les utilisateurs
        users = User.objects.filter(id__in=data['user_ids'])
        
        # Envoyer les SMS via le service
        notification_service = NotificationService()
        notifications = notification_service.send_bulk_notifications(
            users=users,
            notification_type='sms',
            content=data['message'],
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': f'{len(notifications)} SMS envoyés avec succès.',
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
def sms_stats(request):
    """
    Récupère les statistiques SMS
    
    GET /api/notifications/sms/stats/
    """
    # Statistiques pour l'utilisateur connecté
    user_sms = SMSNotification.objects.filter(notification__user=request.user)
    
    stats = {
        'total_sms': user_sms.count(),
        'sent_sms': user_sms.filter(notification__status='sent').count(),
        'failed_sms': user_sms.filter(notification__status='failed').count(),
        'pending_sms': user_sms.filter(notification__status='pending').count(),
    }
    
    # Calculer le taux de succès
    total = stats['total_sms']
    if total > 0:
        stats['success_rate'] = round((stats['sent_sms'] / total) * 100, 2)
    else:
        stats['success_rate'] = 0.0
    
    return Response(stats, status=status.HTTP_200_OK)
