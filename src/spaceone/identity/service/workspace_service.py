import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.resource_manager import ResourceManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.workspace.request import *
from spaceone.identity.model.workspace.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceService(BaseService):
    resource = "Workspace"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.resource_mgr = ResourceManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(permission="identity:Workspace.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def create(self, params: WorkspaceCreateRequest) -> Union[WorkspaceResponse, dict]:
        """Create workspace
        Args:
            params (WorkspaceCreateRequest): {
                'name': 'str',          # required
                'tags': 'dict',
                'domain_id': 'str',     # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """

        params_data = params.dict()
        params_data["created_by"] = self.transaction.get_meta("authorization.user_id")

        workspace_vo = self.workspace_mgr.create_workspace(params_data)

        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(permission="identity:Workspace.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def update(self, params: WorkspaceUpdateRequest) -> Union[WorkspaceResponse, dict]:
        """Update workspace
        Args:
            params (WorkspaceUpdateRequest): {
                'workspace_id': 'str',  # required
                'name': 'str',
                'tags': 'dict'
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(workspace_vo)

        workspace_vo = self.workspace_mgr.update_workspace_by_vo(
            params.dict(exclude_unset=True), workspace_vo
        )
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(permission="identity:Workspace.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def delete(self, params: WorkspaceDeleteRequest) -> None:
        """Delete workspace
        Args:
            params (WorkspaceDeleteRequest): {
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            None
        """

        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(workspace_vo)

        self.workspace_mgr.delete_workspace_by_vo(workspace_vo)

    @transaction(permission="identity:Workspace.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def enable(self, params: WorkspaceEnableRequest) -> Union[WorkspaceResponse, dict]:
        """Enable workspace
        Args:
            params (WorkspaceEnableRequest): {
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(workspace_vo)

        workspace_vo = self.workspace_mgr.enable_workspace(workspace_vo)
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(permission="identity:Workspace.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def disable(
            self, params: WorkspaceDisableRequest
    ) -> Union[WorkspaceResponse, dict]:
        """Disable workspace
        Args:
            params (WorkspaceDisableRequest): {
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """

        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(workspace_vo)

        workspace_vo = self.workspace_mgr.disable_workspace(workspace_vo)
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(permission="identity:Workspace.read", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def get(self, params: WorkspaceGetRequest) -> Union[WorkspaceResponse, dict]:
        """Get workspace
        Args:
            params (WorkspaceGetRequest): {
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """

        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(role_types=["INTERNAL"])
    @convert_model
    def check(self, params: WorkspaceCheckRequest) -> None:
        """Check workspace
        Args:
            params (WorkspaceCheckRequest): {
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # required
            }
        Returns:
            None:
        """

        self.workspace_mgr.get_workspace(params.workspace_id, params.domain_id)

    @transaction(permission="identity:Workspace.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(["workspace_id", "name", "created_by", "domain_id"])
    @append_keyword_filter(["workspace_id", "name"])
    @convert_model
    def list(
            self, params: WorkspaceSearchQueryRequest
    ) -> Union[WorkspacesResponse, dict]:
        """List workspaces
        Args:
            params (WorkspaceSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'name': 'str',
                'workspace_id': 'str',
                'created_by': 'str',
                'domain_id': 'str',         # injected from auth (required)
            }
        Returns:
            WorkspacesResponse:
        """

        query = params.query or {}
        workspace_vos, total_count = self.workspace_mgr.list_workspaces(query)

        workspaces_info = [workspace_vo.to_dict() for workspace_vo in workspace_vos]
        return WorkspacesResponse(results=workspaces_info, total_count=total_count)

    @transaction(permission="identity:Workspace.read", role_types=["DOMAIN_ADMIN"])
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["workspace_id", "name"])
    @convert_model
    def stat(self, params: WorkspaceStatQueryRequest) -> dict:
        """Stat workspaces
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.workspace_mgr.stat_workspaces(query)
