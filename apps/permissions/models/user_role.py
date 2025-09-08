"""
Modèle pour les rôles directs des utilisateurs
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserRole(models.Model):
    """
    Modèle pour les rôles directs des utilisateurs
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="Utilisateur"
    )
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="Rôle"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Contraintes temporelles
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration"
    )
    
    # Métadonnées
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_user_roles',
        verbose_name="Assigné par"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'assignation"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Rôle utilisateur"
        verbose_name_plural = "Rôles utilisateur"
        db_table = 'permissions_user_role'
        unique_together = ['user', 'role']
        ordering = ['user', 'role']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        status = "Actif" if self.is_active else "Inactif"
        return f"{self.user.username} - {self.role.name} ({status})"
    
    def is_expired(self):
        """
        Vérifie si le rôle est expiré
        """
        if not self.expires_at:
            return False
        
        return timezone.now() > self.expires_at
    
    def get_remaining_time(self):
        """
        Retourne le temps restant avant expiration
        """
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return remaining
    
    def extend_expiration(self, days=None, hours=None):
        """
        Prolonge l'expiration du rôle
        """
        if not self.expires_at:
            # Si pas d'expiration, créer une nouvelle date
            if days:
                self.expires_at = timezone.now() + timezone.timedelta(days=days)
            elif hours:
                self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        else:
            # Prolonger l'expiration existante
            if days:
                self.expires_at += timezone.timedelta(days=days)
            elif hours:
                self.expires_at += timezone.timedelta(hours=hours)
        
        self.save(update_fields=['expires_at'])
    
    @classmethod
    def assign_role(cls, user, role, assigned_by=None, expires_at=None):
        """
        Assigne un rôle à un utilisateur
        """
        user_role, created = cls.objects.get_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by': assigned_by,
                'expires_at': expires_at
            }
        )
        
        if not created:
            user_role.is_active = True
            user_role.assigned_by = assigned_by
            user_role.expires_at = expires_at
            user_role.save(update_fields=['is_active', 'assigned_by', 'expires_at'])
        
        return user_role
    
    @classmethod
    def revoke_role(cls, user, role):
        """
        Révoque un rôle d'un utilisateur
        """
        try:
            user_role = cls.objects.get(user=user, role=role)
            user_role.is_active = False
            user_role.save(update_fields=['is_active'])
            return user_role
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_active_roles(cls, user):
        """
        Récupère tous les rôles actifs d'un utilisateur
        """
        now = timezone.now()
        return cls.objects.filter(
            user=user,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).select_related('role')
    
    @classmethod
    def get_expired_roles(cls, user):
        """
        Récupère tous les rôles expirés d'un utilisateur
        """
        now = timezone.now()
        return cls.objects.filter(
            user=user,
            expires_at__lt=now
        ).select_related('role')

