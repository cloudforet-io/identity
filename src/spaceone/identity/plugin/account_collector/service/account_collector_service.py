import logging
from typing import Union
from spaceone.core.service import BaseService, transaction
from spaceone.core.service.utils import convert_model
from spaceone.identity.plugin.account_collector.model.account_collect_request import *
from spaceone.identity.plugin.account_collector.model.account_collect_response import *

_LOGGER = logging.getLogger(__name__)


class AccountCollectorService(BaseService):
    resource = "AccountCollector"

    @transaction
    @convert_model
    def init(self, params: AccountCollectorInitRequest) -> Union[PluginResponse, dict]:
        """Get external cost data

        Args:
            params (CostGetDataRequest): {
                'options': 'dict',          # Required
                'domain_id': 'str'          # Required
            }

        Returns:
            Generator[PluginResponse, None, None]
            {
                'metadata': 'dict'
            }
        """

        func = self.get_plugin_method("init")
        response = func(params.dict())
        return PluginResponse(**response)

    @transaction
    @convert_model
    def sync(
        self, params: AccountCollectorSyncRequest
    ) -> Union[AccountsResponse, dict]:
        """Get external cost data

        Args:
            params (AccountCollectorSyncRequest): {
                'options': 'dict',          # Required
                'schema_id': 'str',
                'secret_data': 'dict',       # Required
                'domain_id': 'str'          # Required
            }

        Returns:
            AccountsResponse:
            {
                'results': 'list[AccountResponse]'
            }
        """

        func = self.get_plugin_method("sync")
        response = func(params.dict())
        return AccountsResponse(**response)
