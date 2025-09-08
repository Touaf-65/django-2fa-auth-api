"""
Service de notification pour les alertes
"""
from django.utils import timezone
from apps.monitoring.models import AlertNotification
from apps.notifications.services import EmailService, SMSService


class NotificationService:
    """Service de notification pour les alertes"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_notification(self, notification):
        """Envoie une notification d'alerte"""
        try:
            if notification.channel == 'email':
                return self._send_email_notification(notification)
            elif notification.channel == 'sms':
                return self._send_sms_notification(notification)
            elif notification.channel == 'webhook':
                return self._send_webhook_notification(notification)
            else:
                notification.mark_failed(f"Unsupported channel: {notification.channel}")
                return False
        except Exception as e:
            notification.mark_failed(str(e))
            return False
    
    def _send_email_notification(self, notification):
        """Envoie une notification par email"""
        try:
            success = self.email_service.send_email(
                to_email=notification.recipient,
                subject=notification.subject,
                message=notification.message,
                html_message=f"<h2>Alerte {notification.alert.severity.upper()}</h2><p>{notification.message}</p>"
            )
            
            if success:
                notification.mark_sent()
                return True
            else:
                notification.mark_failed("Email service failed")
                return False
        except Exception as e:
            notification.mark_failed(f"Email error: {str(e)}")
            return False
    
    def _send_sms_notification(self, notification):
        """Envoie une notification par SMS"""
        try:
            success = self.sms_service.send_sms(
                to_phone=notification.recipient,
                message=notification.message
            )
            
            if success:
                notification.mark_sent()
                return True
            else:
                notification.mark_failed("SMS service failed")
                return False
        except Exception as e:
            notification.mark_failed(f"SMS error: {str(e)}")
            return False
    
    def _send_webhook_notification(self, notification):
        """Envoie une notification par webhook"""
        try:
            import requests
            
            webhook_url = notification.recipient
            payload = {
                'alert': {
                    'id': notification.alert.id,
                    'rule_name': notification.alert.rule.name,
                    'severity': notification.alert.severity,
                    'message': notification.alert.message,
                    'value': notification.alert.value,
                    'threshold': notification.alert.threshold,
                    'created_at': notification.alert.created_at.isoformat(),
                },
                'notification': {
                    'id': notification.id,
                    'channel': notification.channel,
                    'subject': notification.subject,
                    'message': notification.message,
                }
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                notification.mark_sent()
                return True
            else:
                notification.mark_failed(f"Webhook returned status {response.status_code}")
                return False
        except Exception as e:
            notification.mark_failed(f"Webhook error: {str(e)}")
            return False

