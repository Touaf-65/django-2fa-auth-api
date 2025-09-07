"""
Service pour l'envoi d'emails via SendGrid
"""

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service pour l'envoi d'emails
    """
    
    def __init__(self):
        self.sendgrid_client = None
        if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
            self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    def send_email(self, email_notification) -> Dict[str, Any]:
        """
        Envoie un email via SendGrid ou Django SMTP
        
        Args:
            email_notification: Instance d'EmailNotification
            
        Returns:
            Dict avec le résultat de l'envoi
        """
        try:
            if self.sendgrid_client:
                return self._send_via_sendgrid(email_notification)
            else:
                return self._send_via_django(email_notification)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_sendgrid(self, email_notification) -> Dict[str, Any]:
        """
        Envoie un email via SendGrid
        """
        try:
            # Préparer l'email
            from_email = Email(email_notification.from_email, email_notification.from_name)
            to_email = To(email_notification.to_email, email_notification.to_name)
            
            # Contenu
            plain_text_content = Content("text/plain", email_notification.text_content)
            html_content = Content("text/html", email_notification.html_content)
            
            # Créer le message
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=email_notification.subject,
                plain_text_content=plain_text_content,
                html_content=html_content
            )
            
            # Ajouter les pièces jointes si présentes
            if email_notification.attachments:
                for attachment in email_notification.attachments:
                    mail.add_attachment(attachment)
            
            # Envoyer
            response = self.sendgrid_client.send(mail)
            
            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code,
                'provider': 'sendgrid'
            }
            
        except Exception as e:
            logger.error(f"Erreur SendGrid: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'sendgrid'
            }
    
    def _send_via_django(self, email_notification) -> Dict[str, Any]:
        """
        Envoie un email via Django SMTP
        """
        try:
            # Envoyer l'email
            django_send_mail(
                subject=email_notification.subject,
                message=email_notification.text_content,
                from_email=email_notification.from_email,
                recipient_list=[email_notification.to_email],
                html_message=email_notification.html_content,
                fail_silently=False
            )
            
            return {
                'success': True,
                'provider': 'django_smtp'
            }
            
        except Exception as e:
            logger.error(f"Erreur Django SMTP: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'django_smtp'
            }
    
    def send_bulk_emails(self, email_notifications: list) -> Dict[str, Any]:
        """
        Envoie plusieurs emails en lot
        """
        results = {
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        for email_notification in email_notifications:
            result = self.send_email(email_notification)
            
            if result['success']:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                results['errors'].append({
                    'email': email_notification.to_email,
                    'error': result.get('error', 'Erreur inconnue')
                })
        
        return results
    
    def validate_email(self, email: str) -> bool:
        """
        Valide une adresse email
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_sendgrid_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques SendGrid
        """
        if not self.sendgrid_client:
            return {'error': 'SendGrid non configuré'}
        
        try:
            # Cette fonctionnalité nécessite une configuration SendGrid avancée
            # Pour l'instant, retourner des données de base
            return {
                'provider': 'sendgrid',
                'configured': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'provider': 'sendgrid'
            }
