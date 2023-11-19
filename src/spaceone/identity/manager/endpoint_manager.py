import logging
from typing import Tuple

from spaceone.core import config
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)


class EndpointManager(BaseManager):

    def list_endpoints(self, service: str = None) -> Tuple[list, int]:
        endpoints: list = config.get_global('ENDPOINTS', [])

        if service:
            endpoints: list = [endpoint for endpoint in endpoints if endpoint.get('service') == service]

        return endpoints, len(endpoints)
