import logging
from typing import Dict, List, Tuple

from spaceone.core.error import ERROR_INVALID_PARAMETER, ERROR_PERMISSION_DENIED
from spaceone.core.manager import BaseManager

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupUserManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rb_mgr = RoleBindingManager()
        self.user_mgr = UserManager()

    def stat_workspace_group_users(
        self, query: dict, workspace_group_id: str, domain_id: str
    ) -> dict:
        user_ids, _ = self._get_role_binding_map_in_workspace_group(
            workspace_group_id, domain_id
        )
        query["filter"] = query.get("filter", [])
        query["filter"].append({"k": "user_id", "v": user_ids, "o": "in"})

        return self.user_mgr.stat_users(query)

    @staticmethod
    def check_user_role_type(
        old_users_in_workspace_group: List[Dict[str, str]],
        user_id: str,
    ) -> None:
        user_role_type = ""
        for old_user in old_users_in_workspace_group:
            if old_user["user_id"] == user_id:
                user_role_type = old_user["role_type"]

        if user_role_type == "WORKSPACE_MEMBER":
            _LOGGER.error(
                f"[check_user_role_type] User ID {user_id} is WORKSPACE_MEMBER."
            )
            raise ERROR_PERMISSION_DENIED()

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
