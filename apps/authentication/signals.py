"""
Signaux pour l'app authentication
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import TwoFactorAuth, UserSession

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil utilisateur lors de la création d'un utilisateur"""
    if created:
        # Créer un profil utilisateur basique
        from apps.users.models import UserProfile
        UserProfile.objects.create(user=instance)
        
        # Envoyer un email de bienvenue
        try:
            from apps.notifications.services.template_email_service import TemplateEmailService
            email_service = TemplateEmailService()
            email_service.send_welcome_email(instance)
        except Exception as e:
            # Log l'erreur mais ne pas faire échouer la création de l'utilisateur
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")


@receiver(post_save, sender=User)
def create_two_factor_auth(sender, instance, created, **kwargs):
    """Crée automatiquement une configuration 2FA lors de la création d'un utilisateur"""
    if created:
        TwoFactorAuth.objects.create(user=instance)


@receiver(pre_save, sender=User)
def hash_password(sender, instance, **kwargs):
    """Hash le mot de passe avant de sauvegarder l'utilisateur"""
    if instance.pk is None:  # Nouvel utilisateur
        instance.set_password(instance.password)
    else:  # Utilisateur existant
        # Vérifier si le mot de passe a changé
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.password != instance.password:
                instance.set_password(instance.password)
        except User.DoesNotExist:
            pass
