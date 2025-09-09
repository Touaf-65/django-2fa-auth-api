"""
Signaux pour l'app Internationalization
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.internationalization.models import Language, Translation, TranslationKey


@receiver(post_save, sender=Language)
def language_post_save(sender, instance, created, **kwargs):
    """
    Signal post-save pour Language
    """
    if created:
        # Initialiser les statistiques pour une nouvelle langue
        instance.translation_count = 0
        instance.save(update_fields=['translation_count'])


@receiver(post_save, sender=Translation)
def translation_post_save(sender, instance, created, **kwargs):
    """
    Signal post-save pour Translation
    """
    if created:
        # Mettre à jour les statistiques de la langue
        instance.language.translation_count += 1
        instance.language.last_used = timezone.now()
        instance.language.save(update_fields=['translation_count', 'last_used'])


@receiver(post_save, sender=TranslationKey)
def translation_key_post_save(sender, instance, created, **kwargs):
    """
    Signal post-save pour TranslationKey
    """
    if created:
        # Initialiser les statistiques pour une nouvelle clé
        instance.usage_count = 0
        instance.save(update_fields=['usage_count'])

