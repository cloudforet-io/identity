from typing import Union

from spaceone.core.service import (
    BaseService,
    authentication_handler,
    authorization_handler,
    event_handler,
    mutation_handler,
    transaction,
)
from spaceone.core.service.utils import convert_model

from spaceone.identity.model.workspace_group_details.request import (
    WorkspaceGroupDetailsAddUsersRequest,
    WorkspaceGroupDetailsAddWorkspacesRequest,
    WorkspaceGroupDetailsDeleteRequest,
    WorkspaceGroupDetailsFindRequest,
    WorkspaceGroupDetailsGetWorkspaceGroupsRequest,
    WorkspaceGroupDetailsRemoveUsersRequest,
    WorkspaceGroupDetailsRemoveWorkspacesRequest,
    WorkspaceGroupDetailsUpdateRequest,
)
from spaceone.identity.model.workspace_group_details.response import (
    WorkspaceGroupDetailsResponse,
    WorkspaceGroupDetailsUsersSummaryResponse,
    WorkspaceGroupsDetailsResponse,
)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceGroupDetailsService(BaseService):
    resource = "WorkspaceGroupDetails"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def update(
        self, params: WorkspaceGroupDetailsUpdateRequest
    ) -> Union[WorkspaceGroupDetailsResponse, dict]:
        """Update workspace group details
        Args:
            params (WorkspaceGroupDetailsUpdateRequest): {
                'workspace_group_id': 'str',           # required
                'name': 'str',
                'tags': 'dict',
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
           WorkspaceGroupDetailsResponse:
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def delete(self, params: WorkspaceGroupDetailsDeleteRequest) -> None:
        """Delete workspace group details
        Args:
            params (dict): {
                'workspace_group_id': 'str',           # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            None
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def add_workspaces(
        self, params: WorkspaceGroupDetailsAddWorkspacesRequest
    ) -> Union[WorkspaceGroupDetailsResponse, dict]:
        """Add workspaces to workspace group
        Args:
            params (dict): {
                'workspace_group_id': 'str',           # required
                'workspaces': 'list',                  # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupDetailsResponse:
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def remove_workspaces(
        self, params: WorkspaceGroupDetailsRemoveWorkspacesRequest
    ) -> Union[WorkspaceGroupDetailsResponse, dict]:
        """Remove workspaces from workspace group
        Args:
            params (dict): {
                'workspace_group_id': 'str',           # required
                'workspaces': 'list',                  # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupDetailsResponse:
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:read", role_types=["USER"])
    @convert_model
    def find_users(
        self, params: WorkspaceGroupDetailsFindRequest
    ) -> Union[WorkspaceGroupDetailsUsersSummaryResponse, dict]:
        """Find users in the domain except users in its workspace_group
        Args:
            params (WorkspaceGroupFindRequest): {
                'workspace_group_id': 'str',           # required
                'keyword': 'str',
                'state': 'State',
                'page': 'dict',
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupDetailsUsersSummaryResponse:
        """

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def add_users(
        self, params: WorkspaceGroupDetailsAddUsersRequest
    ) -> Union[WorkspaceGroupDetailsResponse, dict]:
        """Add users to workspace group
        Args:
            params (dict): {
                'workspace_group_id': 'str',           # required
                'users': 'list',                       # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupDetailsResponse:
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:write", role_types=["USER"])
    @convert_model
    def remove_users(
        self, params: WorkspaceGroupDetailsRemoveUsersRequest
    ) -> Union[WorkspaceGroupDetailsResponse, dict]:
        """Remove users from workspace group
        Args:
            params (dict): {
                'workspace_group_id': 'str',           # required
                'users': 'list',                       # required
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupDetailsResponse:
        """
        pass

    @transaction(permission="identity:WorkspaceGroupDetails:read", role_types=["USER"])
    @convert_model
    def get_workspace_groups(
        self, params: WorkspaceGroupDetailsGetWorkspaceGroupsRequest
    ) -> Union[WorkspaceGroupsDetailsResponse, dict]:
        """Get workspace groups
        Args:
            params (dict): {
                'user_id': 'str'                       # injected from auth (required)
                'domain_id': 'str',                    # injected from auth (required)
            }
        Returns:
            WorkspaceGroupsDetailsResponse:
        """
        pass
