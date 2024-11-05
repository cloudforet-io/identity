import logging
from datetime import datetime
from typing import Dict, List, Union

from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager import SecretManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.resource_manager import ResourceManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.workspace_group_manager import WorkspaceGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model import Workspace
from spaceone.identity.model.workspace.request import *
from spaceone.identity.model.workspace.response import *
from spaceone.identity.service.role_binding_service import RoleBindingService

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
        self.rb_mgr = RoleBindingManager()
        self.workspace_group_mgr = WorkspaceGroupManager()

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
    def change_workspace_group(
        self, params: WorkspaceChangeWorkspaceGroupRequest
    ) -> Union[WorkspaceResponse, dict]:
        """Change workspace group
        Args:
            params (WorkspaceChangeWorkspaceGroupRequest): {
                'workspace_id': 'str',                   # required
                'workspace_group_id': 'str',
                'domain_id': 'str'                       # injected from auth (required)
            }
        Returns:
            WorkspaceResponse:
        """
        workspace_id = params.workspace_id
        new_workspace_group_id = params.workspace_group_id
        domain_id = params.domain_id

        workspace_vo = self.workspace_mgr.get_workspace(
            workspace_id=params.workspace_id, domain_id=domain_id
        )

        old_workspace_group_id = workspace_vo.workspace_group_id
        is_updatable = True
        workspace_group_vo = None
        if new_workspace_group_id:
            workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
                domain_id, new_workspace_group_id
            )
            is_updatable = self._add_workspace_to_group(
                workspace_id, new_workspace_group_id, domain_id
            )
        elif old_workspace_group_id:
            workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
                domain_id, old_workspace_group_id
            )
            self._remove_workspace_from_group_with_workspace_vo(
                workspace_vo, old_workspace_group_id, domain_id
            )

        if is_updatable:
            workspace_vo = self.workspace_mgr.update_workspace_by_vo(
                params.dict(exclude_unset=False), workspace_vo
            )

            if new_workspace_group_id:
                workspace_vos = self.workspace_mgr.filter_workspaces(
                    workspace_group_id=new_workspace_group_id, domain_id=domain_id
                )

                self.workspace_group_mgr.update_workspace_group_by_vo(
                    {"workspace_count": len(workspace_vos)}, workspace_group_vo
                )
            if old_workspace_group_id:
                workspace_vos = self.workspace_mgr.filter_workspaces(
                    workspace_group_id=old_workspace_group_id, domain_id=domain_id
                )

                workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
                    domain_id, old_workspace_group_id
                )

                self.workspace_group_mgr.update_workspace_group_by_vo(
                    {"workspace_count": len(workspace_vos)}, workspace_group_vo
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
                'workspace_group_id': 'str',
                'domain_id': 'str',         # injected from auth (required)
            }
        Returns:
            WorkspacesResponse:
        """

        query = params.query or {}
        workspace_group_id = params.workspace_group_id

        if not workspace_group_id:
            workspace_vos, total_count = self.workspace_mgr.list_workspaces(query)

            workspaces_info = [workspace_vo.to_dict() for workspace_vo in workspace_vos]
        else:
            workspaces_info, total_count = (
                self.workspace_mgr.list_workspace_group_workspaces(
                    params.workspace_group_id,
                    params.domain_id,
                )
            )

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

    def _add_workspace_to_group(
        self, workspace_id: str, workspace_group_id: str, domain_id: str
    ) -> bool:
        workspace_vo = self.workspace_mgr.get_workspace(
            workspace_id=workspace_id, domain_id=domain_id
        )
        old_workspace_group_id = workspace_vo.workspace_group_id
        is_updatable = True

        workspace_group_vo = self.workspace_group_mgr.get_workspace_group(
            domain_id, workspace_group_id
        )

        if old_workspace_group_id:
            if old_workspace_group_id != workspace_group_id:
                self._delete_role_bindings(
                    workspace_id, domain_id, old_workspace_group_id
                )

                self._create_role_bindings(
                    workspace_group_vo.users,
                    workspace_id,
                    workspace_group_id,
                    domain_id,
                )

                workspaces_info, total_count = (
                    self.workspace_mgr.list_workspace_group_workspaces(
                        old_workspace_group_id,
                        domain_id,
                    )
                )
                for workspace_info in workspaces_info:
                    workspace_vo = self.workspace_mgr.get_workspace(
                        workspace_info["workspace_id"], domain_id
                    )
                    user_rb_ids = self.rb_mgr.stat_role_bindings(
                        query={
                            "distinct": "user_id",
                            "filter": [
                                {
                                    "k": "workspace_id",
                                    "v": workspace_info["workspace_id"],
                                    "o": "eq",
                                },
                                {"k": "domain_id", "v": domain_id, "o": "eq"},
                            ],
                        }
                    ).get("results", [])
                    user_rb_total_count = len(user_rb_ids)

                    workspace_vo = self.workspace_mgr.update_workspace_by_vo(
                        {"user_count": user_rb_total_count}, workspace_vo
                    )
                    workspace_info.update({"user_count": workspace_vo.user_count})
            else:
                is_updatable = False
        else:
            workspace_group_dict = workspace_group_vo.to_dict()
            users = workspace_group_dict.get("users", []) or []
            user_ids = [user.get("user_id") for user in users]
            self._delete_role_bindings(workspace_id, domain_id, user_ids=user_ids)
            self._create_role_bindings(
                workspace_group_vo.users,
                workspace_id,
                workspace_group_id,
                domain_id,
            )

        if is_updatable:
            workspace_vo.changed_at = datetime.utcnow()
            self.workspace_mgr.update_workspace_by_vo(
                {"changed_at": workspace_vo.changed_at}, workspace_vo
            )

        return is_updatable

    def _remove_workspace_from_group_with_workspace_vo(
        self, workspace_vo: Workspace, old_workspace_group_id: str, domain_id: str
    ) -> None:
        workspace_id = workspace_vo.workspace_id

        workspace_vo.changed_at = datetime.utcnow()
        workspace_vo.workspace_group_id = None

        user_rb_ids = self.rb_mgr.stat_role_bindings(
            query={
                "distinct": "user_id",
                "filter": [
                    {"k": "workspace_id", "v": workspace_id, "o": "eq"},
                    {"k": "domain_id", "v": domain_id, "o": "eq"},
                ],
            }
        ).get("results", [])
        self._delete_role_bindings(
            workspace_id, domain_id, old_workspace_group_id, user_rb_ids
        )
        user_rb_total_count = len(user_rb_ids)

        self.workspace_mgr.update_workspace_by_vo(
            {
                "user_count": user_rb_total_count,
                "changed_at": workspace_vo.changed_at,
                "workspace_group_id": None,
            },
            workspace_vo,
        )

    def _delete_role_bindings(
        self,
        workspace_id: str,
        domain_id: str,
        existing_workspace_group_id: str = None,
        user_ids: List[str] = None,
    ):
        rb_vos = self.rb_mgr.filter_role_bindings(
            workspace_id=workspace_id,
            domain_id=domain_id,
            workspace_group_id=existing_workspace_group_id,
            user_id=user_ids,
        )
        for rb_vo in rb_vos:
            self.rb_mgr.delete_role_binding_by_vo(rb_vo)

    @staticmethod
    def _create_role_bindings(
        workspace_group_users: List[Dict[str, str]],
        workspace_id: str,
        workspace_group_id: str,
        domain_id: str,
    ):
        rb_svc = RoleBindingService()
        for user_info in workspace_group_users or []:
            rb_svc.create_role_binding(
                {
                    "user_id": user_info["user_id"],
                    "role_id": user_info["role_id"],
                    "resource_group": "WORKSPACE",
                    "domain_id": domain_id,
                    "workspace_group_id": workspace_group_id,
                    "workspace_id": workspace_id,
                }
            )
