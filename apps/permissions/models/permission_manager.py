"""
Modèle pour les gestionnaires de permissions
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class PermissionManager(models.Model):
    """
    Modèle pour les gestionnaires de permissions
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='permission_manager_profile',
        verbose_name="Utilisateur"
    )
    
    # Droits de gestion des permissions
    can_create_permissions = models.BooleanField(
        default=False,
        verbose_name="Peut créer des permissions"
    )
    can_modify_permissions = models.BooleanField(
        default=False,
        verbose_name="Peut modifier des permissions"
    )
    can_delete_permissions = models.BooleanField(
        default=False,
        verbose_name="Peut supprimer des permissions"
    )
    
    # Droits de gestion des rôles
    can_create_roles = models.BooleanField(
        default=False,
        verbose_name="Peut créer des rôles"
    )
    can_modify_roles = models.BooleanField(
        default=False,
        verbose_name="Peut modifier des rôles"
    )
    can_delete_roles = models.BooleanField(
        default=False,
        verbose_name="Peut supprimer des rôles"
    )
    can_assign_roles = models.BooleanField(
        default=False,
        verbose_name="Peut assigner des rôles"
    )
    
    # Droits de gestion des groupes
    can_create_groups = models.BooleanField(
        default=False,
        verbose_name="Peut créer des groupes"
    )
    can_modify_groups = models.BooleanField(
        default=False,
        verbose_name="Peut modifier des groupes"
    )
    can_delete_groups = models.BooleanField(
        default=False,
        verbose_name="Peut supprimer des groupes"
    )
    can_manage_groups = models.BooleanField(
        default=False,
        verbose_name="Peut gérer les groupes"
    )
    
    # Droits de délégation
    can_delegate_permissions = models.BooleanField(
        default=False,
        verbose_name="Peut déléguer des permissions"
    )
    can_delegate_roles = models.BooleanField(
        default=False,
        verbose_name="Peut déléguer des rôles"
    )
    
    # Contraintes
    max_delegation_duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée maximale de délégation (jours)"
    )
    max_delegation_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre maximum d'utilisations de délégation"
    )
    
    # Restrictions d'étendue
    allowed_apps = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Applications autorisées"
    )
    allowed_models = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Modèles autorisés"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Métadonnées
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_permission_managers',
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
        verbose_name = "Gestionnaire de permissions"
        verbose_name_plural = "Gestionnaires de permissions"
        db_table = 'permissions_permission_manager'
        ordering = ['user']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Gestionnaire de permissions - {self.user.username}"
    
    def can_manage_permission(self, permission):
        """
        Vérifie si le gestionnaire peut gérer une permission
        """
        if not self.is_active:
            return False
        
        # Vérifier les restrictions d'étendue
        if self.allowed_apps and permission.app_label not in self.allowed_apps:
            return False
        
        if self.allowed_models and permission.model not in self.allowed_models:
            return False
        
        return True
    
    def can_manage_role(self, role):
        """
        Vérifie si le gestionnaire peut gérer un rôle
        """
        if not self.is_active:
            return False
        
        # Vérifier si c'est un rôle système
        if role.is_system:
            return False
        
        return True
    
    def can_manage_group(self, group):
        """
        Vérifie si le gestionnaire peut gérer un groupe
        """
        if not self.is_active:
            return False
        
        return True
    
    def can_delegate_to_user(self, target_user):
        """
        Vérifie si le gestionnaire peut déléguer à un utilisateur
        """
        if not self.is_active:
            return False
        
        # Vérifier si l'utilisateur cible n'est pas un superutilisateur
        if target_user.is_superuser:
            return False
        
        return True
    
    def get_delegation_constraints(self):
        """
        Retourne les contraintes de délégation
        """
        return {
            'max_duration_days': self.max_delegation_duration_days,
            'max_uses': self.max_delegation_uses,
            'allowed_apps': self.allowed_apps,
            'allowed_models': self.allowed_models
        }
    
    def get_permissions_summary(self):
        """
        Retourne un résumé des permissions du gestionnaire
        """
        return {
            'permissions': {
                'create': self.can_create_permissions,
                'modify': self.can_modify_permissions,
                'delete': self.can_delete_permissions
            },
            'roles': {
                'create': self.can_create_roles,
                'modify': self.can_modify_roles,
                'delete': self.can_delete_roles,
                'assign': self.can_assign_roles
            },
            'groups': {
                'create': self.can_create_groups,
                'modify': self.can_modify_groups,
                'delete': self.can_delete_groups,
                'manage': self.can_manage_groups
            },
            'delegation': {
                'permissions': self.can_delegate_permissions,
                'roles': self.can_delegate_roles
            }
        }
    
    @classmethod
    def create_manager(cls, user, permissions=None, assigned_by=None):
        """
        Crée un gestionnaire de permissions
        """
        permissions = permissions or {}
        
        return cls.objects.create(
            user=user,
            can_create_permissions=permissions.get('can_create_permissions', False),
            can_modify_permissions=permissions.get('can_modify_permissions', False),
            can_delete_permissions=permissions.get('can_delete_permissions', False),
            can_create_roles=permissions.get('can_create_roles', False),
            can_modify_roles=permissions.get('can_modify_roles', False),
            can_delete_roles=permissions.get('can_delete_roles', False),
            can_assign_roles=permissions.get('can_assign_roles', False),
            can_create_groups=permissions.get('can_create_groups', False),
            can_modify_groups=permissions.get('can_modify_groups', False),
            can_delete_groups=permissions.get('can_delete_groups', False),
            can_manage_groups=permissions.get('can_manage_groups', False),
            can_delegate_permissions=permissions.get('can_delegate_permissions', False),
            can_delegate_roles=permissions.get('can_delegate_roles', False),
            max_delegation_duration_days=permissions.get('max_delegation_duration_days'),
            max_delegation_uses=permissions.get('max_delegation_uses'),
            allowed_apps=permissions.get('allowed_apps', []),
            allowed_models=permissions.get('allowed_models', []),
            assigned_by=assigned_by
        )
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Récupère ou crée un profil de gestionnaire pour un utilisateur
        """
        manager, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'is_active': False  # Par défaut, pas de droits
            }
        )
        return manager
