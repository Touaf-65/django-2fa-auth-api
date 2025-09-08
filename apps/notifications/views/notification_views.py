"""
Vues pour la gestion des notifications
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from ..models import Notification, NotificationTemplate, NotificationLog
from ..serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
)
from ..services import NotificationService

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    Liste les notifications de l'utilisateur connecté
    
    GET /api/notifications/
    """
    # Paramètres de filtrage
    notification_type = request.GET.get('type')
    status_filter = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Construire la requête
    notifications = Notification.objects.filter(user=request.user)
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if status_filter:
        notifications = notifications.filter(status=status_filter)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    notifications_page = notifications.order_by('-created_at')[start:end]
    
    serializer = NotificationSerializer(notifications_page, many=True, context={'request': request})
    
    return Response({
        'notifications': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': notifications.count(),
            'has_next': end < notifications.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_detail(request, notification_id):
    """
    Récupère les détails d'une notification
    
    GET /api/notifications/{notification_id}/
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    serializer = NotificationSerializer(notification, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_create(request):
    """
    Crée une nouvelle notification
    
    POST /api/notifications/create/
    """
    serializer = NotificationCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer l'utilisateur
        user = User.objects.get(id=data['user_id'])
        
        # Créer la notification via le service
        notification_service = NotificationService()
        notification = notification_service.send_notification(
            user=user,
            notification_type=data['notification_type'],
            subject=data.get('subject', ''),
            content=data['content'],
            template_name=data.get('template_name'),
            context=data.get('context', {}),
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at'),
            recipient_email=data.get('recipient_email'),
            recipient_phone=data.get('recipient_phone')
        )
        
        return Response({
            'message': 'Notification créée avec succès.',
            'notification': NotificationSerializer(notification, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """
    Récupère les statistiques des notifications
    
    GET /api/notifications/stats/
    """
    # Statistiques pour l'utilisateur connecté
    user_notifications = Notification.objects.filter(user=request.user)
    
    stats = {
        'total_notifications': user_notifications.count(),
        'sent_notifications': user_notifications.filter(status='sent').count(),
        'failed_notifications': user_notifications.filter(status='failed').count(),
        'pending_notifications': user_notifications.filter(status='pending').count(),
        'email_notifications': user_notifications.filter(notification_type='email').count(),
        'sms_notifications': user_notifications.filter(notification_type='sms').count(),
        'push_notifications': user_notifications.filter(notification_type='push').count(),
    }
    
    # Calculer le taux de succès
    total = stats['total_notifications']
    if total > 0:
        stats['success_rate'] = round((stats['sent_notifications'] / total) * 100, 2)
    else:
        stats['success_rate'] = 0.0
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_retry(request, notification_id):
    """
    Retente l'envoi d'une notification échouée
    
    POST /api/notifications/{notification_id}/retry/
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if not notification.can_retry():
        return Response({
            'error': 'Cette notification ne peut pas être retentée.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Retenter l'envoi via le service
    notification_service = NotificationService()
    notification_service._send_notification(notification)
    
    return Response({
        'message': 'Tentative de renvoi effectuée.',
        'notification': NotificationSerializer(notification, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notification_cancel(request, notification_id):
    """
    Annule une notification en attente
    
    DELETE /api/notifications/{notification_id}/cancel/
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if notification.status not in ['pending', 'scheduled']:
        return Response({
            'error': 'Seules les notifications en attente peuvent être annulées.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    notification.cancel()
    
    return Response({
        'message': 'Notification annulée avec succès.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_logs(request, notification_id):
    """
    Récupère les logs d'une notification
    
    GET /api/notifications/{notification_id}/logs/
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    logs = NotificationLog.objects.filter(notification=notification).order_by('-created_at')
    
    from ..serializers import NotificationLogSerializer
    serializer = NotificationLogSerializer(logs, many=True, context={'request': request})
    
    return Response({
        'logs': serializer.data,
        'count': len(serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_templates(request):
    """
    Liste les templates de notifications disponibles
    
    GET /api/notifications/templates/
    """
    notification_type = request.GET.get('type')
    
    templates = NotificationTemplate.objects.filter(is_active=True)
    
    if notification_type:
        templates = templates.filter(notification_type=notification_type)
    
    from ..serializers import NotificationTemplateSerializer
    serializer = NotificationTemplateSerializer(templates, many=True, context={'request': request})
    
    return Response({
        'templates': serializer.data,
        'count': len(serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_template_detail(request, template_id):
    """
    Récupère les détails d'un template de notification
    
    GET /api/notifications/templates/{template_id}/
    """
    template = get_object_or_404(NotificationTemplate, id=template_id, is_active=True)
    
    from ..serializers import NotificationTemplateSerializer
    serializer = NotificationTemplateSerializer(template, context={'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)



