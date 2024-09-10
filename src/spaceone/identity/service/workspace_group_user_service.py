import logging
from typing import Dict, List, Union

from spaceone.core.error import ERROR_NOT_FOUND
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

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_group_user_manager import (
    WorkspaceGroupUserManager,
)
from spaceone.identity.model.workspace_group.response import (
    WorkspaceGroupResponse,
    WorkspaceGroupsResponse,
)
from spaceone.identity.model.workspace_group_user.request import (
    WorkspaceGroupUserAddRequest,
    WorkspaceGroupUserFindRequest,
    WorkspaceGroupUserGetRequest,
    WorkspaceGroupUserRemoveRequest,
    WorkspaceGroupUserSearchQueryRequest,
    WorkspaceGroupUserStatQueryRequest,
    WorkspaceGroupUserUpdateRoleRequest,
)
from spaceone.identity.model.workspace_group_user.response import (
    WorkspaceGroupUsersSummaryResponse,
)
from spaceone.identity.service.role_binding_service import RoleBindingService
from spaceone.identity.service.workspace_group_service import WorkspaceGroupService

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
        self.workspace_group_svc = WorkspaceGroupService()
        self.workspace_group_mgr = WorkspaceGroupManager()
        self.workspace_group_user_mgr = WorkspaceGroupUserManager()
        self.role_mgr = RoleManager()
        self.rb_svc = RoleBindingService()
        self.rb_mgr = RoleBindingManager()

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def add(
        self, params: WorkspaceGroupUserAddRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
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
           WorkspaceGroupResponse:
        """
        workspace_group_id = params.workspace_group_id
        new_users_info_list: List[Dict[str, str]] = params.users
        user_id = params.user_id
        domain_id = params.domain_id

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            workspace_group_id, domain_id
        )

        old_users, new_users = (
            self.workspace_group_mgr.get_unique_old_users_and_new_users(
                new_users_info_list, workspace_group_id, domain_id
            )
        )
        self.workspace_group_mgr.check_new_users_already_in_workspace_group(
            old_users, new_users
        )

        workspace_group_user_ids: List[str] = old_users + new_users

        self.workspace_group_svc.check_new_users_exist_in_domain(new_users, domain_id)

        workspace_group_old_users_info = workspace_group_vo.users or []
        if workspace_group_old_users_info:
            self.workspace_group_user_mgr.check_user_role_type(
                workspace_group_old_users_info, user_id, command="add"
            )

        role_map = self.workspace_group_svc.get_role_map(new_users_info_list, domain_id)

        workspace_group_workspace_ids = self.workspace_group_svc.get_workspace_ids(
            workspace_group_id, domain_id
        )
        workspace_group_new_users_info = (
            self.workspace_group_svc.add_users_to_workspace_group(
                new_users_info_list,
                role_map,
                workspace_group_workspace_ids,
                workspace_group_id,
                domain_id,
            )
        )
        params.users = workspace_group_old_users_info + workspace_group_new_users_info

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        workspace_group_user_dict = (
            self.workspace_group_svc.add_user_name_and_state_to_users(
                workspace_group_user_ids, workspace_group_vo, domain_id
            )
        )

        return WorkspaceGroupResponse(**workspace_group_user_dict)

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def remove(
        self, params: WorkspaceGroupUserRemoveRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
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
            WorkspaceGroupResponse:
        """
        # user_id = self.transaction.get_meta("authorization.user_id")
        workspace_group_id = params.workspace_group_id
        users = params.users
        user_id = params.user_id
        domain_id = params.domain_id

        old_user_ids, user_ids = (
            self.workspace_group_mgr.get_unique_old_users_and_new_users(
                users, workspace_group_id, domain_id
            )
        )
        self.workspace_group_mgr.check_user_ids_exist_in_workspace_group(
            old_user_ids, user_ids
        )

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id, user_id=user_id
        )
        if not workspace_group_vo:
            ERROR_NOT_FOUND(key="workspace_group_id", value=params.workspace_group_id)
        workspace_group_dict = workspace_group_vo.to_mongo().to_dict()

        workspace_group_users = workspace_group_vo.users
        self.workspace_group_user_mgr.check_user_role_type(
            workspace_group_users, user_id, command="remove"
        )

        old_users = workspace_group_dict["users"]
        updated_users = self.workspace_group_svc.remove_users_from_workspace_group(
            user_ids, old_users, workspace_group_id, domain_id
        )
        params.users = updated_users

        workspace_group_vo = self.workspace_group_mgr.update_workspace_group_by_vo(
            params.dict(exclude_unset=True), workspace_group_vo
        )

        return WorkspaceGroupResponse(**workspace_group_vo.to_dict())

    @transaction(permission="identity:WorkspaceGroupUser:write", role_types=["USER"])
    @convert_model
    def update_role(
        self, params: WorkspaceGroupUserUpdateRoleRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Update workspace group user role
        Args:
            params (WorkspaceGroupUserUpdateRoleRequest): {
                'workspace_group_id': 'str',            # required
                'role_id': 'str',                       # required
                'target_user_id': 'str',                # required
                'user_id': 'str',                       # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        workspace_group_id = params.workspace_group_id
        role_id = params.role_id
        target_user_id = params.target_user_id
        user_id = params.user_id
        domain_id = params.domain_id

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            params.workspace_group_id, params.domain_id
        )

        workspace_group_users = workspace_group_vo.users
        self.workspace_group_user_mgr.check_user_role_type(
            workspace_group_users, user_id, command="update_role"
        )

        target_user_vo = self.user_mgr.get_user(target_user_id, domain_id)
        target_user_state = target_user_vo.state
        self.workspace_group_svc.check_user_state(target_user_id, target_user_state)

        role_vo = self.role_mgr.get_role(role_id, domain_id)
        role_type = role_vo.role_type
        self.workspace_group_svc.check_role_type(role_type)

        self.workspace_group_svc.update_user_role_of_workspace_group(
            role_id, role_type, user_id, workspace_group_id, domain_id
        )

        update_workspace_group_params = {"users": workspace_group_vo.users or []}
        for user_info in update_workspace_group_params.get("users", []):
            if user_info["user_id"] == target_user_id:
                user_info["role_id"] = role_id
                user_info["role_type"] = role_type
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

    @transaction(permission="identity:WorkspaceGroupUser:read", role_types=["USER"])
    @convert_model
    def get(
        self, params: WorkspaceGroupUserGetRequest
    ) -> Union[WorkspaceGroupResponse, dict]:
        """Get workspace groups
        Args:
            params (WorkspaceGroupUserGetRequest): {
                'workspace_group_id': 'str',     # required
                'user_id': 'str'                 # injected from auth (required)
                'domain_id': 'str',              # injected from auth (required)
            }
        Returns:
            WorkspaceGroupResponse:
        """
        workspace_group_id = params.workspace_group_id
        domain_id = params.domain_id

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            workspace_group_id, domain_id
        )

        workspace_group_user_ids = []
        if workspace_group_vo.users:
            old_users, new_users = (
                self.workspace_group_mgr.get_unique_old_users_and_new_users(
                    workspace_group_vo.users, workspace_group_id, domain_id
                )
            )

            workspace_group_user_ids: List[str] = old_users + new_users

        workspace_group_dict = (
            self.workspace_group_svc.add_user_name_and_state_to_users(
                workspace_group_user_ids, workspace_group_vo, domain_id
            )
        )
        return WorkspaceGroupResponse(**workspace_group_dict)

    @transaction(permission="identity:WorkspaceGroupUser.read", role_types=["USER"])
    @append_query_filter(["workspace_group_id", "name", "domain_id"])
    @append_keyword_filter(["workspace_group_id", "name"])
    @convert_model
    def list(
        self, params: WorkspaceGroupUserSearchQueryRequest
    ) -> Union[WorkspaceGroupsResponse, dict]:
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
            WorkspaceGroupsResponse:
        """
        query = params.query

        workspace_group_vos, total_count = (
            self.workspace_group_mgr.list_workspace_groups(query)
        )

        workspace_groups_info = []
        for workspace_group_vo in workspace_group_vos:
            workspace_group_users = workspace_group_vo.users or []
            old_users = list(
                set(
                    [user_info["user_id"] for user_info in workspace_group_users]
                    if workspace_group_users
                    else []
                )
            )
            new_users = list(
                set([user_info["user_id"] for user_info in workspace_group_users])
            )

            workspace_group_user_ids: List[str] = old_users + new_users

            workspace_group_dict = (
                self.workspace_group_svc.add_user_name_and_state_to_users(
                    workspace_group_user_ids, workspace_group_vo, params.domain_id
                )
            )
            workspace_groups_info.append(workspace_group_dict)

        return WorkspaceGroupsResponse(
            results=workspace_groups_info, total_count=total_count
        )

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
