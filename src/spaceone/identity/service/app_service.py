import logging
from datetime import datetime, timedelta
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_app import *
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.client_secret_manager import ClientSecretManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.model.app.request import *
from spaceone.identity.model.app.response import *
from spaceone.identity.error.error_role import ERROR_NOT_ALLOWED_ROLE_TYPE

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class AppService(BaseService):
    resource = "App"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_mgr = AppManager()

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def create(self, params: AppCreateRequest) -> Union[AppResponse, dict]:
        """Create API Key
        Args:
            params (AppCreateRequest): {
                'name': 'str',              # required
                'role_id': 'str',           # required
                'tags': 'dict',
                'expired_at': 'str',
                'resource_group': 'str',    # required
                'project_id': 'str',
                'project_group_id': 'str',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
            }
        Return:
            AppResponse:
        """

        # Check role
        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(params.role_id, params.domain_id)

        # Check workspace and project
        if params.resource_group in ["WORKSPACE", "PROJECT"]:
            if params.workspace_id is None:
                raise ERROR_REQUIRED_PARAMETER(key="workspace_id")

            workspace_mgr = WorkspaceManager()
            workspace_mgr.get_workspace(params.workspace_id, params.domain_id)

            if params.resource_group == "PROJECT":
                if params.project_id and params.project_group_id:
                    raise ERROR_INVALID_PARAMETER(
                        key="project_id or project_group_id",
                        reason="Both are not allowed",
                    )
                elif params.project_group_id:
                    project_group_mgr = ProjectGroupManager()
                    project_group_mgr.get_project_group(
                        params.project_group_id, params.domain_id
                    )
                elif params.project_id:
                    project_mgr = ProjectManager()
                    project_mgr.get_project(params.project_id, params.domain_id)
                else:
                    raise ERROR_REQUIRED_PARAMETER(key="project_id or project_group_id")

        else:
            params.workspace_id = "*"

        # Check role type by resource_group
        if params.resource_group == "DOMAIN":
            if role_vo.role_type != "DOMAIN_ADMIN":
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=role_vo.role_id,
                    request_role_type=role_vo.role_type,
                    supported_role_type="DOMAIN_ADMIN",
                )
        elif params.resource_group == "WORKSPACE":
            if role_vo.role_type != "WORKSPACE_OWNER":
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=role_vo.role_id,
                    request_role_type=role_vo.role_type,
                    supported_role_type="WORKSPACE_OWNER",
                )
        else:
            if role_vo.role_type != "WORKSPACE_MEMBER":
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(
                    request_role_id=role_vo.role_id,
                    request_role_type=role_vo.role_type,
                    supported_role_type="WORKSPACE_MEMBER",
                )

        params.expired_at = self._get_expired_at(params.expired_at)
        self._check_expired_at(params.expired_at)

        params_data = params.dict()
        params_data["role_type"] = role_vo.role_type

        app_vo = self.app_mgr.create_app(params_data)

        client_secret_mgr = ClientSecretManager()
        client_id, client_secret = client_secret_mgr.generate_client_secret(
            app_vo.app_id,
            app_vo.domain_id,
            params.expired_at,
            app_vo.role_type,
            app_vo.workspace_id,
        )

        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        return AppResponse(**app_vo.to_dict(), client_secret=client_secret)

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def update(self, params: AppUpdateRequest) -> Union[AppResponse, dict]:
        """Update App
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        Return:
            AppResponse:
        """

        app_vo = self.app_mgr.get_app(
            params.app_id, params.domain_id, params.workspace_id
        )
        app_vo = self.app_mgr.update_app_by_vo(params.dict(exclude_unset=True), app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def generate_client_secret(
        self, params: AppGenerateAPIKeyRequest
    ) -> Union[AppResponse, dict]:
        """Generate API Key
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'expired_at': 'str',
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        Return:
            AppResponse:
        """

        params.expired_at = self._get_expired_at(params.expired_at)
        self._check_expired_at(params.expired_at)

        app_vo = self.app_mgr.get_app(
            params.app_id, params.domain_id, params.workspace_id
        )

        # Create new client secret
        client_secret_mgr = ClientSecretManager()
        client_id, client_secret = client_secret_mgr.generate_client_secret(
            app_vo.app_id,
            app_vo.domain_id,
            params.expired_at,
            app_vo.role_type,
            app_vo.workspace_id,
        )

        # Update app info
        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        return AppResponse(**app_vo.to_dict(), client_secret=client_secret)

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def enable(self, params: AppEnableRequest) -> Union[AppResponse, dict]:
        """Enable App Key
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.domain_id, params.workspace_id
        )
        app_vo = self.app_mgr.enable_app(app_vo)

        if app_vo.is_managed:
            raise ERROR_PERMISSION_DENIED(
                key="app_id", _message="Managed App cannot be enabled."
            )

        return AppResponse(**app_vo.to_dict())

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def disable(self, params: AppDisableRequest) -> Union[AppResponse, dict]:
        """Disable App Key
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.domain_id, params.workspace_id
        )
        app_vo = self.app_mgr.disable_app(app_vo)

        if app_vo.is_managed:
            raise ERROR_PERMISSION_DENIED(
                key="app_id", _message="Managed App cannot be disabled."
            )

        return AppResponse(**app_vo.to_dict())

    @transaction(
        permission="identity:App.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def delete(self, params: AppDeleteRequest) -> None:
        """Delete app
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            None
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.domain_id, params.workspace_id
        )

        if app_vo.is_managed:
            raise ERROR_PERMISSION_DENIED(
                key="app_id", _message="Managed App cannot be deleted."
            )

        self.app_mgr.delete_app_by_vo(app_vo)

    @transaction(
        permission="identity:App.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @convert_model
    def get(self, params: AppGetRequest) -> Union[AppResponse, dict]:
        """Get API Key
        Args:
            params (dict): {
                'app_id': 'str',            # required
                'workspace_id': 'list',     # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            AppResponse:
        """
        app_vo = self.app_mgr.get_app(
            params.app_id,
            params.domain_id,
            params.workspace_id,
        )
        return AppResponse(**app_vo.to_dict())

    @transaction(role_types=["INTERNAL"])
    @convert_model
    def check(self, params: AppCheckRequest) -> Union[CheckAppResponse, dict]:
        """Get API Key
        Args:
            params (dict): {
                'client_id': 'str',         # required
                'domain_id': 'str'          # required
            }
        Returns:
            None:
        """

        app_vos = self.app_mgr.filter_apps(
            client_id=params.client_id,
            domain_id=params.domain_id,
        )
        projects = []

        if app_vos.count() == 0:
            raise ERROR_PERMISSION_DENIED()

        app_vo = app_vos[0]
        if app_vo.state != "ENABLED":
            raise ERROR_PERMISSION_DENIED()

        domain_mgr = DomainManager()
        domain_vo = domain_mgr.get_domain(app_vo.domain_id)
        if domain_vo.state != "ENABLED":
            raise ERROR_PERMISSION_DENIED()

        if app_vo.role_type in ["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]:
            workspace_mgr = WorkspaceManager()
            workspace_vo = workspace_mgr.get_workspace(
                app_vo.workspace_id, app_vo.domain_id
            )
            if workspace_vo.state != "ENABLED":
                raise ERROR_PERMISSION_DENIED()

            if app_vo.project_group_id:
                project_group_mgr = ProjectGroupManager()
                project_group_vo = project_group_mgr.get_project_group(
                    app_vo.project_group_id, app_vo.domain_id
                )
                projects = project_group_mgr.get_projects_in_project_groups(
                    project_group_vo.domain_id, project_group_vo.project_group_id
                )

            elif app_vo.project_id:
                project_mgr = ProjectManager()
                project_vo = project_mgr.get_project(
                    app_vo.project_id, app_vo.domain_id
                )
                projects = [project_vo.project_id]

        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(app_vo.role_id, app_vo.domain_id)

        self.app_mgr.update_app_by_vo({"last_accessed_at": datetime.utcnow()}, app_vo)

        return CheckAppResponse(permissions=role_vo.permissions, projects=projects)

    @transaction(
        permission="identity:App.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @append_query_filter(
        [
            "app_id",
            "name",
            "state",
            "role_type",
            "role_id",
            "client_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["app_id", "name"])
    @convert_model
    def list(self, params: AppSearchQueryRequest) -> Union[AppsResponse, dict]:
        """List Apps
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'app_id': 'str',
                'name': 'str',
                'state': 'str',
                'role_type': 'str',
                'role_id': 'str',
                'client_id': 'str',
                'workspace_id': 'str'       # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            AppsResponse:
        """
        query = params.query or {}
        app_vos, total_count = self.app_mgr.list_apps(query)
        apps_info = [app_vo.to_dict() for app_vo in app_vos]
        return AppsResponse(results=apps_info, total_count=total_count)

    @transaction(
        permission="identity:App.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER"],
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["app_id", "name"])
    @convert_model
    def stat(self, params: AppStatQueryRequest) -> dict:
        """Stat API Keys
        Args:
            params (dict): {
                'query': 'dict',            # required
                'workspace_id': 'list',     # injected from auth
                'domain_id': 'str'          # injected from auth (required)
            }
            Returns:
                dict:
        """
        query = params.query or {}
        return self.app_mgr.stat_apps(query)

    @staticmethod
    def _get_expired_at(expired_at: str) -> str:
        if expired_at:
            return expired_at
        else:
            return (datetime.utcnow() + timedelta(days=365)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    @staticmethod
    def _check_expired_at(expired_at: str) -> None:
        one_year_later = datetime.utcnow() + timedelta(days=365)

        if one_year_later.strftime("%Y-%m-%d %H:%M:%S") < expired_at:
            raise ERROR_APP_EXPIRED_LIMIT(expired_at=expired_at)
