import logging
from datetime import datetime, timedelta
from typing import Union, Tuple

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.core.error import *

from spaceone.identity.error.custom import *
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.client_secret_manager import ClientSecretManager
from spaceone.identity.model import App
from spaceone.identity.model.app.response import AppResponse
from spaceone.identity.model.service_account.request import *
from spaceone.identity.model.service_account.response import *
from spaceone.identity.manager.schema_manager import SchemaManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.secret_manager import SecretManager
from spaceone.identity.manager.resource_manager import ResourceManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ServiceAccountService(BaseService):
    resource = "ServiceAccount"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_account_mgr = ServiceAccountManager()
        self.app_mgr = AppManager()
        self.resource_mgr = ResourceManager()

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def create(
        self, params: ServiceAccountCreateRequest
    ) -> Union[ServiceAccountResponse, dict]:
        """create service account

         Args:
            params (ServiceAccountCreateRequest): {
                'name': 'str',                          # required
                'data': 'dict',                         # required
                'provider': 'str',                      # required
                'secret_schema_id': 'str',
                'secret_data': 'dict',
                'trusted_account_id': 'str',
                'tags': 'dict',
                'project_id': 'str',                    # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str'                      # injected from auth (required)
            }

        Returns:
            ServiceAccountResponse:
        """

        # Check data by schema
        schema_mgr = SchemaManager()
        schema_mgr.validate_data_by_schema(
            params.provider, params.domain_id, "SERVICE_ACCOUNT", params.data
        )

        # Check project
        project_mgr = ProjectManager()
        project_mgr.get_project(
            params.project_id, params.domain_id, params.workspace_id
        )

        # Check trusted service account
        if params.trusted_account_id and params.secret_data:
            trusted_account_mgr = TrustedAccountManager()

            # Append wildcard to workspace_id for DOMAIN trusted account
            workspace_id = [params.workspace_id, "*"]

            trusted_account_vo = trusted_account_mgr.get_trusted_account(
                params.trusted_account_id,
                params.domain_id,
                workspace_id,
            )
            secret_type = "TRUSTING_SECRET"
        else:
            trusted_account_vo = None
            params.trusted_account_id = None
            secret_type = "SECRET"

        service_account_vo = self.service_account_mgr.create_service_account(
            params.dict()
        )

        if params.secret_data:
            if params.secret_schema_id is None:
                raise ERROR_REQUIRED_PARAMETER(key="secret_schema_id")

            # Check secret_data by schema
            schema_mgr.validate_secret_data_by_schema_id(
                params.secret_schema_id,
                params.domain_id,
                params.secret_data,
                secret_type,
            )

            # Create a secret
            secret_mgr = self.locator.get_manager("SecretManager")
            create_secret_params = {
                "name": f"{service_account_vo.service_account_id}-secret",
                "data": params.secret_data,
                "schema_id": params.secret_schema_id,
                "service_account_id": service_account_vo.service_account_id,
                "resource_group": "PROJECT",
            }

            if trusted_account_vo:
                create_secret_params[
                    "trusted_secret_id"
                ] = trusted_account_vo.trusted_secret_id

            domain_id = params.domain_id
            secret_info = secret_mgr.create_secret(create_secret_params, domain_id)

            # Update secret_id in service_account_vo
            service_account_vo = self.service_account_mgr.update_service_account_by_vo(
                {"secret_id": secret_info["secret_id"]}, service_account_vo
            )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def create_app(
        self, params: ServiceAccountCreateAppRequest
    ) -> Union[AppResponse, dict]:
        """create app created by service account

         Args:
            params (ServiceAccountCreateAppRequest): {
                'service_account_id': 'str',            # required
                'options': 'dict',
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AppResponse:
        """
        resource_group = "WORKSPACE"
        service_account_id = params.service_account_id
        options = params.options or {}
        workspace_id = params.workspace_id
        domain_id = params.domain_id
        users_project = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id, domain_id, workspace_id, users_project
        )

        if service_account_vo.app_id:
            raise ERROR_EXIST_RESOURCE(
                key="app_id",
                value=service_account_vo.app_id,
                message="Please delete the existing app first.",
            )

        params_data = {
            "name": f"{service_account_vo.name} agent app",
            "role_id": "managed-workspace-owner",
            "role_type": "WORKSPACE_OWNER",
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "resource_group": resource_group,
            "service_account_id": service_account_id,
            "is_managed": True,
            "expired_at": self._get_expired_at(),
        }

        app_vo = self.app_mgr.create_app(params_data)

        client_id, client_secret = self._create_service_account_app_client_secret(
            app_vo, service_account_id
        )

        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        self.service_account_mgr.update_service_account_by_vo(
            {"app_id": app_vo.app_id, "options": options}, service_account_vo
        )

        return AppResponse(**app_vo.to_dict(), client_secret=client_secret)

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def update(
        self, params: ServiceAccountUpdateRequest
    ) -> Union[ServiceAccountResponse, dict]:
        """update service account

         Args:
            params (ServiceAccountUpdateRequest): {
                'service_account_id': 'str',        # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'project_id': 'str',
                'workspace_id': 'str',              # injected from auth (required)
                'domain_id': 'str',                 # injected from auth (required)
                'user_projects': 'list'             # injected from auth
            }

        Returns:
            ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(service_account_vo)

        if params.data:
            # Check data by schema
            schema_mgr = SchemaManager()
            schema_mgr.validate_data_by_schema(
                service_account_vo.provider,
                params.domain_id,
                "SERVICE_ACCOUNT",
                params.data,
            )

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(
            params.dict(exclude_unset=True), service_account_vo
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def update_secret_data(
        self, params: ServiceAccountUpdateSecretRequest
    ) -> Union[ServiceAccountResponse, dict]:
        """update service account secret data

         Args:
            params (ServiceAccountUpdateSecretRequest): {
                'service_account_id': 'str',        # required
                'secret_schema_id': 'str',          # required
                'secret_data': 'dict',              # required
                'trusted_account_id': 'str',
                'workspace_id': 'str',              # injected from auth (required)
                'domain_id': 'str',                 # injected from auth (required)
                'user_projects': 'list'             # injected from auth
            }

        Returns:
            ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        if params.trusted_account_id:
            trusted_account_mgr = TrustedAccountManager()

            # Append wildcard to workspace_id for DOMAIN trusted account
            workspace_id = [params.workspace_id, "*"]

            trusted_account_vo = trusted_account_mgr.get_trusted_account(
                params.trusted_account_id, params.domain_id, workspace_id
            )
            schema_type = "TRUSTING_SECRET"
        else:
            trusted_account_vo = None
            params.trusted_account_id = None
            schema_type = "SECRET"

        # Check secret_data by schema
        schema_mgr = SchemaManager()
        schema_mgr.validate_secret_data_by_schema_id(
            params.secret_schema_id,
            params.domain_id,
            params.secret_data,
            schema_type,
        )

        secret_mgr = SecretManager()

        # Delete old secret
        if service_account_vo.secret_id:
            secret_mgr.delete_secret(service_account_vo.secret_id)

        # Create New Secret
        create_secret_params = {
            "name": f"{service_account_vo.service_account_id}-secret",
            "data": params.secret_data,
            "schema_id": params.secret_schema_id,
            "service_account_id": service_account_vo.service_account_id,
            "resource_group": "PROJECT",
        }

        if trusted_account_vo:
            create_secret_params[
                "trusted_secret_id"
            ] = trusted_account_vo.trusted_secret_id

        secret_info = secret_mgr.create_secret(create_secret_params)

        params_data = params.dict(exclude_unset=True)
        params_data["secret_id"] = secret_info["secret_id"]
        params_data["secret_schema_id"] = params.secret_schema_id

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(
            params_data, service_account_vo
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def delete_secret_data(
        self, params: ServiceAccountDeleteSecretRequest
    ) -> ServiceAccountResponse:
        """delete service account secret data

         Args:
            params (ServiceAccountDeleteSecretRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        secret_mgr = SecretManager()
        secret_mgr.delete_related_secrets(service_account_vo.service_account_id)

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(
            {"secret_id": None, "secret_schema_id": None, "trusted_account_id": None},
            service_account_vo,
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def delete(self, params: ServiceAccountDeleteRequest) -> None:
        """delete service account

         Args:
            params (ServiceAccountDeleteRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            None
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        # Check is managed resource
        self.resource_mgr.check_is_managed_resource(service_account_vo)

        if service_account_vo.app_id:
            raise ERROR_SERVICE_ACCOUNT_CANNOT_BE_DELETED_WITH_EXISTING_APP(
                key="service_account_id"
            )

        secret_mgr = SecretManager()
        secret_mgr.delete_related_secrets(service_account_vo.service_account_id)

        self.service_account_mgr.delete_service_account_by_vo(service_account_vo)

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def enable_app(
        self, params: ServiceAccountEnableAppRequest
    ) -> Union[AppResponse, dict]:
        """enable app created by service account

         Args:
            params (ServiceAccountEnableAppRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AppResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )
        app_vo = self.app_mgr.get_app(
            service_account_vo.app_id,
            domain_id,
            workspace_id,
            service_account_id,
        )
        app_vo = self.app_mgr.enable_app(app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def disable_app(
        self, params: ServiceAccountDisableAppRequest
    ) -> Union[AppResponse, dict]:
        """disable app created by service account

         Args:
            params (ServiceAccountDisableAppRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AppResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )
        app_vo = self.app_mgr.get_app(
            service_account_vo.app_id,
            domain_id,
            workspace_id,
            service_account_id,
        )
        app_vo = self.app_mgr.disable_app(app_vo)
        return AppResponse(**app_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def regenerate_app(
        self, params: ServiceAccountRegenerateAppRequest
    ) -> Union[AppResponse, dict]:
        """regenerate app created by service account

         Args:
            params (ServiceAccountRegenerateAppRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AppResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        app_vo = self.app_mgr.get_app(
            service_account_vo.app_id,
            domain_id,
            workspace_id,
            service_account_id,
        )

        client_id, client_secret = self._create_service_account_app_client_secret(
            app_vo, service_account_id
        )

        # Update app info
        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        return AppResponse(**app_vo.to_dict(), client_secret=client_secret)

    @transaction(
        permission="identity:ServiceAccount.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def delete_app(self, params: ServiceAccountDeleteAppRequest) -> None:
        """delete app created by service account

        Args:
            params (ServiceAccountDeleteAppRequest): {
                'service_account_id: 'str'   # required
                'workspace_id': 'str',       # injected from auth (required)
                'domain_id': 'str'           # injected from auth (required)
                'user_projects': 'list'      # injected from auth
            }
        Returns:
            None
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        app_vo = self.app_mgr.get_app(
            service_account_vo.app_id,
            domain_id,
            workspace_id,
            service_account_id,
        )
        self.app_mgr.delete_app_by_vo(app_vo)
        self.service_account_mgr.update_service_account_by_vo(
            {"app_id": None}, service_account_vo
        )

    @transaction(
        permission="identity:ServiceAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(
        self, params: ServiceAccountGetRequest
    ) -> Union[ServiceAccountResponse, dict]:
        """get service account

         Args:
            params (ServiceAccountDeleteRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
             ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id,
            params.domain_id,
            params.workspace_id,
            params.user_projects,
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(
        permission="identity:ServiceAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "service_account_id",
            "name",
            "provider",
            "secret_schema_id",
            "secret_id",
            "project_id",
            "workspace_id",
            "domain_id",
            "user_projects",
        ]
    )
    @append_keyword_filter(["service_account_id", "name"])
    @set_query_page_limit(1000)
    @convert_model
    def list(
        self, params: ServiceAccountSearchQueryRequest
    ) -> Union[ServiceAccountsResponse, dict]:
        """list service accounts

        Args:
            params (ServiceAccountSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'service_account_id': 'str',
                'name': 'str',
                'provider': 'str',
                'secret_schema_id': 'str',
                'secret_id': 'str',
                'project_id': 'str',
                'workspace_id': 'str',                  # injected from auth
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            ServiceAccountsResponse:
        """

        query = params.query or {}
        (
            service_account_vos,
            total_count,
        ) = self.service_account_mgr.list_service_accounts(query)

        service_accounts_info = [
            service_account_vo.to_dict() for service_account_vo in service_account_vos
        ]
        return ServiceAccountsResponse(
            results=service_accounts_info, total_count=total_count
        )

    @transaction(
        permission="identity:ServiceAccount.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id", "user_projects"])
    @append_keyword_filter(["service_account_id", "name"])
    @set_query_page_limit(1000)
    @convert_model
    def stat(self, params: ServiceAccountStatQueryRequest) -> dict:
        """stat service accounts

        Args:
            params (ServiceAccountStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',      # injected from auth
                'domain_id': 'str',         # injected from auth (required)
                'user_projects': 'list'     # injected from auth
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.service_account_mgr.stat_service_accounts(query)

    def _create_service_account_app_client_secret(
        self, app_vo: App, service_account_id: str
    ) -> Tuple[str, str]:
        """create client_id, client_secret for app created by service account

        Args:
            app_vo: 'App'                   # required
            service_account_id: 'str'       # required

        Returns:
            tuple: ('client_id': 'str', 'client_secret': 'str')

        """
        permissions = ["identity:ServiceAccount.read"]
        injected_params = {"service_account_id": service_account_id}
        expired_at = self._get_expired_at()

        client_secret_mgr = ClientSecretManager()
        client_id, client_secret = client_secret_mgr.generate_client_secret(
            app_vo.app_id,
            app_vo.domain_id,
            expired_at,
            app_vo.role_type,
            app_vo.workspace_id,
            permissions=permissions,
            injected_params=injected_params,
        )

        return client_id, client_secret

    @staticmethod
    def _get_expired_at() -> str:
        return (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
