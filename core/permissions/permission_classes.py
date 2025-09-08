"""
Classes de permissions pour l'application Core
"""
from rest_framework import permissions
from .base_permissions import (
    IsOwnerOrReadOnly,
    IsOwnerOrAdmin,
    IsAdminOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsStaffOrReadOnly,
    IsSuperuserOrReadOnly,
)
from .custom_permissions import (
    CanViewOwnData,
    CanEditOwnData,
    CanDeleteOwnData,
    CanViewUserData,
    CanEditUserData,
    CanDeleteUserData,
    CanManageUsers,
    CanManagePermissions,
    CanManageRoles,
    CanManageGroups,
    CanViewAuditLogs,
    CanManageSystemSettings,
    CanAccessAdminPanel,
    CanViewReports,
    CanExportData,
    CanImportData,
    CanManageNotifications,
    CanManageSecurity,
    CanViewAnalytics,
    CanManageIntegrations,
)


class CorePermission(permissions.BasePermission):
    """Permission de base pour l'application Core"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class AuthenticationPermission(permissions.BasePermission):
    """Permission pour l'authentification"""
    
    def has_permission(self, request, view):
        # Les endpoints d'authentification sont publics
        if view.action in ['login', 'register', 'refresh', 'verify_email', 'reset_password']:
            return True
        
        # Les autres endpoints nécessitent une authentification
        return request.user.is_authenticated


class UserPermission(permissions.BasePermission):
    """Permission pour la gestion des utilisateurs"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture pour les propriétaires, staff ou superutilisateurs
        return (
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.has_perm('users.change_user')
        )
    
    def has_object_permission(self, request, view, obj):
        # Lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture pour les propriétaires, staff ou superutilisateurs
        return (
            obj == request.user or
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.has_perm('users.change_user')
        )


class NotificationPermission(permissions.BasePermission):
    """Permission pour la gestion des notifications"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture pour les propriétaires, staff ou superutilisateurs
        return (
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.has_perm('notifications.change_notification')
        )
    
    def has_object_permission(self, request, view, obj):
        # Lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture pour les propriétaires, staff ou superutilisateurs
        return (
            obj.user == request.user or
            request.user.is_staff or 
            request.user.is_superuser or
            request.user.has_perm('notifications.change_notification')
        )


class SecurityPermission(permissions.BasePermission):
    """Permission pour la gestion de la sécurité"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('security.view_security')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('security.manage_security')
        )


class PermissionPermission(permissions.BasePermission):
    """Permission pour la gestion des permissions"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('permissions.view_permission')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('permissions.manage_permissions')
        )


class RolePermission(permissions.BasePermission):
    """Permission pour la gestion des rôles"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('permissions.view_role')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('permissions.manage_roles')
        )


class GroupPermission(permissions.BasePermission):
    """Permission pour la gestion des groupes"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('permissions.view_group')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('permissions.manage_groups')
        )


class AuditPermission(permissions.BasePermission):
    """Permission pour la gestion des audits"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('security.view_audit_logs')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('security.manage_audit_logs')
        )


class SystemPermission(permissions.BasePermission):
    """Permission pour la gestion du système"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('core.view_system')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('core.manage_system')
        )


class ReportPermission(permissions.BasePermission):
    """Permission pour la gestion des rapports"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('core.view_reports')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('core.manage_reports')
        )


class IntegrationPermission(permissions.BasePermission):
    """Permission pour la gestion des intégrations"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecture pour les staff et superutilisateurs
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.is_staff or 
                request.user.is_superuser or
                request.user.has_perm('core.view_integrations')
            )
        
        # Écriture pour les superutilisateurs uniquement
        return (
            request.user.is_superuser or
            request.user.has_perm('core.manage_integrations')
        )

