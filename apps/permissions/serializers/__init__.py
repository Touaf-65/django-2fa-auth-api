"""
Serializers pour l'app permissions
"""
from .permission_serializers import (
    PermissionSerializer,
    PermissionCreateSerializer,
    PermissionUpdateSerializer,
    PermissionListSerializer,
    PermissionStatsSerializer,
    ConditionalPermissionSerializer,
)
from .role_serializers import (
    RoleSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    RoleListSerializer,
    RoleStatsSerializer,
    RolePermissionSerializer,
)
from .group_serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupListSerializer,
    GroupStatsSerializer,
    GroupMembershipSerializer,
    GroupRoleSerializer,
)
from .user_role_serializers import (
    UserRoleSerializer,
    UserRoleCreateSerializer,
    UserRoleUpdateSerializer,
    UserRoleListSerializer,
    UserRoleStatsSerializer,
)
from .delegation_serializers import (
    PermissionDelegationSerializer,
    PermissionDelegationCreateSerializer,
    RoleDelegationSerializer,
    RoleDelegationCreateSerializer,
    DelegationStatsSerializer,
)
from .permission_manager_serializers import (
    PermissionManagerSerializer,
    PermissionManagerCreateSerializer,
    PermissionManagerUpdateSerializer,
    PermissionManagerListSerializer,
    PermissionManagerStatsSerializer,
)

__all__ = [
    # Permission serializers
    'PermissionSerializer',
    'PermissionCreateSerializer',
    'PermissionUpdateSerializer',
    'PermissionListSerializer',
    'PermissionStatsSerializer',
    'ConditionalPermissionSerializer',
    
    # Role serializers
    'RoleSerializer',
    'RoleCreateSerializer',
    'RoleUpdateSerializer',
    'RoleListSerializer',
    'RoleStatsSerializer',
    'RolePermissionSerializer',
    
    # Group serializers
    'GroupSerializer',
    'GroupCreateSerializer',
    'GroupUpdateSerializer',
    'GroupListSerializer',
    'GroupStatsSerializer',
    'GroupMembershipSerializer',
    'GroupRoleSerializer',
    
    # User role serializers
    'UserRoleSerializer',
    'UserRoleCreateSerializer',
    'UserRoleUpdateSerializer',
    'UserRoleListSerializer',
    'UserRoleStatsSerializer',
    
    # Delegation serializers
    'PermissionDelegationSerializer',
    'PermissionDelegationCreateSerializer',
    'RoleDelegationSerializer',
    'RoleDelegationCreateSerializer',
    'DelegationStatsSerializer',
    
    # Permission manager serializers
    'PermissionManagerSerializer',
    'PermissionManagerCreateSerializer',
    'PermissionManagerUpdateSerializer',
    'PermissionManagerListSerializer',
    'PermissionManagerStatsSerializer',
]
