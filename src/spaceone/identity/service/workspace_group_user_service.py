from typing import Union

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

from spaceone.identity.model.workspace_group.response import (
    WorkspaceGroupUsersSummaryResponse,
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
    WorkspaceGroupUserResponse,
    WorkspaceGroupUsersResponse,
)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceGroupUserService(BaseService):
    resource = "WorkspaceGroupUser"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        pass

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
        pass

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
                'user_id': 'str',                       # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
            }
        Returns:
            WorkspaceGroupUserResponse:
        """
        pass

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
        pass

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
        pass

    @transaction(permission="identity:WorkspaceGroup.read", role_types=["USER"])
    @append_query_filter(["user_id", "workspace_group_id", "domain_id"])
    @convert_model
    def stat(self, params: WorkspaceGroupUserStatQueryRequest) -> dict:
        """Stat workspace group users
        Args:
            params (WorkspaceGroupUserStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'user_id': 'str'                         # injected from auth (required)
                'domain_id': 'str',                      # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        pass
