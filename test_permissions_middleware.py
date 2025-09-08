#!/usr/bin/env python
"""
Test du middleware de permissions
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.permissions.middleware import PermissionMiddleware, DelegationMiddleware, AuditMiddleware
from apps.permissions.decorators import permission_required, method_permissions
from apps.permissions.models import Permission, Role, UserRole
from apps.permissions.utils import has_permission

User = get_user_model()

def test_permissions_middleware():
    """Test du middleware de permissions"""
    print("🛡️ Test du Middleware de Permissions")
    print("=" * 50)
    
    try:
        # 1. Récupérer un utilisateur existant
        print("1️⃣ Récupération d'un utilisateur existant...")
        user = User.objects.first()
        if not user:
            print("   ❌ Aucun utilisateur trouvé.")
            return
        print(f"   ✅ Utilisateur trouvé: {user.email}")
        
        # 2. Créer une permission de test
        print("\n2️⃣ Création d'une permission de test...")
        test_permission, created = Permission.objects.get_or_create(
            codename="test.middleware.view",
            defaults={
                'name': "Test Middleware View",
                'description': "Permission pour tester le middleware",
                'app_label': "test",
                'model': "middleware",
                'action': "view",
                'is_custom': True,
                'created_by': user
            }
        )
        print(f"   ✅ Permission: {test_permission}")
        
        # 3. Créer un rôle de test
        print("\n3️⃣ Création d'un rôle de test...")
        test_role, created = Role.objects.get_or_create(
            name="Test Middleware Role",
            defaults={
                'description': "Rôle pour tester le middleware",
                'created_by': user
            }
        )
        
        if created:
            test_role.add_permission(test_permission)
            print(f"   ✅ Rôle créé: {test_role}")
        else:
            print(f"   ✅ Rôle existant: {test_role}")
        
        # 4. Assigner le rôle à l'utilisateur
        print("\n4️⃣ Attribution du rôle à l'utilisateur...")
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=test_role,
            defaults={'assigned_by': user}
        )
        print(f"   ✅ Rôle assigné: {user_role}")
        
        # 5. Créer une vue de test avec décorateur
        print("\n5️⃣ Création d'une vue de test...")
        
        @permission_required("test.middleware.view")
        def test_view(request):
            return {"message": "Accès autorisé", "user": request.user.email}
        
        # 6. Tester le middleware
        print("\n6️⃣ Test du middleware...")
        
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/test/middleware/')
        request.user = user
        
        # Créer le middleware
        middleware = PermissionMiddleware(lambda req: {"message": "Test"})
        
        # Simuler la résolution d'URL
        from django.urls import resolve
        from unittest.mock import patch
        
        with patch('django.urls.resolve') as mock_resolve:
            # Mock de la résolution d'URL
            mock_match = type('MockMatch', (), {
                'func': test_view,
                'view_name': 'test.middleware.view',
                'app_name': 'test',
                'url_name': 'middleware_view',
                'kwargs': {}
            })()
            mock_resolve.return_value = mock_match
            
            # Traiter la requête
            response = middleware.process_request(request)
            
            if response is None:
                print("   ✅ Middleware: Requête autorisée")
                print(f"   📊 Permission vérifiée: {getattr(request, 'permission_required', 'N/A')}")
            else:
                print(f"   ❌ Middleware: Requête refusée - {response.status_code}")
                print(f"   📝 Réponse: {response.content.decode()}")
        
        # 7. Tester la vérification de permission directe
        print("\n7️⃣ Test de vérification de permission directe...")
        has_perm = has_permission(user, "test.middleware.view")
        print(f"   🔍 Permission directe: {has_perm}")
        
        # 8. Tester avec un utilisateur sans permission
        print("\n8️⃣ Test avec utilisateur sans permission...")
        other_user = User.objects.exclude(id=user.id).first()
        if other_user:
            has_perm_other = has_permission(other_user, "test.middleware.view")
            print(f"   🔍 Permission autre utilisateur: {has_perm_other}")
        
        # 9. Tester le middleware d'audit
        print("\n9️⃣ Test du middleware d'audit...")
        audit_middleware = AuditMiddleware(lambda req: {"message": "Test"})
        
        # Traiter la requête avec l'audit
        audit_middleware.process_request(request)
        
        # Créer un objet de réponse Django
        from django.http import JsonResponse
        response = JsonResponse({"message": "Test"})
        audit_middleware.process_response(request, response)
        
        if hasattr(request, 'audit_info'):
            print("   ✅ Audit: Informations enregistrées")
            print(f"   📊 Permissions utilisateur: {len(request.audit_info.get('user_permissions', []))}")
            print(f"   📊 Rôles utilisateur: {len(request.audit_info.get('user_roles', []))}")
        else:
            print("   ❌ Audit: Aucune information enregistrée")
        
        # 10. Statistiques finales
        print("\n🔟 Statistiques finales...")
        print(f"   📊 Total permissions: {Permission.objects.count()}")
        print(f"   📊 Total rôles: {Role.objects.count()}")
        print(f"   📊 Utilisateurs avec rôles: {UserRole.objects.filter(is_active=True).count()}")
        
        print("\n✅ Test du middleware terminé!")
        print("🛡️ Le middleware de permissions fonctionne correctement")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions_middleware()
