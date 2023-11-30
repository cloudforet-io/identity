import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.core.error import *
from spaceone.identity.model.trusted_account.request import *
from spaceone.identity.model.trusted_account.response import *
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.manager.trusted_account_manager import TrustedAccountManager

_LOGGER = logging.getLogger(__name__)


class TrustedAccountService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trusted_account_mgr = TrustedAccountManager()

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def create(self, params: TrustedAccountCreateRequest) -> Union[TrustedAccountResponse, dict]:
        """ create trusted service account

         Args:
            params (TrustedAccountCreateRequest): {
                'name': 'str',          # required
                'data': 'dict',         # required
                'provider': 'str',      # required
                'tags': 'dict',
                'scope': 'str',         # required
                'workspace_id': 'str',
                'domain_id': 'str'      # required
            }

        Returns:
            TrustedAccountResponse:
        """

        # Check data by schema

        trusted_account_vo = self.trusted_account_mgr.create_trusted_account(params.dict())
        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def update(self, params: TrustedAccountUpdateRequest) -> Union[TrustedAccountResponse, dict]:
        """ update trusted service account

         Args:
            params (TrustedAccountUpdateRequest): {
                'trusted_account_id': 'str',    # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            TrustedAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        if params.data:
            # Check data by schema
            pass

        trusted_account_vo = self.trusted_account_mgr.update_trusted_account_by_vo(
            params.dict(exclude_unset=True), trusted_account_vo
        )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
    @convert_model
    def delete(self, params: TrustedAccountDeleteRequest) -> None:
        """ delete trusted service account

         Args:
            params (TrustedAccountDeleteRequest): {
                'trusted_account_id': 'str',    # required
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            None
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        self.trusted_account_mgr.delete_trusted_account_by_vo(trusted_account_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @convert_model
    def get(self, params: TrustedAccountGetRequest) -> Union[TrustedAccountResponse, dict]:
        """ get trusted service account

         Args:
            params (TrustedAccountGetRequest): {
                'trusted_account_id': 'str',    # required
                'workspace_id': 'str',
                'domain_id': 'str'                      # required
            }

        Returns:
            TrustedAccountResponse:
        """

        trusted_account_vo = self.trusted_account_mgr.get_trusted_account(
            params.trusted_account_id, params.domain_id, params.workspace_id
        )

        return TrustedAccountResponse(**trusted_account_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter([
        'trusted_account_id', 'name', 'provider', 'permission_group', 'workspace_id', 'domain_id'
    ])
    @append_keyword_filter(['trusted_account_id', 'name'])
    @convert_model
    def list(self, params: TrustedAccountSearchQueryRequest) -> Union[TrustedAccountsResponse, dict]:
        """ list providers

        Args:
            params (TrustedAccountSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'trusted_account_id': 'str',
                'name': 'str',
                'provider': 'str',
                'permission_group': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',         # required
            }

        Returns:
            TrustedAccountsResponse:
        """

        query = params.query or {}
        trusted_account_vos, total_count = self.trusted_account_mgr.list_trusted_accounts(query)

        trusted_accounts_info = [trusted_account_vo.to_dict() for trusted_account_vo in trusted_account_vos]
        return TrustedAccountsResponse(results=trusted_accounts_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter(['workspace_id', 'domain_id'])
    @append_keyword_filter(['trusted_account_id', 'name'])
    @convert_model
    def stat(self, params: TrustedAccountStatQueryRequest) -> dict:
        """ stat trusted service accounts

        Args:
            params (TrustedAccountStatQueryRequest): {
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
        return self.trusted_account_mgr.stat_trusted_accounts(query)
