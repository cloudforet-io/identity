import logging
from typing import Union
from spaceone.core.service import (BaseService, transaction, convert_model, append_query_filter,
                                   append_keyword_filter, set_query_page_limit)
from spaceone.identity.model.service_account.request import *
from spaceone.identity.model.service_account.response import *
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.trusted_service_account_manager import TrustedServiceAccountManager


_LOGGER = logging.getLogger(__name__)


class ServiceAccountService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_account_mgr = ServiceAccountManager()

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @convert_model
    def create(self, params: ServiceAccountCreateRequest) -> Union[ServiceAccountResponse, dict]:
        """ create service account

         Args:
            params (ServiceAccountCreateRequest): {
                'name': 'str',                          # required
                'data': 'dict',                         # required
                'provider': 'str',                      # required
                'trusted_service_account_id': 'str',
                'tags': 'dict',
                'project_id': 'str',                    # required
                'workspace_id': 'str',                  # required
                'domain_id': 'str'                      # required
            }

        Returns:
            ServiceAccountResponse:
        """

        # Check data by schema
        provider_mgr = ProviderManager()
        provider_mgr.check_data_by_schema(params.provider, params.domain_id, params.data)

        # Check trusted service account
        if params.trusted_service_account_id:
            trusted_service_account_mgr = TrustedServiceAccountManager()
            trusted_service_account_mgr.get_trusted_service_account(
                params.trusted_service_account_id, params.domain_id, params.workspace_id
            )

        service_account_vo = self.service_account_mgr.create_service_account(params.dict())
        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @convert_model
    def update(self, params: ServiceAccountUpdateRequest) -> Union[ServiceAccountResponse, dict]:
        """ update service account

         Args:
            params (ServiceAccountUpdateRequest): {
                'service_account_id': 'str',        # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'project_id': 'str',
                'workspace_id': 'str',              # required
                'domain_id': 'str',                 # required
                'user_projects': 'list'             # from meta
            }

        Returns:
            ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id, params.domain_id, params.workspace_id, params.user_projects
        )

        if params.data:
            # Check data by schema
            provider_mgr = ProviderManager()
            provider_mgr.check_data_by_schema(service_account_vo.provider, params.domain_id, params.data)

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(
            params.dict(exclude_unset=True), service_account_vo
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @convert_model
    def change_trusted_service_account(
        self, params: ServiceAccountChangeTrustedServiceAccountRequest
    ) -> Union[ServiceAccountResponse, dict]:
        """ change trusted service account

         Args:
            params (ServiceAccountChangeTrustedServiceAccountRequest): {
                'service_account_id': 'str',            # required
                'trusted_service_account_id': 'str',    # required
                'workspace_id': 'str',                  # required
                'domain_id': 'str',                     # required
                'user_projects': 'list'                 # from meta
            }

        Returns:

            ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id, params.domain_id, params.workspace_id, params.user_projects
        )

        # Check trusted service account
        trusted_service_account_mgr = TrustedServiceAccountManager()
        trusted_service_account_mgr.get_trusted_service_account(
            params.trusted_service_account_id, params.domain_id, params.workspace_id
        )

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(
            {'trusted_service_account_id': params.trusted_service_account_id}, service_account_vo
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @convert_model
    def delete(self, params: ServiceAccountDeleteRequest) -> None:
        """ delete service account

         Args:
            params (ServiceAccountDeleteRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # required
                'domain_id': 'str',                     # required
                'user_projects': 'list'                 # from meta
            }

        Returns:
            None
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id, params.domain_id, params.workspace_id, params.user_projects
        )

        self.service_account_mgr.delete_service_account_by_vo(service_account_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT_READ'})
    @convert_model
    def get(self, params: ServiceAccountGetRequest) -> Union[ServiceAccountResponse, dict]:
        """ get service account

         Args:
            params (ServiceAccountDeleteRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # required
                'domain_id': 'str',                     # required
                'user_projects': 'list'                 # from meta
            }

        Returns:
             ServiceAccountResponse:
        """

        service_account_vo = self.service_account_mgr.get_service_account(
            params.service_account_id, params.domain_id, params.workspace_id, params.user_projects
        )

        return ServiceAccountResponse(**service_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'PROJECT_READ'})
    @append_query_filter([
        'service_account_id', 'name', 'provider', 'project_id', 'workspace_id', 'domain_id', 'user_projects',
        'user_workspaces'
    ])
    @append_keyword_filter(['service_account_id', 'name'])
    @set_query_page_limit(1000)
    @convert_model
    def list(self, params: ServiceAccountSearchQueryRequest) -> Union[ServiceAccountsResponse, dict]:
        """ list service accounts

        Args:
            params (ServiceAccountSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'service_account_id': 'str',
                'name': 'str',
                'provider': 'str',
                'project_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',                     # required
                'user_workspaces': 'list',              # from meta
                'user_projects': 'list'                 # from meta
            }

        Returns:
            ServiceAccountsResponse:
        """

        query = params.query or {}
        service_account_vos, total_count = self.service_account_mgr.list_service_accounts(query)

        service_accounts_info = [service_account_vo.to_dict() for service_account_vo in service_account_vos]
        return ServiceAccountsResponse(results=service_accounts_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'PROJECT_READ'})
    @append_query_filter(['domain_id', 'workspace_id', 'user_workspaces', 'user_projects'])
    @append_keyword_filter(['service_account_id', 'name'])
    @set_query_page_limit(1000)
    @convert_model
    def stat(self, params: ServiceAccountStatQueryRequest) -> dict:
        """ stat service accounts

        Args:
            params (ServiceAccountStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_workspaces': 'list',  # from meta
                'user_projects': 'list'     # from meta
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.service_account_mgr.stat_service_accounts(query)
