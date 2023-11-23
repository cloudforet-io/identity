import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.core.error import *
from spaceone.identity.model.trusted_service_account.request import *
from spaceone.identity.model.trusted_service_account.response import *
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.manager.trusted_service_account_manager import TrustedServiceAccountManager

_LOGGER = logging.getLogger(__name__)


class TrustedServiceAccountService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trusted_account_mgr = TrustedServiceAccountManager()

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def create(self, params: TrustedServiceAccountCreateRequest) -> Union[TrustedServiceAccountResponse, dict]:
        """ create trusted service account

         Args:
            params (TrustedServiceAccountCreateRequest): {
                'name': 'str',          # required
                'data': 'dict',         # required
                'provider': 'str',      # required
                'tags': 'dict',
                'scope': 'str',         # required
                'workspace_id': 'str',
                'domain_id': 'str'      # required
            }

        Returns:
            TrustedServiceAccountResponse:
        """

        # Check Scope
        if params.scope == 'DOMAIN':
            params.workspace_id = None
        else:
            if not params.workspace_id:
                raise ERROR_REQUIRED_PARAMETER(key='workspace_id')

        # Check data by schema
        provider_mgr = ProviderManager()
        provider_mgr.check_data_by_schema(params.provider, params.domain_id, params.data)

        trusted_account_vo = self.trusted_account_mgr.create_trusted_service_account(params.dict())
        return TrustedServiceAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def update(self, params: TrustedServiceAccountUpdateRequest) -> Union[TrustedServiceAccountResponse, dict]:
        """ update trusted service account

         Args:
            params (TrustedServiceAccountUpdateRequest): {
                'trusted_service_account_id': 'str',    # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            TrustedServiceAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_service_account(
            params.trusted_service_account_id, params.domain_id, params.workspace_id
        )

        if params.data:
            # Check data by schema
            provider_mgr = ProviderManager()
            provider_mgr.check_data_by_schema(trusted_account_vo.provider, params.domain_id, params.data)

        trusted_account_vo = self.trusted_account_mgr.update_trusted_service_account_by_vo(
            params.dict(exclude_unset=True), trusted_account_vo
        )

        return TrustedServiceAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def delete(self, params: TrustedServiceAccountDeleteRequest) -> None:
        """ delete trusted service account

         Args:
            params (TrustedServiceAccountDeleteRequest): {
                'trusted_service_account_id': 'str',    # required
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            None
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_service_account(
            params.trusted_service_account_id, params.domain_id, params.workspace_id
        )

        # self.trusted_account_mgr.delete_trusted_secrets(
        #     params.trusted_service_account_id, params.workspace_id, params.domain_id
        # )
        self.trusted_account_mgr.delete_trusted_service_account_by_vo(trusted_account_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @convert_model
    def get(self, params: TrustedServiceAccountGetRequest) -> Union[TrustedServiceAccountResponse, dict]:
        """ get trusted service account

         Args:
            params (TrustedServiceAccountGetRequest): {
                'trusted_service_account_id': 'str',    # required
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            TrustedServiceAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_service_account(
            params.trusted_service_account_id, params.domain_id, params.workspace_id
        )

        return TrustedServiceAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter([
        'trusted_service_account_id', 'name', 'provider', 'scope', 'workspace_id', 'domain_id', 'user_workspaces'
    ])
    @append_keyword_filter(['trusted_service_account_id', 'name'])
    @convert_model
    def list(self, params: TrustedServiceAccountSearchQueryRequest) -> Union[TrustedServiceAccountsResponse, dict]:
        """ list providers

        Args:
            params (TrustedServiceAccountSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'trusted_service_account_id': 'str',
                'name': 'str',
                'provider': 'str',
                'scope': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_workspaces': 'list'   # from meta
            }

        Returns:
            TrustedServiceAccountsResponse:
        """

        query = params.query or {}
        trusted_account_vos, total_count = self.trusted_account_mgr.list_trusted_service_accounts(query)

        trusted_accounts_info = [trusted_account_vo.to_dict() for trusted_account_vo in trusted_account_vos]
        return TrustedServiceAccountsResponse(results=trusted_accounts_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter(['domain_id', 'workspace_id', 'user_workspaces'])
    @append_keyword_filter(['trusted_service_account_id', 'name'])
    @convert_model
    def stat(self, params: TrustedServiceAccountStatQueryRequest) -> dict:
        """ stat trusted service accounts

        Args:
            params (TrustedServiceAccountStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_workspaces': 'list'   # from meta
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}
        return self.trusted_account_mgr.stat_trusted_service_accounts(query)
