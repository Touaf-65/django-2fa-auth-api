"""
Permissions personnalisées pour l'application Core
"""
from rest_framework import permissions


class CanViewOwnData(permissions.BasePermission):
    """Permission pour voir ses propres données"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user or obj.created_by == request.user


class CanEditOwnData(permissions.BasePermission):
    """Permission pour modifier ses propres données"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user or obj.created_by == request.user


class CanDeleteOwnData(permissions.BasePermission):
    """Permission pour supprimer ses propres données"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user or obj.created_by == request.user


class CanViewUserData(permissions.BasePermission):
    """Permission pour voir les données des utilisateurs"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('users.view_user')
        )


class CanEditUserData(permissions.BasePermission):
    """Permission pour modifier les données des utilisateurs"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('users.change_user')
        )


class CanDeleteUserData(permissions.BasePermission):
    """Permission pour supprimer les données des utilisateurs"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('users.delete_user')
        )


class CanManageUsers(permissions.BasePermission):
    """Permission pour gérer les utilisateurs"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('users.manage_users')
        )


class CanManagePermissions(permissions.BasePermission):
    """Permission pour gérer les permissions"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('permissions.manage_permissions')
        )


class CanManageRoles(permissions.BasePermission):
    """Permission pour gérer les rôles"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('permissions.manage_roles')
        )


class CanManageGroups(permissions.BasePermission):
    """Permission pour gérer les groupes"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('permissions.manage_groups')
        )


class CanViewAuditLogs(permissions.BasePermission):
    """Permission pour voir les logs d'audit"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('security.view_audit_logs')
        )


class CanManageSystemSettings(permissions.BasePermission):
    """Permission pour gérer les paramètres système"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('core.manage_system_settings')
        )


class CanAccessAdminPanel(permissions.BasePermission):
    """Permission pour accéder au panneau d'administration"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('core.access_admin_panel')
        )


class CanViewReports(permissions.BasePermission):
    """Permission pour voir les rapports"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('core.view_reports')
        )


class CanExportData(permissions.BasePermission):
    """Permission pour exporter les données"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('core.export_data')
        )


class CanImportData(permissions.BasePermission):
    """Permission pour importer les données"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('core.import_data')
        )


class CanManageNotifications(permissions.BasePermission):
    """Permission pour gérer les notifications"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('notifications.manage_notifications')
        )


class CanManageSecurity(permissions.BasePermission):
    """Permission pour gérer la sécurité"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('security.manage_security')
        )


class CanViewAnalytics(permissions.BasePermission):
    """Permission pour voir les analytics"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.has_perm('core.view_analytics')
        )


class CanManageIntegrations(permissions.BasePermission):
    """Permission pour gérer les intégrations"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.has_perm('core.manage_integrations')
        )

