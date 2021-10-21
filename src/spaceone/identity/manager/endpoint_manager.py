import logging

from spaceone.core import config
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)

ENDPOINT_MAP = {
    'public': 'ENDPOINTS',
    'internal': 'INTERNAL_ENDPOINTS'
}


class EndpointManager(BaseManager):

    def list_endpoints(self, query={}, endpoint_type='public'):
        endpoint_map = ENDPOINT_MAP.get(endpoint_type, 'ENDPOINTS')
        endpoints = config.get_global(endpoint_map, [])
        return endpoints, len(endpoints)
