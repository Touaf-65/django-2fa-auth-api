"""
Modèles pour les relations entre utilisateurs
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class UserFollow(models.Model):
    """
    Modèle pour les relations de suivi entre utilisateurs
    """
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Utilisateur qui suit"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name="Utilisateur suivi"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de suivi"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Suivi actif"
    )
    
    class Meta:
        verbose_name = "Suivi d'utilisateur"
        verbose_name_plural = "Suivis d'utilisateurs"
        db_table = 'users_user_follow'
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'is_active']),
            models.Index(fields=['following', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.follower.email} suit {self.following.email}"
    
    def clean(self):
        """Validation : un utilisateur ne peut pas se suivre lui-même"""
        from django.core.exceptions import ValidationError
        if self.follower == self.following:
            raise ValidationError("Un utilisateur ne peut pas se suivre lui-même.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def follow_user(cls, follower, following):
        """Crée une relation de suivi"""
        follow, created = cls.objects.get_or_create(
            follower=follower,
            following=following,
            defaults={'is_active': True}
        )
        if not created and not follow.is_active:
            follow.is_active = True
            follow.save()
        return follow
    
    @classmethod
    def unfollow_user(cls, follower, following):
        """Supprime une relation de suivi"""
        try:
            follow = cls.objects.get(follower=follower, following=following)
            follow.is_active = False
            follow.save()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def get_followers_count(cls, user):
        """Retourne le nombre d'abonnés d'un utilisateur"""
        return cls.objects.filter(following=user, is_active=True).count()
    
    @classmethod
    def get_following_count(cls, user):
        """Retourne le nombre d'utilisateurs suivis par un utilisateur"""
        return cls.objects.filter(follower=user, is_active=True).count()
    
    @classmethod
    def is_following(cls, follower, following):
        """Vérifie si un utilisateur suit un autre"""
        return cls.objects.filter(
            follower=follower,
            following=following,
            is_active=True
        ).exists()


class UserBlock(models.Model):
    """
    Modèle pour bloquer des utilisateurs
    """
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_users',
        verbose_name="Utilisateur qui bloque"
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by',
        verbose_name="Utilisateur bloqué"
    )
    
    # Raison du blocage
    reason = models.CharField(
        max_length=100,
        choices=[
            ('spam', 'Spam'),
            ('harassment', 'Harcèlement'),
            ('inappropriate_content', 'Contenu inapproprié'),
            ('fake_account', 'Compte factice'),
            ('other', 'Autre'),
        ],
        default='other',
        verbose_name="Raison du blocage"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (optionnelle)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de blocage"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Blocage actif"
    )
    
    class Meta:
        verbose_name = "Blocage d'utilisateur"
        verbose_name_plural = "Blocages d'utilisateurs"
        db_table = 'users_user_block'
        unique_together = ['blocker', 'blocked']
        indexes = [
            models.Index(fields=['blocker', 'is_active']),
            models.Index(fields=['blocked', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.blocker.email} a bloqué {self.blocked.email}"
    
    def clean(self):
        """Validation : un utilisateur ne peut pas se bloquer lui-même"""
        from django.core.exceptions import ValidationError
        if self.blocker == self.blocked:
            raise ValidationError("Un utilisateur ne peut pas se bloquer lui-même.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def block_user(cls, blocker, blocked, reason='other', description=''):
        """Bloque un utilisateur"""
        block, created = cls.objects.get_or_create(
            blocker=blocker,
            blocked=blocked,
            defaults={
                'reason': reason,
                'description': description,
                'is_active': True
            }
        )
        if not created and not block.is_active:
            block.is_active = True
            block.reason = reason
            block.description = description
            block.save()
        
        # Supprimer automatiquement les relations de suivi
        UserFollow.unfollow_user(blocker, blocked)
        UserFollow.unfollow_user(blocked, blocker)
        
        return block
    
    @classmethod
    def unblock_user(cls, blocker, blocked):
        """Débloque un utilisateur"""
        try:
            block = cls.objects.get(blocker=blocker, blocked=blocked)
            block.is_active = False
            block.save()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def is_blocked(cls, user1, user2):
        """Vérifie si un utilisateur est bloqué par un autre"""
        return cls.objects.filter(
            models.Q(blocker=user1, blocked=user2) |
            models.Q(blocker=user2, blocked=user1),
            is_active=True
        ).exists()
    
    @classmethod
    def get_blocked_users(cls, user):
        """Retourne la liste des utilisateurs bloqués par un utilisateur"""
        return cls.objects.filter(blocker=user, is_active=True).select_related('blocked')
    
    @classmethod
    def get_blocked_by_users(cls, user):
        """Retourne la liste des utilisateurs qui ont bloqué un utilisateur"""
        return cls.objects.filter(blocked=user, is_active=True).select_related('blocker')

