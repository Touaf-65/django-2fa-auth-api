"""
Vues pour l'app permissions
"""
from .permission_views import (
    permission_list,
    permission_detail,
    permission_create,
    permission_update,
    permission_delete,
    permission_stats,
    conditional_permission_list,
    conditional_permission_detail,
)
from .role_views import (
    role_list,
    role_detail,
    role_create,
    role_update,
    role_delete,
    role_stats,
    role_permission_list,
    role_permission_detail,
)
from .group_views import (
    group_list,
    group_detail,
    group_create,
    group_update,
    group_delete,
    group_stats,
    group_membership_list,
    group_membership_detail,
    group_role_list,
    group_role_detail,
)
from .user_role_views import (
    user_role_list,
    user_role_detail,
    user_role_create,
    user_role_update,
    user_role_delete,
    user_role_stats,
)
from .delegation_views import (
    permission_delegation_list,
    permission_delegation_detail,
    permission_delegation_create,
    permission_delegation_revoke,
    role_delegation_list,
    role_delegation_detail,
    role_delegation_create,
    role_delegation_revoke,
    delegation_stats,
)
from .permission_manager_views import (
    permission_manager_list,
    permission_manager_detail,
    permission_manager_create,
    permission_manager_update,
    permission_manager_delete,
    permission_manager_stats,
)

__all__ = [
    # Permission views
    'permission_list',
    'permission_detail',
    'permission_create',
    'permission_update',
    'permission_delete',
    'permission_stats',
    'conditional_permission_list',
    'conditional_permission_detail',
    
    # Role views
    'role_list',
    'role_detail',
    'role_create',
    'role_update',
    'role_delete',
    'role_stats',
    'role_permission_list',
    'role_permission_detail',
    
    # Group views
    'group_list',
    'group_detail',
    'group_create',
    'group_update',
    'group_delete',
    'group_stats',
    'group_membership_list',
    'group_membership_detail',
    'group_role_list',
    'group_role_detail',
    
    # User role views
    'user_role_list',
    'user_role_detail',
    'user_role_create',
    'user_role_update',
    'user_role_delete',
    'user_role_stats',
    
    # Delegation views
    'permission_delegation_list',
    'permission_delegation_detail',
    'permission_delegation_create',
    'permission_delegation_revoke',
    'role_delegation_list',
    'role_delegation_detail',
    'role_delegation_create',
    'role_delegation_revoke',
    'delegation_stats',
    
    # Permission manager views
    'permission_manager_list',
    'permission_manager_detail',
    'permission_manager_create',
    'permission_manager_update',
    'permission_manager_delete',
    'permission_manager_stats',
]



