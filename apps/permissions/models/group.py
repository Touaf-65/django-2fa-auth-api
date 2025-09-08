"""
Modèle pour les groupes d'utilisateurs
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Group(models.Model):
    """
    Modèle pour les groupes d'utilisateurs
    """
    # Informations de base
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du groupe"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    
    # Rôles et utilisateurs
    roles = models.ManyToManyField(
        'Role',
        through='GroupRole',
        related_name='groups',
        verbose_name="Rôles"
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        through_fields=('group', 'user'),
        related_name='permission_groups',
        verbose_name="Utilisateurs"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_groups',
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
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        db_table = 'permissions_group'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_group(cls, name, description, roles=None, created_by=None):
        """
        Crée un nouveau groupe
        """
        group = cls.objects.create(
            name=name,
            description=description,
            created_by=created_by
        )
        
        if roles:
            for role in roles:
                GroupRole.objects.create(
                    group=group,
                    role=role,
                    assigned_by=created_by
                )
        
        return group
    
    def add_role(self, role, assigned_by=None):
        """
        Ajoute un rôle au groupe
        """
        group_role, created = GroupRole.objects.get_or_create(
            group=self,
            role=role,
            defaults={'assigned_by': assigned_by}
        )
        return group_role
    
    def remove_role(self, role):
        """
        Supprime un rôle du groupe
        """
        GroupRole.objects.filter(
            group=self,
            role=role
        ).delete()
    
    def add_user(self, user, joined_by=None):
        """
        Ajoute un utilisateur au groupe
        """
        membership, created = GroupMembership.objects.get_or_create(
            group=self,
            user=user,
            defaults={'joined_by': joined_by}
        )
        return membership
    
    def remove_user(self, user):
        """
        Supprime un utilisateur du groupe
        """
        GroupMembership.objects.filter(
            group=self,
            user=user
        ).delete()
    
    def get_roles(self):
        """
        Récupère tous les rôles du groupe
        """
        return self.roles.all()
    
    def get_users(self):
        """
        Récupère tous les utilisateurs actifs du groupe
        """
        return self.users.filter(
            groupmembership__is_active=True
        )
    
    def get_user_count(self):
        """
        Retourne le nombre d'utilisateurs actifs du groupe
        """
        return self.users.filter(
            groupmembership__is_active=True
        ).count()
    
    def get_permissions(self):
        """
        Récupère toutes les permissions du groupe (via ses rôles)
        """
        from .permission import Permission
        
        role_permissions = RolePermission.objects.filter(
            role__groups=self,
            granted=True
        ).select_related('permission')
        
        return Permission.objects.filter(
            rolepermission__in=role_permissions
        ).distinct()


class GroupRole(models.Model):
    """
    Table de liaison entre les groupes et les rôles
    """
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="Groupe"
    )
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        verbose_name="Rôle"
    )
    
    # Métadonnées
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_group_roles',
        verbose_name="Assigné par"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'assignation"
    )
    
    class Meta:
        verbose_name = "Rôle de groupe"
        verbose_name_plural = "Rôles de groupe"
        db_table = 'permissions_group_role'
        unique_together = ['group', 'role']
        ordering = ['group', 'role']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.group.name} - {self.role.name}"


class GroupMembership(models.Model):
    """
    Table de liaison entre les groupes et les utilisateurs
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="Groupe"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Métadonnées
    joined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_group_members',
        verbose_name="Ajouté par"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'adhésion"
    )
    
    class Meta:
        verbose_name = "Adhésion au groupe"
        verbose_name_plural = "Adhésions aux groupes"
        db_table = 'permissions_group_membership'
        unique_together = ['user', 'group']
        ordering = ['group', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['group', 'is_active']),
        ]
    
    def __str__(self):
        status = "Actif" if self.is_active else "Inactif"
        return f"{self.user.username} - {self.group.name} ({status})"
