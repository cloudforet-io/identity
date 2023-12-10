import logging
from datetime import datetime, timedelta
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_api_key import *
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.api_key_manager import APIKeyManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.app.request import *
from spaceone.identity.model.app.response import *

_LOGGER = logging.getLogger(__name__)


class AppService(BaseService):
    service = "identity"
    resource = "App"
    permission_group = "COMPOUND"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_mgr = AppManager()

    @transaction(scope="workspace_owner:write")
    @convert_model
    def create(self, params: AppCreateRequest) -> Union[AppResponse, dict]:
        """Create API Key
        Args:
            params (AppCreateRequest): {
                'name': 'str',              # required
                'role_id': 'str',           # required
                'tags': 'dict',
                'expired_at': 'str',
                'permission_group': 'str',  # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
            }
        Return:
            AppResponse:
        """
        params.expired_at = self._get_expired_at(params.expired_at)
        self._check_expired_at(params.expired_at)

        # Check workspace
        if params.permission_group == "WORKSPACE":
            workspace_mgr = WorkspaceManager()
            workspace_mgr.get_workspace(params.workspace_id, params.domain_id)
        else:
            params.workspace_id = "*"

        app_vo = self.app_mgr.create_app(params.dict())

        api_key_mgr = APIKeyManager()
        api_key_vo, api_key = api_key_mgr.create_api_key_by_app_vo(
            app_vo, params.dict()
        )

        app_vo = self.app_mgr.update_app_by_vo(
            {"api_key_id": api_key_vo.api_key_id}, app_vo
        )

        return AppResponse(**app_vo.to_dict(), api_key=api_key)

    @transaction(scope="workspace_owner:write")
    @convert_model
    def update(self, params: AppUpdateRequest) -> Union[AppResponse, dict]:
        """Update App
        Args:
            params (dict): {
                'app_id': 'str', # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Return:
            AppResponse:
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )
        app_vo = self.app_mgr.update_app_by_vo(params.dict(exclude_unset=True), app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(scope="workspace_owner:write")
    @convert_model
    def generate_api_key(
        self, params: AppGenerateAPIKeyRequest
    ) -> Union[AppResponse, dict]:
        """Generate API Key
        Args:
            params (dict): {
                'app_id': 'str', # required
                'expired_at': 'str',
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Return:
            AppResponse:
        """

        params.expired_at = params.expired_at or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self._check_expired_at(params.expired_at)

        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )

        # Create new api_key
        api_key_mgr = APIKeyManager()
        api_key_vo, api_key = api_key_mgr.create_api_key_by_app_vo(
            app_vo, params.dict()
        )

        # Delete previous api_key
        api_key_vo = api_key_mgr.get_api_key(
            app_vo.api_key_id, params.domain_id, owner_type="APP"
        )
        api_key_mgr.delete_api_key_by_vo(api_key_vo)

        # Update app info
        app_vo = self.app_mgr.update_app_by_vo(
            {"api_key_id": api_key_vo.api_key_id}, app_vo
        )

        return AppResponse(**app_vo.to_dict(), api_key=api_key)

    @transaction(scope="workspace_owner:write")
    @convert_model
    def enable(self, params: AppEnableRequest) -> Union[AppResponse, dict]:
        """Enable App Key
        Args:
            params (dict): {
                'app_id': 'str', # required
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )
        app_vo = self.app_mgr.enable_app(app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(scope="workspace_owner:write")
    @convert_model
    def disable(self, params: AppDisableRequest) -> Union[AppResponse, dict]:
        """Disable App Key
        Args:
            params (dict): {
                'app_id': 'str', # required
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )
        app_vo = self.app_mgr.disable_app(app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(scope="workspace_owner:write")
    @convert_model
    def delete(self, params: AppDeleteRequest) -> None:
        """Delete app
        Args:
            params (dict): {
                'api_key_id': 'str', # required
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Returns:
            None
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )
        self.app_mgr.delete_app_by_vo(app_vo)

    @transaction(scope="workspace_owner:read")
    @convert_model
    def get(self, params: AppGetRequest) -> Union[AppResponse, dict]:
        """Get API Key
        Args:
            params (dict): {
                'app_id': 'str', # required
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Returns:
            AppResponse:
        """
        app_vo = self.app_mgr.get_app(
            params.app_id, params.workspace_id, params.domain_id
        )
        return AppResponse(**app_vo.to_dict())

    @transaction(scope="workspace_owner:read")
    @append_query_filter(
        [
            "app_id",
            "name",
            "state",
            "role_type",
            "role_id",
            "api_key_id",
            "permission_group",
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
                'api_key_id': 'str',
                'permission_group': 'str',
                'workspace_id': 'str',
                'domain_id': 'str' # required
            }
        Returns:
            AppsResponse:
        """
        query = params.query or {}
        app_vos, total_count = self.app_mgr.list_apps(query)
        apps_info = [app_vo.to_dict() for app_vo in app_vos]
        return AppsResponse(results=apps_info, total_count=total_count)

    @transaction(scope="workspace_owner:read")
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["app_id", "name"])
    @convert_model
    def stat(self, params: AppStatQueryRequest) -> dict:
        """Stat API Keys
        Args:
            params (dict): {
                'query': 'dict', # required
                'workspace_id': 'str',
                'domain_id': 'str' # required
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
            return (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _check_expired_at(expired_at: str) -> None:
        one_year_later = datetime.now() + timedelta(days=365)

        if one_year_later.strftime("%Y-%m-%d %H:%M:%S") < expired_at:
            raise ERROR_API_KEY_EXPIRED_LIMIT(expired_at=expired_at)
