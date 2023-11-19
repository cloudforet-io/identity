import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.identity.model.endpoint_request import *
from spaceone.identity.model.endpoint_response import *
from spaceone.identity.manager.endpoint_manager import EndpointManager


_LOGGER = logging.getLogger(__name__)


class EndpointService(BaseService):
    @transaction
    # @append_query_filter(['service'])
    # @append_keyword_filter(['service'])
    @convert_model
    def list(self, params: EndpointSearchQueryRequest) -> Union[EndpointsResponse, dict]:
        """ list endpoints of service

        Args:
            params (EndpointSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'service': 'str'
            }

        Returns:
            EndpointsResponse: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        endpoint_mgr: EndpointManager = EndpointManager()
        endpoints_data, total_count = endpoint_mgr.list_endpoints(params.service)

        return EndpointsResponse(
            results=endpoints_data,
            total_count=total_count
        )

