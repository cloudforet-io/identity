import logging
from typing import Union

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.workspace.request import *
from spaceone.identity.model.workspace.response import *

_LOGGER = logging.getLogger(__name__)


class WorkspaceService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.workspace_mgr = WorkspaceManager()

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def create(self, params: WorkspaceCreateRequest) -> Union[WorkspaceResponse, dict]:
        """Create workspace
        Args:
            params (dict): {
                'name': 'str', # required
                'tags': 'dict', # required
                'domain_id': 'str' # required
            }
        Returns:
            WorkspaceResponse:
        """

        workspace_vo = self.workspace_mgr.create_workspace(params.dict())

        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def update(self, params: WorkspaceUpdateRequest) -> Union[WorkspaceResponse, dict]:
        """Update workspace
        Args:
            params (dict): {
                'workspace_id': 'str', # required
                'name': 'str',
                'tags': 'dict'
                'domain_id': 'str' # required
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        workspace_vo = self.workspace_mgr.update_workspace_by_vo(
            params.dict(), workspace_vo
        )
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def delete(self, params: WorkspaceDeleteRequest) -> None:
        """Delete workspace
        Args:
            params (dict): {
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            None
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        self.workspace_mgr.delete_workspace_by_vo(workspace_vo)

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def enable(self, params: WorkspaceEnableRequest) -> Union[WorkspaceResponse, dict]:
        """Enable workspace
        Args:
            params (dict): {
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        workspace_vo = self.workspace_mgr.enable_workspace(workspace_vo)
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE"})
    @convert_model
    def disable(
        self, params: WorkspaceDisableRequest
    ) -> Union[WorkspaceResponse, dict]:
        """Disable workspace
        Args:
            params (dict): {
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            WorkspaceResponse:
        """

        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        workspace_vo = self.workspace_mgr.disable_workspace(workspace_vo)
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE_READ"})
    @convert_model
    def get(self, params: WorkspaceGetRequest) -> Union[WorkspaceResponse, dict]:
        """Get workspace
        Args:
            params (dict): {
                'workspace_id': 'str', # required
                'domain_id': 'str' # required
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_vo = self.workspace_mgr.get_workspace(
            params.workspace_id, params.domain_id
        )
        return WorkspaceResponse(**workspace_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "WORKSPACE_READ"})
    @append_query_filter(["workspace_id", "name", "domain_id"])
    @append_keyword_filter(["workspace_id", "name"])
    @convert_model
    def list(
        self, params: WorkspaceSearchQueryRequest
    ) -> Union[WorkspacesResponse, dict]:
        """List workspace
        Args:
            params (dict): {
                'query': 'dict',
                'name': 'str',
                'workspace_id': 'str',
                'domain_id': 'str' #required
            }
        Returns:
            WorkspacesResponse:
        """
        query = params.query or {}

        workspace_vos, total_count = self.workspace_mgr.list_workspaces(query)
        workspaces_info = [workspace_vo.to_dict() for workspace_vo in workspace_vos]
        return WorkspacesResponse(results=workspaces_info, total_count=total_count)

    @transaction(append_meta={"authorization.scope": "WORKSPACE_READ"})
    @convert_model
    def stat(self, params: WorkspaceStatQueryRequest) -> dict:
        return {}
