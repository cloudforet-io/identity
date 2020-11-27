import logging

from spaceone.core import config
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)


class EndpointManager(BaseManager):

    def list_endpoints(self, query={}):
        endpoints = config.get_global('ENDPOINTS', [])
        return endpoints, len(endpoints)
