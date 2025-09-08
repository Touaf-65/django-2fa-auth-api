"""
Service pour l'envoi de SMS via Twilio
"""

from twilio.rest import Client
from django.conf import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """
    Service pour l'envoi de SMS
    """
    
    def __init__(self):
        self.twilio_client = None
        if (hasattr(settings, 'TWILIO_ACCOUNT_SID') and 
            hasattr(settings, 'TWILIO_AUTH_TOKEN') and 
            settings.TWILIO_ACCOUNT_SID and 
            settings.TWILIO_AUTH_TOKEN):
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def send_sms(self, sms_notification) -> Dict[str, Any]:
        """
        Envoie un SMS via Twilio
        
        Args:
            sms_notification: Instance de SMSNotification
            
        Returns:
            Dict avec le résultat de l'envoi
        """
        try:
            if self.twilio_client:
                return self._send_via_twilio(sms_notification)
            else:
                return self._send_via_mock(sms_notification)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_twilio(self, sms_notification) -> Dict[str, Any]:
        """
        Envoie un SMS via Twilio
        """
        try:
            # Envoyer le SMS
            message = self.twilio_client.messages.create(
                body=sms_notification.message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=sms_notification.to_phone
            )
            
            return {
                'success': True,
                'sid': message.sid,
                'status': message.status,
                'provider': 'twilio'
            }
            
        except Exception as e:
            logger.error(f"Erreur Twilio: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'twilio'
            }
    
    def _send_via_mock(self, sms_notification) -> Dict[str, Any]:
        """
        Envoie un SMS via un service mock (pour les tests)
        """
        try:
            # Simuler l'envoi d'un SMS
            logger.info(f"SMS Mock envoyé à {sms_notification.to_phone}: {sms_notification.message}")
            
            return {
                'success': True,
                'sid': f'mock_{sms_notification.id}',
                'status': 'sent',
                'provider': 'mock'
            }
            
        except Exception as e:
            logger.error(f"Erreur Mock SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'mock'
            }
    
    def send_bulk_sms(self, sms_notifications: list) -> Dict[str, Any]:
        """
        Envoie plusieurs SMS en lot
        """
        results = {
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        for sms_notification in sms_notifications:
            result = self.send_sms(sms_notification)
            
            if result['success']:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                results['errors'].append({
                    'phone': sms_notification.to_phone,
                    'error': result.get('error', 'Erreur inconnue')
                })
        
        return results
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Valide un numéro de téléphone
        """
        import re
        # Format international basique
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone) is not None
    
    def format_phone_number(self, phone: str) -> str:
        """
        Formate un numéro de téléphone
        """
        # Supprimer tous les caractères non numériques sauf +
        import re
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Ajouter + si pas présent
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        return cleaned
    
    def get_twilio_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques Twilio
        """
        if not self.twilio_client:
            return {'error': 'Twilio non configuré'}
        
        try:
            # Récupérer les statistiques de base
            account = self.twilio_client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            
            return {
                'provider': 'twilio',
                'account_sid': account.sid,
                'account_name': account.friendly_name,
                'configured': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'provider': 'twilio'
            }



