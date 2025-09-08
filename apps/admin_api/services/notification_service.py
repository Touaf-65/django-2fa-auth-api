"""
Service de notification pour les alertes
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.admin_api.models import AlertNotification
from apps.notifications.services import EmailService, SMSService


class NotificationService:
    """Service de notification pour les alertes"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_alert_notification(self, notification):
        """Envoie une notification d'alerte"""
        try:
            if notification.channel_type == 'email':
                return self._send_email_notification(notification)
            elif notification.channel_type == 'sms':
                return self._send_sms_notification(notification)
            elif notification.channel_type == 'webhook':
                return self._send_webhook_notification(notification)
            elif notification.channel_type == 'slack':
                return self._send_slack_notification(notification)
            elif notification.channel_type == 'teams':
                return self._send_teams_notification(notification)
            elif notification.channel_type == 'discord':
                return self._send_discord_notification(notification)
            else:
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi de notification: {e}")
            notification.error_message = str(e)
            notification.retry_count += 1
            notification.save()
            return False
    
    def _send_email_notification(self, notification):
        """Envoie une notification par email"""
        try:
            # Utilise le service d'email existant
            success = self.email_service.send_email(
                to_email=notification.recipient,
                subject=notification.subject,
                message=notification.message,
                html_message=f"<h2>Alerte {notification.alert.severity.upper()}</h2><p>{notification.message}</p>"
            )
            
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = 'Failed to send email'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
    
    def _send_sms_notification(self, notification):
        """Envoie une notification par SMS"""
        try:
            # Utilise le service SMS existant
            success = self.sms_service.send_sms(
                phone_number=notification.recipient,
                message=notification.message
            )
            
            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = 'Failed to send SMS'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
    
    def _send_webhook_notification(self, notification):
        """Envoie une notification par webhook"""
        try:
            import requests
            
            webhook_url = notification.recipient
            payload = {
                'alert_id': notification.alert.id,
                'title': notification.alert.title,
                'message': notification.message,
                'severity': notification.alert.severity,
                'alert_type': notification.alert.alert_rule.alert_type,
                'triggered_at': notification.alert.triggered_at.isoformat(),
                'current_value': notification.alert.current_value,
                'threshold_value': notification.alert.threshold_value,
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = f'HTTP {response.status_code}'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
    
    def _send_slack_notification(self, notification):
        """Envoie une notification par Slack"""
        try:
            import requests
            
            webhook_url = notification.recipient
            
            # Couleur selon la sévérité
            color_map = {
                'low': '#36a64f',      # Vert
                'medium': '#ffaa00',   # Orange
                'high': '#ff6600',     # Rouge-orange
                'critical': '#ff0000', # Rouge
            }
            
            color = color_map.get(notification.alert.severity, '#36a64f')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': notification.alert.title,
                    'text': notification.message,
                    'fields': [
                        {
                            'title': 'Sévérité',
                            'value': notification.alert.get_severity_display(),
                            'short': True
                        },
                        {
                            'title': 'Type',
                            'value': notification.alert.alert_rule.get_alert_type_display(),
                            'short': True
                        },
                        {
                            'title': 'Valeur actuelle',
                            'value': str(notification.alert.current_value),
                            'short': True
                        },
                        {
                            'title': 'Seuil',
                            'value': str(notification.alert.threshold_value),
                            'short': True
                        }
                    ],
                    'footer': 'Admin API Alert System',
                    'ts': int(notification.alert.triggered_at.timestamp())
                }]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = f'HTTP {response.status_code}'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
    
    def _send_teams_notification(self, notification):
        """Envoie une notification par Microsoft Teams"""
        try:
            import requests
            
            webhook_url = notification.recipient
            
            # Couleur selon la sévérité
            color_map = {
                'low': '00ff00',       # Vert
                'medium': 'ffaa00',    # Orange
                'high': 'ff6600',      # Rouge-orange
                'critical': 'ff0000',  # Rouge
            }
            
            color = color_map.get(notification.alert.severity, '00ff00')
            
            payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': color,
                'summary': notification.alert.title,
                'sections': [{
                    'activityTitle': notification.alert.title,
                    'activitySubtitle': f"Sévérité: {notification.alert.get_severity_display()}",
                    'activityImage': 'https://via.placeholder.com/64x64/ff0000/ffffff?text=!',
                    'facts': [
                        {
                            'name': 'Type d\'alerte',
                            'value': notification.alert.alert_rule.get_alert_type_display()
                        },
                        {
                            'name': 'Valeur actuelle',
                            'value': str(notification.alert.current_value)
                        },
                        {
                            'name': 'Seuil',
                            'value': str(notification.alert.threshold_value)
                        },
                        {
                            'name': 'Déclenchée à',
                            'value': notification.alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    ],
                    'markdown': True
                }],
                'text': notification.message
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = f'HTTP {response.status_code}'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
    
    def _send_discord_notification(self, notification):
        """Envoie une notification par Discord"""
        try:
            import requests
            
            webhook_url = notification.recipient
            
            # Couleur selon la sévérité
            color_map = {
                'low': 0x36a64f,       # Vert
                'medium': 0xffaa00,    # Orange
                'high': 0xff6600,      # Rouge-orange
                'critical': 0xff0000,  # Rouge
            }
            
            color = color_map.get(notification.alert.severity, 0x36a64f)
            
            payload = {
                'embeds': [{
                    'title': notification.alert.title,
                    'description': notification.message,
                    'color': color,
                    'fields': [
                        {
                            'name': 'Sévérité',
                            'value': notification.alert.get_severity_display(),
                            'inline': True
                        },
                        {
                            'name': 'Type',
                            'value': notification.alert.alert_rule.get_alert_type_display(),
                            'inline': True
                        },
                        {
                            'name': 'Valeur actuelle',
                            'value': str(notification.alert.current_value),
                            'inline': True
                        },
                        {
                            'name': 'Seuil',
                            'value': str(notification.alert.threshold_value),
                            'inline': True
                        }
                    ],
                    'footer': {
                        'text': 'Admin API Alert System'
                    },
                    'timestamp': notification.alert.triggered_at.isoformat()
                }]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                return True
            else:
                notification.status = 'failed'
                notification.error_message = f'HTTP {response.status_code}'
                notification.save()
                return False
                
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            return False
