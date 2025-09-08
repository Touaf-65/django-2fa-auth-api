"""
Tests pour les permissions
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from core.permissions.base_permissions import (
    IsOwnerOrReadOnly,
    IsOwnerOrAdmin,
    IsAdminOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsStaffOrReadOnly,
    IsSuperuserOrReadOnly,
)
from core.permissions.custom_permissions import (
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

User = get_user_model()


class BasePermissionsTest(TestCase):
    """Tests pour les permissions de base"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.superuser = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_superuser=True
        )
        
        # Crée un objet de test
        class TestObject:
            def __init__(self, created_by):
                self.created_by = created_by
        
        self.test_object = TestObject(self.user)
    
    def test_is_owner_or_read_only(self):
        """Test de IsOwnerOrReadOnly"""
        permission = IsOwnerOrReadOnly()
        
        # Test de lecture (GET)
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(permission.has_object_permission(request, None, self.test_object))
        
        # Test d'écriture par le propriétaire (POST)
        request = self.factory.post('/')
        request.user = self.user
        self.assertTrue(permission.has_object_permission(request, None, self.test_object))
        
        # Test d'écriture par un autre utilisateur (POST)
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        request.user = other_user
        self.assertFalse(permission.has_object_permission(request, None, self.test_object))
    
    def test_is_owner_or_admin(self):
        """Test de IsOwnerOrAdmin"""
        permission = IsOwnerOrAdmin()
        
        # Test par le propriétaire
        request = self.factory.post('/')
        request.user = self.user
        self.assertTrue(permission.has_object_permission(request, None, self.test_object))
        
        # Test par un administrateur
        request.user = self.staff_user
        self.assertTrue(permission.has_object_permission(request, None, self.test_object))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_object_permission(request, None, self.test_object))
        
        # Test par un utilisateur normal
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        request.user = other_user
        self.assertFalse(permission.has_object_permission(request, None, self.test_object))
    
    def test_is_admin_or_read_only(self):
        """Test de IsAdminOrReadOnly"""
        permission = IsAdminOrReadOnly()
        
        # Test de lecture par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'écriture par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test d'écriture par un administrateur
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'écriture par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_is_authenticated_or_read_only(self):
        """Test de IsAuthenticatedOrReadOnly"""
        permission = IsAuthenticatedOrReadOnly()
        
        # Test de lecture par un utilisateur non authentifié
        request = self.factory.get('/')
        request.user = None
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'écriture par un utilisateur non authentifié
        request = self.factory.post('/')
        request.user = None
        self.assertFalse(permission.has_permission(request, None))
        
        # Test d'écriture par un utilisateur authentifié
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
    
    def test_is_staff_or_read_only(self):
        """Test de IsStaffOrReadOnly"""
        permission = IsStaffOrReadOnly()
        
        # Test de lecture par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'écriture par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test d'écriture par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
    
    def test_is_superuser_or_read_only(self):
        """Test de IsSuperuserOrReadOnly"""
        permission = IsSuperuserOrReadOnly()
        
        # Test de lecture par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'écriture par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test d'écriture par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test d'écriture par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))


class CustomPermissionsTest(TestCase):
    """Tests pour les permissions personnalisées"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.superuser = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_superuser=True
        )
    
    def test_can_view_own_data(self):
        """Test de CanViewOwnData"""
        permission = CanViewOwnData()
        
        # Test par un utilisateur non authentifié
        request = self.factory.get('/')
        request.user = None
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un utilisateur authentifié
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test d'accès à ses propres données
        self.assertTrue(permission.has_object_permission(request, None, self.user))
        
        # Test d'accès aux données d'un autre utilisateur
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        self.assertFalse(permission.has_object_permission(request, None, other_user))
    
    def test_can_edit_own_data(self):
        """Test de CanEditOwnData"""
        permission = CanEditOwnData()
        
        # Test par un utilisateur non authentifié
        request = self.factory.post('/')
        request.user = None
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un utilisateur authentifié
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test de modification de ses propres données
        self.assertTrue(permission.has_object_permission(request, None, self.user))
        
        # Test de modification des données d'un autre utilisateur
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        self.assertFalse(permission.has_object_permission(request, None, other_user))
    
    def test_can_delete_own_data(self):
        """Test de CanDeleteOwnData"""
        permission = CanDeleteOwnData()
        
        # Test par un utilisateur non authentifié
        request = self.factory.delete('/')
        request.user = None
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un utilisateur authentifié
        request.user = self.user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test de suppression de ses propres données
        self.assertTrue(permission.has_object_permission(request, None, self.user))
        
        # Test de suppression des données d'un autre utilisateur
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )
        self.assertFalse(permission.has_object_permission(request, None, other_user))
    
    def test_can_manage_users(self):
        """Test de CanManageUsers"""
        permission = CanManageUsers()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_permissions(self):
        """Test de CanManagePermissions"""
        permission = CanManagePermissions()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_roles(self):
        """Test de CanManageRoles"""
        permission = CanManageRoles()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_groups(self):
        """Test de CanManageGroups"""
        permission = CanManageGroups()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_view_audit_logs(self):
        """Test de CanViewAuditLogs"""
        permission = CanViewAuditLogs()
        
        # Test par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_system_settings(self):
        """Test de CanManageSystemSettings"""
        permission = CanManageSystemSettings()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_access_admin_panel(self):
        """Test de CanAccessAdminPanel"""
        permission = CanAccessAdminPanel()
        
        # Test par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_view_reports(self):
        """Test de CanViewReports"""
        permission = CanViewReports()
        
        # Test par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_export_data(self):
        """Test de CanExportData"""
        permission = CanExportData()
        
        # Test par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_import_data(self):
        """Test de CanImportData"""
        permission = CanImportData()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_notifications(self):
        """Test de CanManageNotifications"""
        permission = CanManageNotifications()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_security(self):
        """Test de CanManageSecurity"""
        permission = CanManageSecurity()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_view_analytics(self):
        """Test de CanViewAnalytics"""
        permission = CanViewAnalytics()
        
        # Test par un utilisateur normal
        request = self.factory.get('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_integrations(self):
        """Test de CanManageIntegrations"""
        permission = CanManageIntegrations()
        
        # Test par un utilisateur normal
        request = self.factory.post('/')
        request.user = self.user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par le staff
        request.user = self.staff_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Test par un superutilisateur
        request.user = self.superuser
        self.assertTrue(permission.has_permission(request, None))



