"""
URLs pour l'app Authentication
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    user_registration, user_login, user_logout,
    TokenRefreshView, user_profile, update_user_profile,
    two_factor_setup, two_factor_verify_setup, two_factor_verify_login,
    two_factor_disable, two_factor_status, two_factor_regenerate_backup_codes,
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', user_registration, name='user-register'),
    path('login/', user_login, name='user-login'),
    path('logout/', user_logout, name='user-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile
    path('profile/', user_profile, name='user-profile'),
    path('profile/update/', update_user_profile, name='user-profile-update'),
    
    # Two-Factor Authentication
    path('2fa/setup/', two_factor_setup, name='2fa-setup'),
    path('2fa/verify-setup/', two_factor_verify_setup, name='2fa-verify-setup'),
    path('2fa/verify-login/', two_factor_verify_login, name='2fa-verify-login'),
    path('2fa/disable/', two_factor_disable, name='2fa-disable'),
    path('2fa/status/', two_factor_status, name='2fa-status'),
    path('2fa/backup-codes/', two_factor_regenerate_backup_codes, name='2fa-backup-codes'),
]
