"""
Signaux pour l'app security
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserSecurity, SecurityEvent, LoginAttempt

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_security_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil de sécurité lors de la création d'un utilisateur"""
    if created:
        UserSecurity.get_or_create_for_user(instance)


@receiver(post_save, sender=LoginAttempt)
def handle_failed_login_attempt(sender, instance, created, **kwargs):
    """Gère les tentatives de connexion échouées"""
    if created and instance.status in [LoginAttempt.FAILED, LoginAttempt.BLOCKED]:
        # Créer un événement de sécurité
        SecurityEvent.create_event(
            event_type=SecurityEvent.LOGIN_FAILED,
            title='Tentative de connexion échouée',
            description=f'Tentative de connexion échouée pour {instance.email} depuis {instance.ip_address}',
            ip_address=instance.ip_address,
            user=instance.user,
            severity='medium',
            user_agent=instance.user_agent,
            country=instance.country,
            city=instance.city,
            metadata={
                'email': instance.email,
                'failure_reason': instance.failure_reason,
                'attempt_count': LoginAttempt.get_failed_attempts_count(
                    instance.ip_address, instance.email, minutes=15
                )
            }
        )
        
        # Mettre à jour le profil de sécurité de l'utilisateur
        if instance.user:
            security_profile = UserSecurity.get_or_create_for_user(instance.user)
            security_profile.record_failed_login(instance.ip_address, instance.user_agent)


@receiver(post_save, sender=LoginAttempt)
def handle_successful_login_attempt(sender, instance, created, **kwargs):
    """Gère les tentatives de connexion réussies"""
    if created and instance.status == LoginAttempt.SUCCESS:
        # Créer un événement de sécurité
        SecurityEvent.create_event(
            event_type=SecurityEvent.LOGIN_SUCCESS,
            title='Connexion réussie',
            description=f'Connexion réussie pour {instance.email} depuis {instance.ip_address}',
            ip_address=instance.ip_address,
            user=instance.user,
            severity='low',
            user_agent=instance.user_agent,
            country=instance.country,
            city=instance.city,
            metadata={
                'email': instance.email,
                'login_time': instance.created_at.isoformat()
            }
        )
        
        # Mettre à jour le profil de sécurité de l'utilisateur
        if instance.user:
            security_profile = UserSecurity.get_or_create_for_user(instance.user)
            security_profile.record_successful_login(
                instance.ip_address,
                instance.country,
                instance.city,
                instance.user_agent
            )

