import logging
from typing import List, Tuple

from spaceone.core.error import *
from spaceone.core.manager import BaseManager

from spaceone.identity.error.error_workspace_user import (
    ERROR_USER_NOT_EXIST_IN_WORKSPACE,
)
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.user.database import User
from spaceone.identity.service.role_binding_service import RoleBindingService
from spaceone.identity.service.user_service import UserService

_LOGGER = logging.getLogger(__name__)


class WorkspaceUserManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_svc = UserService()
        self.rb_svc = RoleBindingService()
        self.rb_mgr = RoleBindingManager()
        self.user_mgr = UserManager()

    def create_workspace_user(self, params: dict) -> User:
        role_id = params.pop("role_id")
        user_vo = self.user_svc.create_user(params)

        self.rb_svc.create_role_binding(
            {
                "resource_group": "WORKSPACE",
                "user_id": params["user_id"],
                "role_id": role_id,
                "permission_group": "WORKSPACE",
                "workspace_id": params["workspace_id"],
                "domain_id": params["domain_id"],
            }
        )

        return user_vo

    def check_workspace_users(
        self, users: List[str], workspace_id: str, domain_id: str
    ) -> None:
        rb_vos = self.rb_mgr.filter_role_bindings(
            user_id=users,
            workspace_id=[workspace_id, "*"],
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
            domain_id=domain_id,
        )

        existing_users = list(set([rb.user_id for rb in rb_vos]))
        not_existing_users = list(set(users) - set(existing_users))

        for user_id in not_existing_users:
            raise ERROR_USER_NOT_EXIST_IN_WORKSPACE(
                user_id=user_id, workspace_id=workspace_id
            )

    def get_workspace_user(
        self, user_id: str, workspace_id: str, domain_id: str
    ) -> dict:
        user_ids, user_rb_map = self._get_role_binding_map_in_workspace(
            workspace_id, domain_id
        )
        if user_id not in user_ids:
            raise ERROR_NOT_FOUND(key="user_id", value=user_id)

        user_vo = self.user_mgr.get_user(user_id, domain_id)
        user_info = user_vo.to_dict()
        user_info["role_binding_info"] = user_rb_map[user_id]

        return user_info

    def list_workspace_users(
        self, query: dict, domain_id: str, workspace_id: str, role_type: str = None
    ) -> Tuple[list, int]:
        user_ids, user_rb_map = self._get_role_binding_map_in_workspace(
            workspace_id, domain_id, role_type
        )
        query["filter"] = query.get("filter", [])
        query["filter"].append({"k": "user_id", "v": user_ids, "o": "in"})

        user_vos, total_count = self.user_mgr.list_users(query)

        users_info = []
        for user_vo in user_vos:
            user_info = user_vo.to_dict()

            if user_rb_map:
                user_info["role_binding_info"] = user_rb_map[user_vo.user_id]

            users_info.append(user_info)

        return users_info, total_count

    def stat_workspace_users(
        self, query: dict, domain_id: str, workspace_id: str
    ) -> dict:
        user_ids, _ = self._get_role_binding_map_in_workspace(workspace_id, domain_id)
        query["filter"] = query.get("filter", [])
        query["filter"].append({"k": "user_id", "v": user_ids, "o": "in"})

        return self.user_mgr.stat_users(query)

    def _get_role_binding_map_in_workspace(
        self, workspace_id: str, domain_id: str, role_type: str = None
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
            domain_id=domain_id,
            workspace_id=[workspace_id, "*"],
            role_type=role_type,
        )

        for rb_vo in rb_vos:
            user_ids.append(rb_vo.user_id)
            user_rb_map[rb_vo.user_id] = rb_vo.to_dict()

        return user_ids, user_rb_map
