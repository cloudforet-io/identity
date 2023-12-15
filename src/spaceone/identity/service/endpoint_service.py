import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.model.endpoint.request import *
from spaceone.identity.model.endpoint.response import *
from spaceone.identity.manager.endpoint_manager import EndpointManager

_LOGGER = logging.getLogger(__name__)


@event_handler
class EndpointService(BaseService):
    resource = "Endpoint"

    @transaction()
    # @append_query_filter(['service'])
    # @append_keyword_filter(['service'])
    @convert_model
    def list(
        self, params: EndpointSearchQueryRequest
    ) -> Union[EndpointsResponse, dict]:
        """list endpoints of service

        Args:
            params (EndpointSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'service': 'str'
            }

        Returns:
            EndpointsResponse:
        """

        endpoint_mgr: EndpointManager = EndpointManager()
        endpoints_info, total_count = endpoint_mgr.list_endpoints(params.service)

        return EndpointsResponse(results=endpoints_info, total_count=total_count)
