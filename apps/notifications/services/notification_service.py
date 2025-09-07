"""
Service principal pour la gestion des notifications
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Dict, List, Optional, Any
import logging

from ..models import (
    Notification, NotificationTemplate, NotificationLog,
    EmailNotification, SMSNotification, PushNotification
)
from .email_service import EmailService
from .sms_service import SMSService
from .push_service import PushService

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service principal pour la gestion des notifications
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushService()
    
    def send_notification(
        self,
        user: User,
        notification_type: str,
        subject: str = "",
        content: str = "",
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        scheduled_at: Optional[timezone.datetime] = None,
        **kwargs
    ) -> Notification:
        """
        Envoie une notification à un utilisateur
        
        Args:
            user: Utilisateur destinataire
            notification_type: Type de notification (email, sms, push)
            subject: Sujet de la notification
            content: Contenu de la notification
            template_name: Nom du template à utiliser
            context: Contexte pour le rendu du template
            priority: Priorité de la notification
            scheduled_at: Date de planification
            **kwargs: Arguments supplémentaires
            
        Returns:
            Notification: Instance de la notification créée
        """
        context = context or {}
        
        # Récupérer le template si spécifié
        template = None
        if template_name:
            try:
                template = NotificationTemplate.objects.get(
                    name=template_name,
                    notification_type=notification_type,
                    is_active=True
                )
            except NotificationTemplate.DoesNotExist:
                logger.warning(f"Template {template_name} non trouvé pour {notification_type}")
        
        # Créer la notification
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            template=template,
            subject=subject,
            content=content,
            priority=priority,
            scheduled_at=scheduled_at,
            context=context,
            **kwargs
        )
        
        # Enregistrer le log
        NotificationLog.log_action(
            notification=notification,
            action='created',
            message=f"Notification {notification_type} créée"
        )
        
        # Envoyer immédiatement si pas de planification
        if not scheduled_at:
            self._send_notification(notification)
        
        return notification
    
    def send_email(
        self,
        user: User,
        subject: str,
        content: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        to_email: Optional[str] = None,
        **kwargs
    ) -> Notification:
        """
        Envoie un email à un utilisateur
        """
        return self.send_notification(
            user=user,
            notification_type='email',
            subject=subject,
            content=content,
            template_name=template_name,
            context=context,
            recipient_email=to_email or user.email,
            **kwargs
        )
    
    def send_sms(
        self,
        user: User,
        message: str,
        to_phone: Optional[str] = None,
        **kwargs
    ) -> Notification:
        """
        Envoie un SMS à un utilisateur
        """
        return self.send_notification(
            user=user,
            notification_type='sms',
            content=message,
            recipient_phone=to_phone or user.phone,
            **kwargs
        )
    
    def send_push(
        self,
        user: User,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Notification:
        """
        Envoie une notification push à un utilisateur
        """
        return self.send_notification(
            user=user,
            notification_type='push',
            subject=title,
            content=body,
            context={'data': data or {}},
            **kwargs
        )
    
    def send_bulk_notifications(
        self,
        users: List[User],
        notification_type: str,
        subject: str = "",
        content: str = "",
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Notification]:
        """
        Envoie des notifications en masse
        """
        notifications = []
        for user in users:
            notification = self.send_notification(
                user=user,
                notification_type=notification_type,
                subject=subject,
                content=content,
                template_name=template_name,
                context=context,
                **kwargs
            )
            notifications.append(notification)
        
        return notifications
    
    def _send_notification(self, notification: Notification):
        """
        Envoie une notification selon son type
        """
        try:
            if notification.notification_type == 'email':
                self._send_email_notification(notification)
            elif notification.notification_type == 'sms':
                self._send_sms_notification(notification)
            elif notification.notification_type == 'push':
                self._send_push_notification(notification)
            else:
                logger.error(f"Type de notification non supporté: {notification.notification_type}")
                notification.mark_as_failed()
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification {notification.id}: {str(e)}")
            notification.mark_as_failed()
            NotificationLog.log_action(
                notification=notification,
                action='failed',
                message=f"Erreur: {str(e)}",
                details={'error': str(e)}
            )
    
    def _send_email_notification(self, notification: Notification):
        """
        Envoie une notification email
        """
        try:
            # Créer l'email notification
            email_notification = EmailNotification.objects.create(
                notification=notification,
                to_email=notification.recipient_email,
                to_name=f"{notification.user.first_name} {notification.user.last_name}".strip(),
                subject=notification.render_content(),
                html_content=notification.render_html_content(),
                context=notification.context
            )
            
            # Préparer le contenu
            email_notification.prepare_content()
            
            # Envoyer via le service email
            result = self.email_service.send_email(email_notification)
            
            if result['success']:
                notification.mark_as_sent()
                email_notification.sendgrid_message_id = result.get('message_id', '')
                email_notification.save(update_fields=['sendgrid_message_id'])
                
                NotificationLog.log_action(
                    notification=notification,
                    action='sent',
                    message="Email envoyé avec succès",
                    details=result
                )
            else:
                notification.mark_as_failed()
                NotificationLog.log_action(
                    notification=notification,
                    action='failed',
                    message=f"Échec envoi email: {result.get('error', 'Erreur inconnue')}",
                    details=result
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email {notification.id}: {str(e)}")
            notification.mark_as_failed()
            raise
    
    def _send_sms_notification(self, notification: Notification):
        """
        Envoie une notification SMS
        """
        try:
            # Créer la SMS notification
            sms_notification = SMSNotification.objects.create(
                notification=notification,
                to_phone=notification.recipient_phone,
                message=notification.render_content(),
                context=notification.context
            )
            
            # Envoyer via le service SMS
            result = self.sms_service.send_sms(sms_notification)
            
            if result['success']:
                notification.mark_as_sent()
                sms_notification.update_twilio_status(
                    sid=result.get('sid', ''),
                    status=result.get('status', '')
                )
                
                NotificationLog.log_action(
                    notification=notification,
                    action='sent',
                    message="SMS envoyé avec succès",
                    details=result
                )
            else:
                notification.mark_as_failed()
                NotificationLog.log_action(
                    notification=notification,
                    action='failed',
                    message=f"Échec envoi SMS: {result.get('error', 'Erreur inconnue')}",
                    details=result
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du SMS {notification.id}: {str(e)}")
            notification.mark_as_failed()
            raise
    
    def _send_push_notification(self, notification: Notification):
        """
        Envoie une notification push
        """
        try:
            # Récupérer les tokens push de l'utilisateur
            from ..models import PushToken
            push_tokens = PushToken.objects.filter(
                user=notification.user,
                is_active=True
            )
            
            if not push_tokens.exists():
                logger.warning(f"Aucun token push actif pour l'utilisateur {notification.user.email}")
                notification.mark_as_failed()
                return
            
            # Envoyer à tous les tokens
            success_count = 0
            for push_token in push_tokens:
                try:
                    # Créer la push notification
                    push_notification = PushNotification.objects.create(
                        notification=notification,
                        push_token=push_token,
                        title=notification.subject,
                        body=notification.render_content(),
                        data=notification.context.get('data', {}),
                        context=notification.context
                    )
                    
                    # Envoyer via le service push
                    result = self.push_service.send_push(push_notification)
                    
                    if result['success']:
                        success_count += 1
                        push_notification.update_fcm_status(
                            message_id=result.get('message_id', ''),
                            status=result.get('status', '')
                        )
                        push_token.mark_as_used()
                    else:
                        logger.error(f"Échec envoi push pour token {push_token.id}: {result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi push pour token {push_token.id}: {str(e)}")
            
            if success_count > 0:
                notification.mark_as_sent()
                NotificationLog.log_action(
                    notification=notification,
                    action='sent',
                    message=f"Push envoyé avec succès à {success_count} device(s)",
                    details={'success_count': success_count}
                )
            else:
                notification.mark_as_failed()
                NotificationLog.log_action(
                    notification=notification,
                    action='failed',
                    message="Échec envoi push à tous les devices"
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du push {notification.id}: {str(e)}")
            notification.mark_as_failed()
            raise
    
    def retry_failed_notifications(self, max_retries: int = 3):
        """
        Retente l'envoi des notifications échouées
        """
        failed_notifications = Notification.objects.filter(
            status='failed',
            retry_count__lt=max_retries
        )
        
        for notification in failed_notifications:
            if notification.can_retry():
                self._send_notification(notification)
                NotificationLog.log_action(
                    notification=notification,
                    action='retry',
                    message=f"Tentative {notification.retry_count + 1}"
                )
    
    def get_user_notifications(
        self,
        user: User,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Notification]:
        """
        Récupère les notifications d'un utilisateur
        """
        queryset = Notification.objects.filter(user=user)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return list(queryset.order_by('-created_at')[:limit])
    
    def mark_notification_as_read(self, notification: Notification):
        """
        Marque une notification comme lue
        """
        # Cette fonctionnalité peut être étendue selon les besoins
        pass
