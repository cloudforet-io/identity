import logging
from typing import Dict, List, Tuple

from spaceone.core.error import (
    ERROR_INVALID_PARAMETER,
    ERROR_NOT_FOUND,
    ERROR_PERMISSION_DENIED,
)
from spaceone.core.manager import BaseManager

from spaceone.identity.error.error_role import (
    ERROR_NOT_ALLOWED_ROLE_TYPE,
    ERROR_NOT_ALLOWED_USER_STATE,
)
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model import WorkspaceGroup

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupUserManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_mgr = RoleManager()
        self.rb_mgr = RoleBindingManager()
        self.user_mgr = UserManager()
        self.workspace_mgr = WorkspaceManager()
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

    def get_old_users_and_new_users(
        self, users: List[Dict[str, str]], workspace_group_id: str, domain_id: str
    ) -> Tuple[List[str], List[str]]:
        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            workspace_group_id, domain_id
        )

        old_users = list(
            set(
                [user_info["user_id"] for user_info in workspace_group_vo.users]
                if workspace_group_vo.users
                else []
            )
        )
        new_users = list(set([user_info["user_id"] for user_info in users]))

        return old_users, new_users

    @staticmethod
    def check_new_users_already_in_workspace_group(
        old_users: List[str], new_users: List[str]
    ) -> None:
        if set(old_users) & set(new_users):
            _LOGGER.error(
                f"Users {new_users} is already in the workspace group or not registered."
            )
            raise ERROR_INVALID_PARAMETER(
                key="users",
                reason=f"User {new_users} is already in the workspace group or not registered.",
            )

    def check_new_users_exist_in_domain(
        self, new_users: List[str], domain_id: str
    ) -> None:
        new_user_vos = self.user_mgr.filter_users(
            domain_id=domain_id, user_id=new_users
        )
        if not new_user_vos.count() == len(new_users):
            raise ERROR_NOT_FOUND(key="user_id", value=new_users)

    @staticmethod
    def check_user_role_type(
        old_users_in_workspace_group: List[Dict[str, str]],
        user_id: str,
        command: str,
    ) -> None:
        user_role_type = ""
        for old_user in old_users_in_workspace_group:
            if old_user["user_id"] == user_id:
                user_role_type = old_user["role_type"]

        if user_role_type == "WORKSPACE_MEMBER":
            _LOGGER.error(
                f"User ID {user_id} does not have permission to {command} users to workspace group."
            )
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def check_user_in_workspace_group(
        old_users_in_workspace_group: List[Dict[str, str]], user_id: str
    ) -> None:
        if user_id not in old_users_in_workspace_group:
            _LOGGER.error(f"User ID {user_id} is not in workspace group.")
            raise ERROR_PERMISSION_DENIED()

    def add_users_to_workspace_group(
        self,
        users: List[Dict[str, str]],
        role_map: Dict[str, str],
        workspace_ids: List[str],
        workspace_group_id: str,
        domain_id: str,
    ) -> List[Dict[str, str]]:
        new_users_in_workspace_group = []
        if workspace_ids:
            for workspace_id in workspace_ids:
                for new_user_info in users:
                    role_type = role_map[new_user_info["role_id"]]

                    role_binding_params = {
                        "user_id": new_user_info["user_id"],
                        "role_id": new_user_info["role_id"],
                        "role_type": role_type,
                        "resource_group": "WORKSPACE",
                        "domain_id": domain_id,
                        "workspace_group_id": workspace_group_id,
                        "workspace_id": workspace_id,
                    }
                    self.rb_mgr.create_role_binding(role_binding_params)

                    new_users_in_workspace_group.append(
                        {
                            "user_id": new_user_info["user_id"],
                            "role_id": new_user_info["role_id"],
                            "role_type": role_type,
                        }
                    )
        else:
            for new_user_info in users:
                role_type = role_map[new_user_info["role_id"]]

                new_users_in_workspace_group.append(
                    {
                        "user_id": new_user_info["user_id"],
                        "role_id": new_user_info["role_id"],
                        "role_type": role_type,
                    }
                )

        return new_users_in_workspace_group

    def get_role_map(
        self, new_users_in_workspace_group: List[Dict[str, str]], domain_id: str
    ) -> Dict[str, str]:
        role_ids = list(set([user["role_id"] for user in new_users_in_workspace_group]))
        role_vos = self.role_mgr.filter_roles(
            role_id=role_ids,
            domain_id=domain_id,
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
        )

        role_map = {role_vo.role_id: role_vo.role_type for role_vo in role_vos}

        return role_map

    def add_user_name_and_state_to_new_users(
        # user_info: dict, new_users_in_workspace_group: List[Dict[str, str]]
        self,
        workspace_group_user_ids: List[str],
        workspace_group_vo: WorkspaceGroup,
        domain_id: str,
    ) -> Dict[str, str]:
        user_vos = self.user_mgr.filter_users(
            user_id=workspace_group_user_ids, domain_id=domain_id
        )

        user_info_map = {}
        for user_vo in user_vos:
            user_info_map[user_vo.user_id] = {
                "name": user_vo.name,
                "state": user_vo.state,
            }

        workspace_group_dict = workspace_group_vo.to_dict()
        users = []
        for user in workspace_group_dict["users"]:
            user_id = user["user_id"]
            user["user_name"] = user_info_map[user_id]["name"]
            user["state"] = user_info_map[user_id]["state"]
            users.append(user)

        workspace_group_dict["users"] = users

        return workspace_group_dict

    @staticmethod
    def get_workspace_ids(workspace_group_id: str, domain_id: str) -> List[str]:
        workspace_mgr = WorkspaceManager()
        workspace_vos = workspace_mgr.filter_workspaces(
            workspace_group_id=workspace_group_id, domain_id=domain_id
        )
        workspace_ids = [workspace_vo.workspace_id for workspace_vo in workspace_vos]

        return workspace_ids

    @staticmethod
    def check_user_ids_exist_in_workspace_group(
        old_user_ids: List[str], user_ids: List[str]
    ) -> None:
        for user_id in user_ids:
            if user_id not in old_user_ids:
                _LOGGER.error(f"User ID {user_id} is not in workspace group.")
                raise ERROR_PERMISSION_DENIED()

    def remove_users_from_workspace_group(
        self,
        user_ids: List[str],
        old_users: List[Dict[str, str]],
        workspace_group_id: str,
        domain_id: str,
    ) -> List[Dict[str, str]]:
        rb_vos = self.rb_mgr.filter_role_bindings(
            user_id=user_ids,
            workspace_group_id=workspace_group_id,
            domain_id=domain_id,
        )

        if rb_vos.count() > 0:
            for rb_vo in rb_vos:
                _LOGGER.debug(
                    f"[remove_users] Delete role binding info: {rb_vo.to_dict()}"
                )
                rb_vo.delete()

        updated_users = [user for user in old_users if user["user_id"] not in user_ids]

        return updated_users

    @staticmethod
    def check_user_state(target_user_id: str, target_user_state: str) -> None:
        if target_user_id in ["DISABLED", "DELETED"]:
            _LOGGER.error(f"User ID {target_user_id}'s state is {target_user_state}.")
            raise ERROR_NOT_ALLOWED_USER_STATE(
                user_id=target_user_id, state=target_user_state
            )

    def update_user_role_of_workspace_group(
        self,
        role_id: str,
        role_type: str,
        user_id: str,
        workspace_group_id: str,
        domain_id: str,
    ) -> None:
        role_binding_vos = self.rb_mgr.filter_role_bindings(
            user_id=user_id,
            workspace_group_id=workspace_group_id,
            domain_id=domain_id,
        )

        for role_binding_vo in role_binding_vos:
            role_binding_vo.update({"role_id": role_id, "role_type": role_type})

    @staticmethod
    def check_role_type(role_type: str) -> None:
        if role_type not in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE()

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
