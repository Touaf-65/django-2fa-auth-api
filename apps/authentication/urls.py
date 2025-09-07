"""
URLs pour l'application authentication
"""

from django.urls import path
from .views import (
    user_registration,
    user_login,
    user_logout,
    TokenRefreshView,
    user_profile,
    update_user_profile,
    two_factor_setup,
    two_factor_verify_setup,
    two_factor_verify_login,
    two_factor_disable,
    two_factor_status,
    two_factor_regenerate_backup_codes,
)

app_name = 'authentication'

urlpatterns = [
    # Authentification de base
    path('signup/', user_registration, name='signup'),
    path('signin/', user_login, name='signin'),
    path('logout/', user_logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profil utilisateur
    path('profile/', user_profile, name='profile'),
    path('profile/update/', update_user_profile, name='profile_update'),
    
    # Authentification à deux facteurs
    path('2fa/setup/', two_factor_setup, name='2fa_setup'),
    path('2fa/verify-setup/', two_factor_verify_setup, name='2fa_verify_setup'),
    path('2fa/verify-login/', two_factor_verify_login, name='2fa_verify_login'),
    path('2fa/disable/', two_factor_disable, name='2fa_disable'),
    path('2fa/status/', two_factor_status, name='2fa_status'),
    path('2fa/regenerate-backup-codes/', two_factor_regenerate_backup_codes, name='2fa_regenerate_backup_codes'),
]
