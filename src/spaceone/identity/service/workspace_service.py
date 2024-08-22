import logging
from typing import Union

from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager import SecretManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.resource_manager import ResourceManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model import Workspace
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
        self.service_account_mgr = ServiceAccountManager()

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
        self.resource_mgr.check_is_managed_resource_by_trusted_account(workspace_vo)

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
                'force': 'bool',
                'workspace_id': 'str',  # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            None
        """

        domain_id = params.domain_id
        workspace_id = params.workspace_id

        workspace_vo = self.workspace_mgr.get_workspace(workspace_id, domain_id)

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource_by_trusted_account(workspace_vo)

        service_account_vos = self.service_account_mgr.filter_service_accounts(
            domain_id=domain_id, workspace_id=workspace_id
        )

        if params.force:
            self._delete_related_resources_in_workspace(workspace_vo)
        elif len(service_account_vos) > 0:
            raise ERROR_UNKNOWN(
                message=f"Please delete service accounts in workspace ({workspace_id})"
            )
        else:
            self._delete_related_resources_in_workspace(workspace_vo)

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
        self.resource_mgr.check_is_managed_resource_by_trusted_account(workspace_vo)

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
        self.resource_mgr.check_is_managed_resource_by_trusted_account(workspace_vo)

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
    @append_query_filter(
        [
            "workspace_id",
            "name",
            "state",
            "created_by",
            "is_managed",
            "is_dormant",
            "domain_id",
        ]
    )
    @append_keyword_filter(["workspace_id", "name"])
    @convert_model
    def list(
        self, params: WorkspaceSearchQueryRequest
    ) -> Union[WorkspacesResponse, dict]:
        """List workspaces
        Args:
            params (WorkspaceSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'workspace_id': 'str',
                'name': 'str',
                'state': 'str',
                'created_by': 'str',
                'is_managed': 'bool',
                'is_dormant': 'bool',
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

    @staticmethod
    def _delete_related_resources_in_workspace(workspace_vo: Workspace):
        project_group_mgr = ProjectGroupManager()
        project_mgr = ProjectManager()
        trusted_account_mgr = TrustedAccountManager()
        service_account_mgr = ServiceAccountManager()
        secret_mgr = SecretManager()
        workspace_group_mgr = WorkspaceGroupManager()

        project_group_vos = project_group_mgr.filter_project_groups(
            domain_id=workspace_vo.domain_id, workspace_id=workspace_vo.workspace_id
        )

        project_vos = project_mgr.filter_projects(
            domain_id=workspace_vo.domain_id, workspace_id=workspace_vo.workspace_id
        )

        trusted_account_vos = trusted_account_mgr.filter_trusted_accounts(
            domain_id=workspace_vo.domain_id, workspace_id=workspace_vo.workspace_id
        )

        service_account_vos = service_account_mgr.filter_service_accounts(
            domain_id=workspace_vo.domain_id, workspace_id=workspace_vo.workspace_id
        )

        workspace_group_vos = workspace_group_mgr.filter_workspace_groups(
            domain_id=workspace_vo.domain_id, workspaces=workspace_vo.workspace_id
        )

        _LOGGER.debug(
            f"[_delete_related_resources_in_workspace] Start delete related resources in workspace: {workspace_vo.domain_id} {workspace_vo.name}( {workspace_vo.workspace_id} )"
        )

        if project_group_vos:
            _LOGGER.debug(
                f"[_delete_related_resources_in_workspace] Delete project groups count {workspace_vo.workspace_id} : {project_group_vos.count()}"
            )
            project_group_vos.delete()

        if project_vos:
            _LOGGER.debug(
                f"[_delete_related_resources_in_workspace] Delete projects count  {workspace_vo.workspace_id} : {project_vos.count()}"
            )
            project_vos.delete()

        for service_account_vo in service_account_vos:
            secret_mgr.delete_related_secrets(service_account_vo.service_account_id)
            _LOGGER.debug(
                f"[_delete_related_resources_in_workspace] Delete service account: {service_account_vo.name} ({service_account_vo.service_account_id})"
            )
            service_account_mgr.delete_service_account_by_vo(service_account_vo)

        for trusted_account_vo in trusted_account_vos:
            secret_mgr.delete_related_trusted_secrets(
                trusted_account_vo.trusted_account_id
            )
            _LOGGER.debug(
                f"[_delete_related_resources_in_workspace] Delete trusted account: {trusted_account_vo.name} ({trusted_account_vo.trusted_account_id})"
            )
            trusted_account_mgr.delete_trusted_account_by_vo(trusted_account_vo)

        for workspace_group_vo in workspace_group_vos:
            workspaces: list = workspace_group_vo.workspaces

            workspaces.remove(workspace_vo.workspace_id)
            workspace_group_mgr.update_workspace_group_by_vo(
                params={"workspaces": workspaces},
                workspace_group_vo=workspace_group_vo,
            )
            _LOGGER.debug(
                f"[_delete_related_resources_in_workspace] Delete workspace group: {workspace_group_vo.name} ({workspace_group_vo.workspace_group_id})"
            )
