"""
URLs pour l'application users
"""

from django.urls import path
from .views import (
    # Profils utilisateur
    user_profile,
    user_profile_update,
    user_preferences,
    user_activity,
    create_user_profile,
    delete_user_profile,
    user_profile_stats,
    
    # Relations entre utilisateurs
    user_list,
    user_search,
    user_follow,
    user_unfollow,
    user_followers,
    user_following,
    user_block,
    user_unblock,
    user_blocked,
    user_stats,
)

app_name = 'users'

urlpatterns = [
    # Gestion des profils
    path('profile/', user_profile, name='profile'),
    path('profile/update/', user_profile_update, name='profile_update'),
    path('profile/create/', create_user_profile, name='profile_create'),
    path('profile/delete/', delete_user_profile, name='profile_delete'),
    path('profile/stats/', user_profile_stats, name='profile_stats'),
    path('profile/<int:user_id>/', user_profile, name='profile_detail'),
    path('profile/<int:user_id>/stats/', user_profile_stats, name='profile_stats_detail'),
    
    # Préférences utilisateur
    path('preferences/', user_preferences, name='preferences'),
    
    # Activités utilisateur
    path('activity/', user_activity, name='activity'),
    path('activity/<int:user_id>/', user_activity, name='activity_detail'),
    
    # Liste et recherche d'utilisateurs
    path('', user_list, name='user_list'),
    path('search/', user_search, name='user_search'),
    path('stats/', user_stats, name='user_stats'),
    path('<int:user_id>/stats/', user_stats, name='user_stats_detail'),
    
    # Relations de suivi
    path('<int:user_id>/follow/', user_follow, name='user_follow'),
    path('<int:user_id>/unfollow/', user_unfollow, name='user_unfollow'),
    path('followers/', user_followers, name='user_followers'),
    path('following/', user_following, name='user_following'),
    path('<int:user_id>/followers/', user_followers, name='user_followers_detail'),
    path('<int:user_id>/following/', user_following, name='user_following_detail'),
    
    # Blocage d'utilisateurs
    path('<int:user_id>/block/', user_block, name='user_block'),
    path('<int:user_id>/unblock/', user_unblock, name='user_unblock'),
    path('blocked/', user_blocked, name='user_blocked'),
]

