import logging
from datetime import datetime
from typing import Union

from spaceone.core.error import (
    ERROR_EXIST_RESOURCE,
    ERROR_INVALID_PARAMETER,
    ERROR_NOT_FOUND,
    ERROR_PERMISSION_DENIED,
)
from spaceone.core.service import (
    BaseService,
    authentication_handler,
    authorization_handler,
    event_handler,
    mutation_handler,
    transaction,
)
from spaceone.core.service.utils import (
    append_keyword_filter,
    append_query_filter,
    convert_model,
)

from spaceone.identity.error import ERROR_ROLE_DOES_NOT_EXIST_OF_USER
from spaceone.identity.error.error_role import (
    ERROR_NOT_ALLOWED_ROLE_TYPE,
    ERROR_NOT_ALLOWED_USER_STATE,
)
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.manager.workspace_user_manager import WorkspaceUserManager
from spaceone.identity.model.workspace_group.request import (
    WorkspaceGroupAddUsersRequest,
    WorkspaceGroupAddWorkspacesRequest,
    WorkspaceGroupCreateRequest,
    WorkspaceGroupDeleteRequest,
    WorkspaceGroupGetRequest,
    WorkspaceGroupRemoveUsersRequest,
    WorkspaceGroupRemoveWorkspacesRequest,
    WorkspaceGroupSearchQueryRequest,
    WorkspaceGroupStatQueryRequest,
    WorkspaceGroupUpdateRequest,
    WorkspaceGroupUpdateRoleRequest,
)
from spaceone.identity.model.workspace_group.response import (
    WorkspaceGroupResponse,
    WorkspaceGroupsResponse,
)
from spaceone.identity.service.role_binding_service import RoleBindingService

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceGroupService(BaseService):
    resource = "WorkspaceGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_group_mgr = WorkspaceGroupManager()
        self.workspace_user_mgr = WorkspaceUserManager()
        self.user_mgr = UserManager()
        self.role_mgr = RoleManager()
        self.rb_svc = RoleBindingService()
        self.rb_mgr = RoleBindingManager()

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def create(
        self, params: WorkspaceGroupCreateRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Create workspace group
        Args:
            params (WorkspaceGroupCreateRequest): {
                'name': 'str',                  # required
                'tags': 'dict',
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        params_data = params.dict()
        params_data["created_by"] = self.transaction.get_meta("authorization.user_id")

        workspace_group_vo = self.workspace_group_mgr.create_workspace_group(
            params_data
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def update(
        self, params: WorkspaceGroupUpdateRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Update workspace group
        Args:
            params (WorkspaceGroupUpdateRequest): {
                'workspace_group_id': 'str',    # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # inje     WorkspaceGroupResponse:
        """
        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        params_data = params.dict()
        params_data["updated_by"] = self.transaction.get_meta("authorization.user_id")
        params_data["updated_at"] = datetime.utcnow()

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params_data, workspace_group_vo
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def delete(self, params: WorkspaceGroupDeleteRequest) -> None:
        """Delete workspace group
        Args:
            params (WorkspaceGroupDeleteRequest): {
                'workspace_group_id': 'str',    # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth (required)
            }
        Returns:
            None
        """
        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        if workspace_group_vo.users:
            _LOGGER.error("Workspace Group has users. Please remove users first.")
            raise ERROR_EXIST_RESOURCE(child="users", parent="workspace_group")
        self.workspace_group_mgr.delete_workspace_group_by_vo(workspace_group_vo)

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def add_workspaces(
        self, params: WorkspaceGroupAddWorkspacesRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Add workspaces to workspace group
        Args:
            params (WorkspaceGroupAddWorkspacesRequest): {
                'workspace_group_id': 'str',           # required
                'workspaces': 'List[str]',             # required
                'workspace_id': 'str',                 # injected from auth
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        workspace_mgr = WorkspaceManager()
        query = {"filter": [{"k": "domain_id", "v": params.domain_id, "o": "eq"}]}
        workspace_list, count = workspace_mgr.list_workspaces(query)
        workspace_id_list = [workspace.workspace_id for workspace in workspace_list]

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        all_workspaces_exist = all(
            params_workspace_id in workspace_id_list
            for params_workspace_id in params.workspaces
        )

        users = workspace_group_vo.users or []
        user_role_ids = list(set([user_info["role_id"] for user_info in users]))
        role_vos = self.role_mgr.filter_roles(
            role_id=user_role_ids, domain_id=params.domain_id
        )
        role_id_map = {
            user_info["user_id"]: user_info["role_id"] for user_info in users
        }

        if len(user_role_ids) != len(role_vos):
            for user_info in users:
                if user_info["user_id"] not in role_id_map:
                    raise ERROR_ROLE_DOES_NOT_EXIST_OF_USER(
                        role_id=user_info["role_id"], user_id=user_info["user_id"]
                    )

        if not all_workspaces_exist:
            raise ERROR_NOT_FOUND(key="workspaces", value=params.workspaces)
        elif (len(params.workspaces) > 0) and all_workspaces_exist:
            workspaces = workspace_group_vo.workspaces or []
            workspaces.extend(params.workspaces)
            params.workspaces = list(set(workspaces))

            role_id_map = {
                user_info["user_id"]: user_info["role_id"] for user_info in users
            }

            workspaces = workspace_group_vo.workspaces or []
            for user_info in users:
                for workspace_id in workspaces:
                    role_binding_params = {
                        "user_id": user_info["user_id"],
                        "role_id": role_id_map[user_info["user_id"]],
                        "resource_group": "WORKSPACE",
                        "domain_id": params.domain_id,
                        "workspace_group_id": params.workspace_group_id,
                        "workspace_id": workspace_id,
                    }
                    self.rb_svc.create_role_binding(role_binding_params)

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def remove_workspaces(
        self, params: WorkspaceGroupRemoveWorkspacesRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Remove workspaces from workspace group
        Args:
            params (WorkspaceGroupRemoveWorkspacesRequest): {
                'workspace_group_id': 'str',              # required
                'workspaces': 'List[str]',                # required
                'workspace_id': 'str',                    # injected from auth
                'domain_id': 'str',                       # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        workspaces = workspace_group_vo.workspaces or []
        params.workspaces = list(set(workspaces) - set(params.workspaces))

        rb_vos = self.rb_mgr.filter_role_bindings(
            workspace_id=params.workspaces,
            workspace_group_id=workspace_group_vo.workspace_group_id,
            domain_id=params.domain_id,
        )
        _LOGGER.info(
            f"[remove_workspaces] deleted role bindings count: {rb_vos.count()}"
        )
        rb_vos.delete()

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def add_users(
        self, params: WorkspaceGroupAddUsersRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Add users to workspace group
        Args:
            params (WorkspaceGroupAddUsersRequest): {
                'workspace_group_id': 'str',      # required
                'users': [
                    {
                        'user_id': 'str',
                        'role_id': 'str',
                    }
                ],                                # required
                'workspace_id': 'str',
                'domain_id': 'str',               # injected from auth (required)
            }
        Returns:
           WorkspaceGroupResponse:
        """
        owner_type = self.transaction.get_meta("authorization.owner_type")
        role_type = self.transaction.get_meta("authorization.role_type")

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

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

        if role_type == "WORKSPACE_OWNER":
            if owner_type == "APP":
                _LOGGER.error("Workspace Owner role type by app cannot add users.")
                raise ERROR_PERMISSION_DENIED()
            else:
                user_id = self.transaction.get_meta("authorization.user_id")
                if user_id not in old_users:
                    _LOGGER.error(f"User ID {user_id} is not in workspace group.")
                    raise ERROR_PERMISSION_DENIED()
        elif role_type != "DOMAIN_ADMIN":
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

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def remove_users(
        self, params: WorkspaceGroupRemoveUsersRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Remove users from workspace group
        Args:
            params (WorkspaceGroupRemoveUsersRequest): {
                'workspace_group_id': 'str',         # required
                'users': [
                    'user_id': 'str'
                ],                                   # required
                'workspace_id': 'str',
                'domain_id': 'str',                  # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        role_type = self.transaction.get_meta("authorization.role_type")
        owner_type = self.transaction.get_meta("authorization.owner_type")

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        if role_type == "WORKSPACE_OWNER":
            if owner_type == "APP":
                _LOGGER.error("Workspace Owner role type by app cannot remove users.")
                raise ERROR_PERMISSION_DENIED()
            else:
                user_id = self.transaction.get_meta("authorization.user_id")
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
                    ERROR_NOT_FOUND(
                        key="workspace_group_id", value=params.workspace_group_id
                    )
        elif role_type != "DOMAIN_ADMIN":
            raise ERROR_PERMISSION_DENIED()

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

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceGroup.write", role_types=["DOMAIN_ADMIN"]
    )
    @convert_model
    def update_role(
        self, params: WorkspaceGroupUpdateRoleRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Update workspace group's user's role

        Args:
            params (WorkspaceGroupUpdateRoleRequest): {
                'workspace_group_id': 'str',        # required
                'user_id': 'str',                   # required
                'role_id': 'str',                   # required
                'workspace_id': 'str',              # injected from auth (required)
                'domain_id': 'str',                 # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )
        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
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

    @convert_model
    @transaction(permission="identity:WorkspaceGroup.read", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def get(
        self, params: WorkspaceGroupGetRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Get workspace group

        Args:
            params (WorkspaceGroupGetRequest): {
                'workspace_group_id': 'str', # required
                'workspace_id': 'str',
                'domain_id': 'str',          # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        user_id = self.transaction.get_meta("authorization.user_id")
        role_type = self.transaction.get_meta("authorization.role_type")

        workspace_group_vo = None
        if role_type == "DOMAIN_ADMIN":
            workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
                params.workspace_group_id, params.domain_id
            )
        elif role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
                params.workspace_group_id, params.domain_id, user_id
            )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(permission="identity:WorkspaceGroup.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(["workspace_group_id", "name", "domain_id"])
    @append_keyword_filter(["workspace_group_id", "name"])
    @convert_model
    def list(
        self, params: WorkspaceGroupSearchQueryRequest
    ) -> Union[WorkspaceGroupsResponse, dict]:
        """List workspace groups
        Args:
            params (WorkspaceGroupSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'workspace_group_id': 'str',         # required
                'name': 'str',
                'created_by': 'str',
                'updated_by': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',                  # injected from auth (required)
            }
        Returns:
            WorkspaceGroupsResponse:
        """
        user_id = self.transaction.get_meta("authorization.user_id")
        role_type = self.transaction.get_meta("authorization.role_type")

        query = {}
        if role_type == "DOMAIN_ADMIN":
            query = params.query
        elif role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            query = params.query
            query["filter"] = query.get("filter", [])
            query["filter"].append(
                {
                    "k": "users",
                    "v": user_id,
                    "o": "contain",
                }
            )

        workspace_group_vos, total_count = (
            self.workspace_group_mgr.list_workspace_groups(query)
        )

        workspace_groups_info = [
            workspace_group_vo.to_dict() for workspace_group_vo in workspace_group_vos
        ]

        return WorkspaceGroupsResponse(
            results=workspace_groups_info, total_count=total_count
        )

    @transaction(permission="identity:WorkspaceGroup.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(["workspace_id", "workspace_group_id", "domain_id"])
    @convert_model
    def stat(self, params: WorkspaceGroupStatQueryRequest) -> dict:
        """Stat workspace groups
        Args:
            params (WorkspaceGroupStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',             # injected from auth (required)
                'domain_id': 'str',                # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        user_id = self.transaction.get_meta("authorization.user_id")
        role_type = self.transaction.get_meta("authorization.role_type")

        query = {}
        if role_type == "DOMAIN_ADMIN":
            query = params.query
        elif role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            query = params.query
            query["filter"] = query.get("filter", [])
            query["filter"].append(
                {
                    "k": "users",
                    "v": user_id,
                    "o": "contain",
                }
            )

        if params.workspace_id:
            query = params.query
        return self.workspace_group_mgr.stat_workspace_group(query)
