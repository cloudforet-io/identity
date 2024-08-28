import logging
from typing import Union

from spaceone.core.error import (ERROR_INVALID_PARAMETER, ERROR_NOT_FOUND,
                                 ERROR_PERMISSION_DENIED)
from spaceone.core.service import (BaseService, authentication_handler,
                                   authorization_handler, event_handler,
                                   mutation_handler, transaction)
from spaceone.core.service.utils import (append_keyword_filter,
                                         append_query_filter, convert_model)

from spaceone.identity.error.error_role import (ERROR_NOT_ALLOWED_ROLE_TYPE,
                                                ERROR_NOT_ALLOWED_USER_STATE)
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import \
    WorkspaceGroupManager
from spaceone.identity.manager.workspace_group_user_manager import \
    WorkspaceGroupUserManager
from spaceone.identity.model.workspace_group.response import \
    WorkspaceGroupResponse
from spaceone.identity.model.workspace_group_user.request import (
    WorkspaceGroupUserAddRequest, WorkspaceGroupUserFindRequest,
    WorkspaceGroupUserGetRequest, WorkspaceGroupUserRemoveRequest,
    WorkspaceGroupUserSearchQueryRequest, WorkspaceGroupUserStatQueryRequest,
    WorkspaceGroupUserUpdateRoleRequest)
from spaceone.identity.model.workspace_group_user.response import (
    WorkspaceGroupUserResponse, WorkspaceGroupUsersResponse,
    WorkspaceGroupUsersSummaryResponse)
from spaceone.identity.service.role_binding_service import RoleBindingService

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceGroupUserService(BaseService):
    resource = "WorkspaceGroupUser"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.workspace_group_mgr = WorkspaceGroupManager()
        self.workspace_group_user_mgr = WorkspaceGroupUserManager()
        self.role_mgr = RoleManager()
        self.rb_svc = RoleBindingService()
        self.rb_mgr = RoleBindingManager()

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def add(
        self, params: WorkspaceGroupUserAddRequest
    ) -> Union[WorkspaceGroupUserResponse, dict]:
        """Add workspace group user
        Args:
            params (WorkspaceGroupUserAddRequest): {
                'workspace_group_id': 'str',     # required
                'users': [
                    {
                        'user_id': 'str',        # required
                        'role_id': 'str',        # required
                    }
                ],
                'user_id': 'str',                # injected from auth (required)
                'domain_id': 'str',              # injected from auth (required)
            }
        Returns:
           WorkspaceGroupUserResponse:
        """
        user_id = self.transaction.get_meta("authorization.user_id")

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        user_role_type = ""
        for user in workspace_group_vo.users:
            if user["user_id"] == user_id:
                user_role_type = user["role_type"]

        if user_role_type == "WORKSPACE_MEMBER":
            _LOGGER.error(
                f"User ID {user_id} does not have permission to add users to workspace group."
            )
            raise ERROR_PERMISSION_DENIED()

        new_users = list(set([user_info["user_id"] for user_info in params.users]))
        old_users = []
        if workspace_group_vo.users:
            old_users = list(
                set([user_info["user_id"] for user_info in workspace_group_vo.users])
            )

        if set(new_users) & set(old_users):
            _LOGGER.error(
                f"Users {new_users} is already added to the workspace group or not registered."
            )
            raise ERROR_INVALID_PARAMETER(
                key="users",
                reason=f"User {new_users} is already added to the workspace group or not registered.",
            )

        user_vos = self.user_mgr.filter_users(
            domain_id=params.domain_id, user_id=new_users
        )

        if not user_vos.count() == len(new_users):
            raise ERROR_NOT_FOUND(key="user_id", value=new_users)

        if user_id not in old_users:
            _LOGGER.error(f"User ID {user_id} is not in workspace group.")
            raise ERROR_PERMISSION_DENIED()

        users = params.users or []
        workspaces = workspace_group_vo.workspaces or []

        role_ids = list(set([user["role_id"] for user in users]))
        role_vos = self.role_mgr.filter_roles(
            role_id=role_ids,
            domain_id=params.domain_id,
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
        )

        role_map = {role_vo.role_id: role_vo.role_type for role_vo in role_vos}

        user_info = {user_vo["user_id"]: user_vo for user_vo in user_vos}
        for user in users:
            user_id = user["user_id"]
            if user_id in user_info:
                user["user_name"] = user_info[user_id]["name"]
                user["state"] = user_info[user_id]["state"]

        new_users = []
        for user in users:
            role_type = role_map[user["role_id"]]

            for workspace_id in workspaces:
                role_binding_params = {
                    "user_id": user["user_id"],
                    "role_id": user["role_id"],
                    "role_type": role_type,
                    "resource_group": "WORKSPACE",
                    "domain_id": params.domain_id,
                    "workspace_group_id": params.workspace_group_id,
                    "workspace_id": workspace_id,
                }
                self.rb_svc.create_role_binding(role_binding_params)

            new_users.append(
                {
                    "user_id": user["user_id"],
                    "role_id": user["role_id"],
                    "role_type": role_type,
                    "user_name": user["user_name"],
                    "state": user["state"],
                }
            )

        old_users = workspace_group_vo.users or []

        params.users = old_users + new_users

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        return WorkspaceGroupUserResponse(**workspace_group_vo.to_dict())

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def remove(
        self, params: WorkspaceGroupUserRemoveRequest
    ) -> Union[WorkspaceGroupUserResponse, dict]:
        """Remove workspace group user
        Args:
            params (WorkspaceGroupUserRemoveRequest): {
                'workspace_group_id': 'str',        # required
                'users': [
                    {
                        'user_id': 'str',           # required
                    }
                ],
                'user_id': 'str',                   # injected from auth (required)
                'domain_id': 'str',                 # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUserResponse:
        """
        user_id = self.transaction.get_meta("authorization.user_id")

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        user_role_type = ""
        for user in workspace_group_vo.users:
            if user["user_id"] == user_id:
                user_role_type = user["role_type"]

        if user_role_type == "WORKSPACE_MEMBER":
            _LOGGER.error(
                f"User ID {user_id} does not have permission to add users to workspace group."
            )
            raise ERROR_PERMISSION_DENIED()

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id,
            params.domain_id,
            user_id=user_id,
        )
        if workspace_group_vo:
            if not self.workspace_group_mgr.check_user_id_in_users(
                user_id, workspace_group_vo
            ):
                _LOGGER.error(f"User ID {user_id} is not in workspace group.")
                ERROR_NOT_FOUND(
                    key="workspace_group_id", value=params.workspace_group_id
                )
        else:
            ERROR_NOT_FOUND(key="workspace_group_id", value=params.workspace_group_id)

        workspace_group_user_ids = [
            user["user_id"] for user in workspace_group_vo.users
        ]
        params_user_ids = list(set([user["user_id"] for user in params.users]))

        for params_user_id in params_user_ids:
            if params_user_id not in workspace_group_user_ids:
                raise ERROR_NOT_FOUND(key="params_user_id", value=params_user_id)

        workspace_group_users = [users for users in workspace_group_vo["users"]]
        role_binding_vos = self.rb_mgr.filter_role_bindings(
            user_id=params_user_ids,
            workspace_group_id=params.workspace_group_id,
            domain_id=params.domain_id,
        )
        role_binding_vos.delete()

        params.users = []
        for user in workspace_group_users:
            if user["user_id"] not in params_user_ids:
                params.users.append(user)

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        return WorkspaceGroupUserResponse(**workspace_group_vo.to_dict())

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def update_role(
        self, params: WorkspaceGroupUserUpdateRoleRequest
    ) -> Union[WorkspaceGroupUserResponse, dict]:
        """Update workspace group user role
        Args:
            params (WorkspaceGroupUserUpdateRoleRequest): {
                'workspace_group_id': 'str',            # required
                'role_id': 'str',                       # required
                'params_user_id': 'str',                # required
                'user_id': 'str',                       # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUserResponse:
        """
        user_id = self.transaction.get_meta("authorization.user_id")

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        user_role_type = ""
        for user in workspace_group_vo.users:
            if user["user_id"] == user_id:
                user_role_type = user["role_type"]

        if user_role_type == "WORKSPACE_MEMBER":
            _LOGGER.error(
                f"User ID {user_id} does not have permission to add users to workspace group."
            )
            raise ERROR_PERMISSION_DENIED()

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )
        user_vo = self.user_mgr.get_user(params.params_user_id, params.domain_id)
        if user_vo.state in ["DISABLED", "DELETED"]:
            _LOGGER.error(f"User ID {user_vo.user_id}'s state is {user_vo.state}.")
            raise ERROR_NOT_ALLOWED_USER_STATE(
                user_id=user_vo.user_id, state=user_vo.state
            )

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        if role_vo.role_type not in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE()

        role_binding_vos = self.rb_mgr.filter_role_bindings(
            user_id=user_vo.user_id,
            role_id=role_vo.role_id,
            workspace_group_id=workspace_group_vo.workspace_group_id,
            domain_id=params.domain_id,
        )

        for role_binding_vo in role_binding_vos:
            role_binding_vo.update(
                {"role_id": params.role_id, "role_type": role_vo.role_type}
            )

        update_workspace_group_params = {"users": workspace_group_vo.users or []}
        for user_info in update_workspace_group_params.get("users", []):
            if user_info["user_id"] == user_vo.user_id:
                user_info["role_id"] = params.role_id
                user_info["role_type"] = role_vo.role_type
                break

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            update_workspace_group_params, workspace_group_vo
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(permission="identity:WorkspaceGroupUser:read", role_types=["USER"])
    @convert_model
    def find(
        self, params: WorkspaceGroupUserFindRequest
    ) -> Union[WorkspaceGroupUsersSummaryResponse, dict]:
        """Find users in the domain except users in its workspace_group
        Args:
            params (WorkspaceGroupUserFindRequest): {
                'workspace_group_id': 'str',      # required
                'keyword': 'str',
                'state': 'State',
                'page': 'dict',
                'user_id': 'str'                  # injected from auth (required)
                'domain_id': 'str',               # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUsersSummaryResponse:
        """
        return self._find(params)

    @transaction(permission="identity:WorkspaceGroupUser:read", role_types=["USER"])
    @convert_model
    def get(
        self, params: WorkspaceGroupUserGetRequest
    ) -> Union[WorkspaceGroupUserResponse, dict]:
        """Get workspace groups
        Args:
            params (WorkspaceGroupUserGetRequest): {
                'workspace_group_id': 'str',     # required
                'user_id': 'str'                 # injected from auth (required)
                'domain_id': 'str',              # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUserResponse:
        """
        user_info = self.workspace_group_user_mgr.get_workspace_group_user(
            params.user_id, params.workspace_group_id, params.domain_id
        )
        return WorkspaceGroupUserResponse(**user_info)

    @transaction(permission="identity:WorkspaceGroupUser.read", role_types=["USER"])
    @append_query_filter(["user_id", "workspace_group_id", "name", "domain_id"])
    @append_keyword_filter(["user_id", "workspace_group_id", "name"])
    @convert_model
    def list(
        self, params: WorkspaceGroupUserSearchQueryRequest
    ) -> Union[WorkspaceGroupUsersResponse, dict]:
        """List workspace group users
        Args:
            params (WorkspaceGroupUserSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'workspace_group_id': 'str',
                'name': 'str',
                'created_by': 'str',
                'updated_by': 'str',
                'user_id': 'str'                         # injected from auth (required)
                'domain_id': 'str',                      # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUsersResponse:
        """
        query = params.query or {}
        users_info, total_count = (
            self.workspace_group_user_mgr.list_workspace_group_users(
                query,
                params.user_id,
                params.domain_id,
            )
        )

        return WorkspaceGroupUsersResponse(results=users_info, total_count=total_count)

    @transaction(permission="identity:WorkspaceGroup.read", role_types=["USER"])
    @append_query_filter(["user_id", "workspace_group_id", "domain_id"])
    @convert_model
    def stat(self, params: WorkspaceGroupUserStatQueryRequest) -> dict:
        """Stat workspace group users
        Args:
            params (WorkspaceGroupUserStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_group_id': 'str',           # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        query = params.query or {}

        return self.workspace_group_user_mgr.stat_workspace_group_users(
            query, params.workspace_group_id, params.domain_id
        )

    def _find(
        self, params: WorkspaceGroupUserFindRequest
    ) -> Union[WorkspaceGroupUsersSummaryResponse, dict]:
        workspace_group = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )
        workspace_group_users = workspace_group.users or []
        workspace_group_user_ids = list(
            set([user["user_id"] for user in workspace_group_users])
        )

        query = {
            "filter": [
                {"k": "domain_id", "v": params.domain_id, "o": "eq"},
                {"k": "user_id", "v": workspace_group_user_ids, "o": "not_in"},
            ],
            "sort": [{"key": "user_id"}],
            "page": params.page,
            "only": ["user_id", "name", "state"],
        }

        if params.keyword:
            query["filter_or"] = [
                {"k": "user_id", "v": params.keyword, "o": "contain"},
                {"k": "name", "v": params.keyword, "o": "contain"},
            ]

        if params.state:
            query["filter"].append({"k": "state", "v": params.state, "o": "eq"})

        user_mgr = UserManager()
        user_vos, total_count = user_mgr.list_users(query)

        workspace_group_users_info = [user_vo.to_dict() for user_vo in user_vos]

        return WorkspaceGroupUsersSummaryResponse(
            results=workspace_group_users_info, total_count=total_count
        )
