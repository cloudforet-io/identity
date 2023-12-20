import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.core.error import *

from spaceone.identity.model.service_account.request import *
from spaceone.identity.model.service_account.response import *
from spaceone.identity.manager.schema_manager import SchemaManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.secret_manager import SecretManager

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
            secret_mgr = SecretManager()
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
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
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

        secret_mgr = SecretManager()
        secret_mgr.delete_related_secrets(service_account_vo.service_account_id)

        self.service_account_mgr.delete_service_account_by_vo(service_account_vo)

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
