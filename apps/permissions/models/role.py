"""
Modèle pour les rôles
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Role(models.Model):
    """
    Modèle pour les rôles avec permissions
    """
    # Informations de base
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du rôle"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    
    # Permissions
    permissions = models.ManyToManyField(
        'Permission',
        through='RolePermission',
        related_name='roles',
        verbose_name="Permissions"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Rôle système"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_roles',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        db_table = 'permissions_role'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_system']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_role(cls, name, description, permissions=None, created_by=None, is_system=False):
        """
        Crée un nouveau rôle
        """
        role = cls.objects.create(
            name=name,
            description=description,
            created_by=created_by,
            is_system=is_system
        )
        
        if permissions:
            for permission in permissions:
                RolePermission.objects.create(
                    role=role,
                    permission=permission,
                    granted=True
                )
        
        return role
    
    def add_permission(self, permission, granted=True):
        """
        Ajoute une permission au rôle
        """
        role_permission, created = RolePermission.objects.get_or_create(
            role=self,
            permission=permission,
            defaults={'granted': granted}
        )
        
        if not created:
            role_permission.granted = granted
            role_permission.save(update_fields=['granted'])
        
        return role_permission
    
    def remove_permission(self, permission):
        """
        Supprime une permission du rôle
        """
        RolePermission.objects.filter(
            role=self,
            permission=permission
        ).delete()
    
    def has_permission(self, permission):
        """
        Vérifie si le rôle a une permission
        """
        try:
            role_permission = RolePermission.objects.get(
                role=self,
                permission=permission
            )
            return role_permission.granted
        except RolePermission.DoesNotExist:
            return False
    
    def get_permissions(self):
        """
        Récupère toutes les permissions du rôle
        """
        return self.permissions.filter(
            rolepermission__granted=True
        )
    
    def get_permission_count(self):
        """
        Retourne le nombre de permissions du rôle
        """
        return self.permissions.filter(
            rolepermission__granted=True
        ).count()


class RolePermission(models.Model):
    """
    Table de liaison entre les rôles et les permissions
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Rôle"
    )
    permission = models.ForeignKey(
        'Permission',
        on_delete=models.CASCADE,
        verbose_name="Permission"
    )
    
    # Accord ou refus de la permission
    granted = models.BooleanField(
        default=True,
        verbose_name="Accordé"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Permission de rôle"
        verbose_name_plural = "Permissions de rôle"
        db_table = 'permissions_role_permission'
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission']
        indexes = [
            models.Index(fields=['role', 'granted']),
            models.Index(fields=['permission', 'granted']),
        ]
    
    def __str__(self):
        status = "Accordé" if self.granted else "Refusé"
        return f"{self.role.name} - {self.permission.name} ({status})"

