"""
Service d'envoi d'emails avec templates
"""
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from ..models import EmailNotification, EmailTemplate

logger = logging.getLogger(__name__)


class TemplateEmailService:
    """Service pour l'envoi d'emails avec templates"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@localhost')
    
    def send_email(self, to_email, subject, message, html_message=None, template_name=None, context=None, user=None):
        """
        Envoie un email
        
        Args:
            to_email (str): Email du destinataire
            subject (str): Sujet de l'email
            message (str): Message texte
            html_message (str): Message HTML (optionnel)
            template_name (str): Nom du template (optionnel)
            context (dict): Contexte pour le template (optionnel)
        
        Returns:
            bool: True si l'envoi a réussi
        """
        try:
            # Si un template est spécifié, l'utiliser
            if template_name and context:
                html_message = self._render_template(template_name, context)
                if not message:
                    message = self._extract_text_from_html(html_message)
            
            # Créer l'enregistrement de notification
            from ..models import Notification
            notification = Notification.objects.create(
                user=user,  # Utilisateur associé
                notification_type='email',
                subject=subject,
                content=message,
                html_content=html_message or '',
                recipient_email=to_email,
                status='pending'
            )
            
            email_notification = EmailNotification.objects.create(
                notification=notification,
                to_email=to_email,
                subject=subject,
                html_content=html_message or '',
                text_content=message
            )
            
            # Envoyer l'email
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.from_email,
                    to=[to_email]
                )
                email.attach_alternative(html_message, "text/html")
                result = email.send()
            else:
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.from_email,
                    recipient_list=[to_email],
                    fail_silently=False
                )
            
            # Mettre à jour le statut
            if result:
                notification.status = 'sent'
                notification.save()
                logger.info(f"Email envoyé avec succès à {to_email}")
                return True
            else:
                notification.status = 'failed'
                notification.save()
                logger.error(f"Échec de l'envoi de l'email à {to_email}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
            if 'notification' in locals():
                notification.status = 'failed'
                notification.save()
            return False
    
    def send_template_email(self, to_email, template_name, context=None, user=None):
        """
        Envoie un email en utilisant un template
        
        Args:
            to_email (str): Email du destinataire
            template_name (str): Nom du template
            context (dict): Contexte pour le template
        
        Returns:
            bool: True si l'envoi a réussi
        """
        try:
            # Préparer le contexte
            if context is None:
                context = {}
            
            # Ajouter des variables globales
            context.update({
                'site_name': getattr(settings, 'SITE_NAME', 'Django 2FA Auth API'),
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                'current_year': 2025
            })
            
            # Rendre le template
            html_message = self._render_template(template_name, context)
            
            # Déterminer le sujet selon le template
            subject = self._get_template_subject(template_name, context)
            
            return self.send_email(
                to_email=to_email,
                subject=subject,
                message=self._extract_text_from_html(html_message),
                html_message=html_message,
                user=user
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du template '{template_name}': {str(e)}")
            return False
    
    def send_welcome_email(self, user):
        """Envoie un email de bienvenue"""
        context = {
            'user': user,
        }
        return self.send_template_email(user.email, 'welcome', context, user)
    
    def send_login_success_email(self, user, ip_address, user_agent, login_time):
        """Envoie un email de connexion réussie"""
        context = {
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'login_time': login_time,
            'location': 'Non disponible'  # TODO: Implémenter la géolocalisation
        }
        return self.send_template_email(user.email, 'login_success', context, user)
    
    def send_password_reset_email(self, user, reset_code, ip_address, expiry_minutes=30):
        """Envoie un email de réinitialisation de mot de passe"""
        from django.utils import timezone
        context = {
            'user': user,
            'reset_code': reset_code,
            'ip_address': ip_address,
            'request_time': timezone.now(),
            'expiry_time': expiry_minutes
        }
        return self.send_template_email(user.email, 'password_reset', context, user)
    
    def send_password_changed_email(self, user, ip_address, user_agent, change_time):
        """Envoie un email de changement de mot de passe"""
        context = {
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'change_time': change_time,
            'location': 'Non disponible'  # TODO: Implémenter la géolocalisation
        }
        return self.send_template_email(user.email, 'password_changed', context, user)
    
    def send_profile_updated_email(self, user, changes, ip_address, user_agent, update_time):
        """Envoie un email de mise à jour de profil"""
        context = {
            'user': user,
            'changes': changes,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'update_time': update_time
        }
        return self.send_template_email(user.email, 'profile_updated', context, user)
    
    def send_security_alert_email(self, user, alert_type, alert_description, ip_address, user_agent, alert_time, recommended_actions=None):
        """Envoie un email d'alerte de sécurité"""
        if recommended_actions is None:
            recommended_actions = [
                "Changez votre mot de passe immédiatement",
                "Révoquez toutes les sessions actives",
                "Contactez notre support si nécessaire"
            ]
        
        context = {
            'user': user,
            'alert_type': alert_type,
            'alert_description': alert_description,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'alert_time': alert_time,
            'location': 'Non disponible',  # TODO: Implémenter la géolocalisation
            'recommended_actions': recommended_actions
        }
        return self.send_template_email(user.email, 'security_alert', context, user)
    
    def send_2fa_enabled_email(self, user, backup_codes, ip_address, user_agent, activation_time):
        """Envoie un email de confirmation d'activation 2FA"""
        context = {
            'user': user,
            'backup_codes': backup_codes,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'activation_time': activation_time
        }
        return self.send_template_email(user.email, '2fa_enabled', context, user)
    
    def _render_template(self, template_name, context):
        """
        Rend un template HTML
        
        Args:
            template_name (str): Nom du template
            context (dict): Contexte pour le template
        
        Returns:
            str: HTML rendu
        """
        try:
            template_path = f'emails/{template_name}.html'
            return render_to_string(template_path, context)
        except Exception as e:
            logger.error(f"Erreur lors du rendu du template '{template_name}': {str(e)}")
            return f"<p>Erreur lors du rendu du template: {str(e)}</p>"
    
    def _get_template_subject(self, template_name, context):
        """Retourne le sujet approprié selon le template"""
        subjects = {
            'welcome': f"Bienvenue sur {context.get('site_name', 'notre plateforme')} !",
            'login_success': f"Connexion réussie - {context.get('site_name', 'notre plateforme')}",
            'password_reset': f"Réinitialisation de mot de passe - {context.get('site_name', 'notre plateforme')}",
            'password_changed': f"Mot de passe modifié - {context.get('site_name', 'notre plateforme')}",
            'profile_updated': f"Profil mis à jour - {context.get('site_name', 'notre plateforme')}",
            'security_alert': f"🚨 Alerte de sécurité - {context.get('site_name', 'notre plateforme')}",
            '2fa_enabled': f"2FA activée - {context.get('site_name', 'notre plateforme')}"
        }
        return subjects.get(template_name, f"Notification - {context.get('site_name', 'notre plateforme')}")
    
    def _extract_text_from_html(self, html_content):
        """
        Extrait le texte d'un contenu HTML
        
        Args:
            html_content (str): Contenu HTML
        
        Returns:
            str: Texte extrait
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except ImportError:
            # Si BeautifulSoup n'est pas disponible, retourner le HTML
            return html_content
        except Exception:
            return html_content
