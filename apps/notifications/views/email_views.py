"""
Vues pour la gestion des notifications email
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import EmailNotification, EmailTemplate
from ..serializers import (
    EmailNotificationSerializer,
    EmailSendSerializer,
    EmailBulkSendSerializer,
    EmailTemplateSerializer,
)
from ..services import NotificationService

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_notification_list(request):
    """
    Liste les notifications email de l'utilisateur connecté
    
    GET /api/notifications/emails/
    """
    # Paramètres de filtrage
    status_filter = request.GET.get('status')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Construire la requête
    email_notifications = EmailNotification.objects.filter(
        notification__user=request.user
    ).select_related('notification', 'template')
    
    if status_filter:
        email_notifications = email_notifications.filter(notification__status=status_filter)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    emails_page = email_notifications.order_by('-created_at')[start:end]
    
    serializer = EmailNotificationSerializer(emails_page, many=True, context={'request': request})
    
    return Response({
        'emails': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': email_notifications.count(),
            'has_next': end < email_notifications.count(),
            'has_previous': page > 1,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_notification_detail(request, email_id):
    """
    Récupère les détails d'une notification email
    
    GET /api/notifications/emails/{email_id}/
    """
    email_notification = get_object_or_404(
        EmailNotification,
        id=email_id,
        notification__user=request.user
    )
    
    serializer = EmailNotificationSerializer(email_notification, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_send(request):
    """
    Envoie un email
    
    POST /api/notifications/emails/send/
    """
    serializer = EmailSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer l'utilisateur
        user = User.objects.get(id=data['user_id'])
        
        # Envoyer l'email via le service
        notification_service = NotificationService()
        notification = notification_service.send_email(
            user=user,
            subject=data['subject'],
            content=data['content'],
            template_name=data.get('template_name'),
            context=data.get('context', {}),
            to_email=data.get('to_email'),
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': 'Email envoyé avec succès.',
            'notification': {
                'id': notification.id,
                'status': notification.status,
                'subject': notification.subject,
                'recipient_email': notification.recipient_email
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_bulk_send(request):
    """
    Envoie des emails en masse
    
    POST /api/notifications/emails/bulk-send/
    """
    serializer = EmailBulkSendSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Récupérer les utilisateurs
        users = User.objects.filter(id__in=data['user_ids'])
        
        # Envoyer les emails via le service
        notification_service = NotificationService()
        notifications = notification_service.send_bulk_notifications(
            users=users,
            notification_type='email',
            subject=data['subject'],
            content=data['content'],
            template_name=data.get('template_name'),
            context=data.get('context', {}),
            priority=data.get('priority', 'normal'),
            scheduled_at=data.get('scheduled_at')
        )
        
        return Response({
            'message': f'{len(notifications)} emails envoyés avec succès.',
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
def email_template_list(request):
    """
    Liste les templates d'emails disponibles
    
    GET /api/notifications/emails/templates/
    """
    templates = EmailTemplate.objects.filter(is_active=True)
    
    from ..serializers import EmailTemplateSerializer
    serializer = EmailTemplateSerializer(templates, many=True, context={'request': request})
    
    return Response({
        'templates': serializer.data,
        'count': len(serializer.data)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_template_detail(request, template_id):
    """
    Récupère les détails d'un template d'email
    
    GET /api/notifications/emails/templates/{template_id}/
    """
    template = get_object_or_404(EmailTemplate, id=template_id, is_active=True)
    
    from ..serializers import EmailTemplateSerializer
    serializer = EmailTemplateSerializer(template, context={'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_template_create(request):
    """
    Crée un nouveau template d'email
    
    POST /api/notifications/emails/templates/create/
    """
    serializer = EmailTemplateSerializer(data=request.data)
    
    if serializer.is_valid():
        template = serializer.save()
        
        return Response({
            'message': 'Template d\'email créé avec succès.',
            'template': EmailTemplateSerializer(template, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def email_template_update(request, template_id):
    """
    Met à jour un template d'email
    
    PUT/PATCH /api/notifications/emails/templates/{template_id}/update/
    """
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    serializer = EmailTemplateSerializer(
        template,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        template = serializer.save()
        
        return Response({
            'message': 'Template d\'email mis à jour avec succès.',
            'template': EmailTemplateSerializer(template, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def email_template_delete(request, template_id):
    """
    Supprime un template d'email
    
    DELETE /api/notifications/emails/templates/{template_id}/delete/
    """
    template = get_object_or_404(EmailTemplate, id=template_id)
    
    # Vérifier qu'aucune notification n'utilise ce template
    from ..models import EmailNotification
    if EmailNotification.objects.filter(template=template).exists():
        return Response({
            'error': 'Ce template est utilisé par des notifications existantes.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    template.delete()
    
    return Response({
        'message': 'Template d\'email supprimé avec succès.'
    }, status=status.HTTP_200_OK)



