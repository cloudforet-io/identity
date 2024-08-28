import logging
from typing import Tuple

from spaceone.core.error import ERROR_INVALID_PARAMETER
from spaceone.core.manager import BaseManager

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.model.workspace_group.database import WorkspaceGroup
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
        self.workspace_group_model = WorkspaceGroup()

    def get_workspace_group_user(
        self, user_id: str, workspace_group_id: str, domain_id: str
    ) -> dict:
        """Get workspace group user
        Args:
            'user_id': 'str',
            'workspace_group_id': 'str',
            'domain_id': 'str'
        Returns:
             'workspace_group_user_info': 'dict'
        """
        workspace_group_vos = self.workspace_group_mgr.filter_workspace_groups(
            users__user_id=user_id,
            workspace_group_id=workspace_group_id,
            domain_id=domain_id,
        )

        workspace_group_user_info = {}
        for workspace_group_vo in workspace_group_vos:
            workspace_group_user_info = workspace_group_vo.to_dict()

        return workspace_group_user_info

    def list_workspace_group_users(
        self,
        query: dict,
        user_id: str,
        domain_id: str,
    ) -> Tuple[list, int]:
        workspace_group_vos = self.workspace_group_mgr.filter_workspace_groups(
            users__user_id=user_id,
            domain_id=domain_id,
        )
        workspace_group_users_info = []
        for workspace_group_vo in workspace_group_vos:
            workspace_group_users_info.append(workspace_group_vo.to_dict())
        total_count = len(workspace_group_users_info)

        return workspace_group_users_info, total_count

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
        self,
        workspace_group_id: str,
        domain_id: str,
        role_type: str = None,
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
