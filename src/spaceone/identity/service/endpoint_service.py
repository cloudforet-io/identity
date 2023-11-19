import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.endpoint_request import *
from spaceone.identity.model.endpoint_response import *


_LOGGER = logging.getLogger(__name__)


class EndpointService(BaseService):
    @transaction
    @convert_model
    def list(self, params: EndpointSearchQueryRequest) -> Union[EndpointsResponse, dict]:
        return {}

