"""
URLs pour l'app permissions
"""
from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    # Permissions
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/<int:pk>/', views.permission_detail, name='permission_detail'),
    path('permissions/create/', views.permission_create, name='permission_create'),
    path('permissions/<int:pk>/update/', views.permission_update, name='permission_update'),
    path('permissions/<int:pk>/delete/', views.permission_delete, name='permission_delete'),
    path('permissions/stats/', views.permission_stats, name='permission_stats'),
    
    # Permissions conditionnelles
    path('conditional-permissions/', views.conditional_permission_list, name='conditional_permission_list'),
    path('conditional-permissions/<int:pk>/', views.conditional_permission_detail, name='conditional_permission_detail'),
    
    # Rôles
    path('roles/', views.role_list, name='role_list'),
    path('roles/<int:pk>/', views.role_detail, name='role_detail'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/update/', views.role_update, name='role_update'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    path('roles/stats/', views.role_stats, name='role_stats'),
    
    # Permissions de rôles
    path('roles/<int:role_pk>/permissions/', views.role_permission_list, name='role_permission_list'),
    path('roles/<int:role_pk>/permissions/<int:permission_pk>/', views.role_permission_detail, name='role_permission_detail'),
    
    # Groupes
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('groups/stats/', views.group_stats, name='group_stats'),
    
    # Adhésions aux groupes
    path('group-memberships/', views.group_membership_list, name='group_membership_list'),
    path('group-memberships/<int:pk>/', views.group_membership_detail, name='group_membership_detail'),
    
    # Rôles de groupes
    path('group-roles/', views.group_role_list, name='group_role_list'),
    path('group-roles/<int:pk>/', views.group_role_detail, name='group_role_detail'),
    
    # Rôles utilisateur
    path('user-roles/', views.user_role_list, name='user_role_list'),
    path('user-roles/<int:pk>/', views.user_role_detail, name='user_role_detail'),
    path('user-roles/create/', views.user_role_create, name='user_role_create'),
    path('user-roles/<int:pk>/update/', views.user_role_update, name='user_role_update'),
    path('user-roles/<int:pk>/delete/', views.user_role_delete, name='user_role_delete'),
    path('user-roles/stats/', views.user_role_stats, name='user_role_stats'),
    
    # Délégations de permissions
    path('permission-delegations/', views.permission_delegation_list, name='permission_delegation_list'),
    path('permission-delegations/<int:pk>/', views.permission_delegation_detail, name='permission_delegation_detail'),
    path('permission-delegations/create/', views.permission_delegation_create, name='permission_delegation_create'),
    path('permission-delegations/<int:pk>/revoke/', views.permission_delegation_revoke, name='permission_delegation_revoke'),
    
    # Délégations de rôles
    path('role-delegations/', views.role_delegation_list, name='role_delegation_list'),
    path('role-delegations/<int:pk>/', views.role_delegation_detail, name='role_delegation_detail'),
    path('role-delegations/create/', views.role_delegation_create, name='role_delegation_create'),
    path('role-delegations/<int:pk>/revoke/', views.role_delegation_revoke, name='role_delegation_revoke'),
    
    # Statistiques des délégations
    path('delegations/stats/', views.delegation_stats, name='delegation_stats'),
    
    # Gestionnaires de permissions
    path('permission-managers/', views.permission_manager_list, name='permission_manager_list'),
    path('permission-managers/<int:pk>/', views.permission_manager_detail, name='permission_manager_detail'),
    path('permission-managers/create/', views.permission_manager_create, name='permission_manager_create'),
    path('permission-managers/<int:pk>/update/', views.permission_manager_update, name='permission_manager_update'),
    path('permission-managers/<int:pk>/delete/', views.permission_manager_delete, name='permission_manager_delete'),
    path('permission-managers/stats/', views.permission_manager_stats, name='permission_manager_stats'),
]

