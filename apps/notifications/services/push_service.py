"""
Service pour l'envoi de notifications push via Firebase Cloud Messaging
"""

import requests
from django.conf import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PushService:
    """
    Service pour l'envoi de notifications push
    """
    
    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'
    
    def send_push(self, push_notification) -> Dict[str, Any]:
        """
        Envoie une notification push via FCM
        
        Args:
            push_notification: Instance de PushNotification
            
        Returns:
            Dict avec le résultat de l'envoi
        """
        try:
            if self.fcm_server_key:
                return self._send_via_fcm(push_notification)
            else:
                return self._send_via_mock(push_notification)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification push: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_fcm(self, push_notification) -> Dict[str, Any]:
        """
        Envoie une notification push via Firebase Cloud Messaging
        """
        try:
            # Préparer les headers
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }
            
            # Préparer le payload
            payload = {
                'to': push_notification.push_token.token,
                'notification': {
                    'title': push_notification.title,
                    'body': push_notification.body,
                    'sound': push_notification.sound,
                    'badge': push_notification.badge
                },
                'data': push_notification.data
            }
            
            # Envoyer la requête
            response = requests.post(
                self.fcm_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') == 1:
                    return {
                        'success': True,
                        'message_id': result.get('results', [{}])[0].get('message_id'),
                        'status': 'sent',
                        'provider': 'fcm'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('results', [{}])[0].get('error'),
                        'provider': 'fcm'
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'provider': 'fcm'
                }
                
        except Exception as e:
            logger.error(f"Erreur FCM: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'fcm'
            }
    
    def _send_via_mock(self, push_notification) -> Dict[str, Any]:
        """
        Envoie une notification push via un service mock (pour les tests)
        """
        try:
            # Simuler l'envoi d'une notification push
            logger.info(f"Push Mock envoyé à {push_notification.push_token.user.email}: {push_notification.title}")
            
            return {
                'success': True,
                'message_id': f'mock_{push_notification.id}',
                'status': 'sent',
                'provider': 'mock'
            }
            
        except Exception as e:
            logger.error(f"Erreur Mock Push: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'mock'
            }
    
    def send_bulk_push(self, push_notifications: list) -> Dict[str, Any]:
        """
        Envoie plusieurs notifications push en lot
        """
        results = {
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        for push_notification in push_notifications:
            result = self.send_push(push_notification)
            
            if result['success']:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                results['errors'].append({
                    'user': push_notification.push_token.user.email,
                    'error': result.get('error', 'Erreur inconnue')
                })
        
        return results
    
    def send_to_topic(self, topic: str, title: str, body: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Envoie une notification push à un topic
        """
        try:
            if not self.fcm_server_key:
                return {'success': False, 'error': 'FCM non configuré'}
            
            # Préparer les headers
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }
            
            # Préparer le payload
            payload = {
                'to': f'/topics/{topic}',
                'notification': {
                    'title': title,
                    'body': body
                },
                'data': data or {}
            }
            
            # Envoyer la requête
            response = requests.post(
                self.fcm_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message_id': result.get('message_id'),
                    'provider': 'fcm'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'provider': 'fcm'
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi au topic {topic}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_token(self, token: str) -> bool:
        """
        Valide un token FCM
        """
        # Validation basique du format du token
        if not token or len(token) < 100:
            return False
        
        # Vérifier que le token contient des caractères valides
        import re
        pattern = r'^[A-Za-z0-9_-]+$'
        return re.match(pattern, token) is not None
    
    def get_fcm_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques FCM
        """
        return {
            'provider': 'fcm',
            'configured': bool(self.fcm_server_key),
            'server_key_set': bool(self.fcm_server_key)
        }

