import logging
from typing import Tuple

from spaceone.core.error import ERROR_INVALID_PARAMETER, ERROR_NOT_FOUND
from spaceone.core.manager import BaseManager

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.service.role_binding_service import RoleBindingService
from spaceone.identity.service.user_service import UserService

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupUserManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_svc = UserService()
        self.rb_svc = RoleBindingService()
        self.rb_mgr = RoleBindingManager()
        self.user_mgr = UserManager()
        self.workspace_group_mgr = WorkspaceGroupManager()

    def get_workspace_group_user(
        self, user_id: str, workspace_group_id: str, domain_id: str
    ) -> dict:
        """Get workspace group user
        Args:
            'user_id': 'str',
            'workspace_group_id': 'str',
            'domain_id': 'str'
        Returns:
            {
                'users': [
                    {
                        'user_id': 'str',
                        'role_id': 'str',
                        'role_type': 'str',
                        'user_name': 'str',
                        'state': 'str'
                    }
                ]
            }
        """
        user_ids, user_rb_map = self._get_role_binding_map_in_workspace_group(
            workspace_group_id, domain_id
        )

        if user_id not in user_ids:
            raise ERROR_NOT_FOUND(key="user_id", value=user_id)

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        updated_user_info = {
            "users": [
                {
                    "user_id": user_rb_map[user_id][0]["user_id"],
                    "role_id": user_rb_map[user_id][0]["role_id"],
                    "role_type": user_rb_map[user_id][0]["role_type"],
                    "user_name": user_vo.name,
                    "state": user_vo.state,
                }
            ]
        }

        return updated_user_info

    def list_workspace_group_users(
        self,
        query: dict,
        domain_id: str,
        workspace_group_id: str,
        role_type: str = None,
    ) -> Tuple[list, int]:
        user_ids, user_rb_map = self._get_role_binding_map_in_workspace_group(
            workspace_group_id, domain_id, role_type
        )
        query["filter"] = query.get("filter", [])
        query["filter"].append({"k": "user_id", "v": user_ids, "o": "in"})

        user_vos, total_count = self.user_mgr.list_users(query)

        users_info = []
        for user_vo in user_vos:
            user_info = {
                "users": [
                    {
                        "user_id": user_vo.user_id,
                        "role_id": user_vo.role_id,
                        "role_type": user_vo.role_type,
                        "user_name": user_vo.name,
                        "state": user_vo.state,
                    }
                ]
            }
            users_info.append(user_info)

        return users_info, total_count

    def stat_workspace_group_users(
        self, query: dict, workspace_group_id: str, domain_id: str
    ) -> dict:
        user_ids, _ = self._get_role_binding_map_in_workspace_group(
            workspace_group_id, domain_id
        )
        query["filter"] = query.get("filter", [])
        query["filter"].append({"k": "user_id", "v": user_ids, "o": "in"})

        return self.user_mgr.stat_users(query)

    def _get_role_binding_map_in_workspace_group(
        self, workspace_group_id: str, domain_id: str, role_type: str = None
    ) -> Tuple[list, dict]:
        user_rb_map = {}
        user_ids = []

        if role_type and role_type not in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            raise ERROR_INVALID_PARAMETER(
                message="role_type must be one of [WORKSPACE_OWNER, WORKSPACE_MEMBER]"
            )

        if role_type is None:
            role_type = ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]

        rb_vos = self.rb_mgr.filter_role_bindings(
            role_type=role_type,
            workspace_group_id=[workspace_group_id, "*"],
            domain_id=domain_id,
        )

        for rb_vo in rb_vos:
            user_ids.append(rb_vo.user_id)
            if user_rb_map.get(rb_vo.user_id):
                user_rb_map[rb_vo.user_id].append(rb_vo.to_dict())
            else:
                user_rb_map[rb_vo.user_id] = [rb_vo.to_dict()]

        return user_ids, user_rb_map
