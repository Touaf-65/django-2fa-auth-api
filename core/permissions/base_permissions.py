"""
Permissions de base pour l'application Core
"""
from rest_framework import permissions


class BasePermission(permissions.BasePermission):
    """Permission de base avec fonctionnalités communes"""
    
    def has_permission(self, request, view):
        """Vérifie les permissions au niveau de la vue"""
        return True
    
    def has_object_permission(self, request, view, obj):
        """Vérifie les permissions au niveau de l'objet"""
        return True


class IsOwnerOrReadOnly(BasePermission):
    """Permission pour les propriétaires ou lecture seule"""
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour le propriétaire
        return obj.created_by == request.user


class IsOwnerOrAdmin(BasePermission):
    """Permission pour les propriétaires ou administrateurs"""
    
    def has_object_permission(self, request, view, obj):
        # Administrateurs ont tous les droits
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsAdminOrReadOnly(BasePermission):
    """Permission pour les administrateurs ou lecture seule"""
    
    def has_permission(self, request, view):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour les administrateurs
        return request.user.is_staff or request.user.is_superuser


class IsAuthenticatedOrReadOnly(BasePermission):
    """Permission pour les utilisateurs authentifiés ou lecture seule"""
    
    def has_permission(self, request, view):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour les utilisateurs authentifiés
        return request.user.is_authenticated


class IsStaffOrReadOnly(BasePermission):
    """Permission pour le staff ou lecture seule"""
    
    def has_permission(self, request, view):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour le staff
        return request.user.is_staff


class IsSuperuserOrReadOnly(BasePermission):
    """Permission pour les superutilisateurs ou lecture seule"""
    
    def has_permission(self, request, view):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour les superutilisateurs
        return request.user.is_superuser


class IsOwnerOrStaff(BasePermission):
    """Permission pour les propriétaires ou le staff"""
    
    def has_object_permission(self, request, view, obj):
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrAdminOrReadOnly(BasePermission):
    """Permission pour les propriétaires, administrateurs ou lecture seule"""
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Administrateurs ont tous les droits
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrStaffOrReadOnly(BasePermission):
    """Permission pour les propriétaires, staff ou lecture seule"""
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrSuperuser(BasePermission):
    """Permission pour les propriétaires ou superutilisateurs"""
    
    def has_object_permission(self, request, view, obj):
        # Superutilisateurs ont tous les droits
        if request.user.is_superuser:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrStaffOrSuperuser(BasePermission):
    """Permission pour les propriétaires, staff ou superutilisateurs"""
    
    def has_object_permission(self, request, view, obj):
        # Superutilisateurs ont tous les droits
        if request.user.is_superuser:
            return True
        
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrAdminOrStaff(BasePermission):
    """Permission pour les propriétaires, administrateurs ou staff"""
    
    def has_object_permission(self, request, view, obj):
        # Superutilisateurs ont tous les droits
        if request.user.is_superuser:
            return True
        
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrAdminOrStaffOrReadOnly(BasePermission):
    """Permission pour les propriétaires, administrateurs, staff ou lecture seule"""
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superutilisateurs ont tous les droits
        if request.user.is_superuser:
            return True
        
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user


class IsOwnerOrAdminOrStaffOrSuperuser(BasePermission):
    """Permission pour les propriétaires, administrateurs, staff ou superutilisateurs"""
    
    def has_object_permission(self, request, view, obj):
        # Superutilisateurs ont tous les droits
        if request.user.is_superuser:
            return True
        
        # Staff a tous les droits
        if request.user.is_staff:
            return True
        
        # Propriétaires ont tous les droits
        return obj.created_by == request.user

