import logging
from typing import Tuple

from spaceone.core import config
from spaceone.core.manager import BaseManager

_LOGGER = logging.getLogger(__name__)


class EndpointManager(BaseManager):

    @staticmethod
    def list_endpoints(service: str = None, endpoint_type: str = None) -> Tuple[list, int]:
        endpoints: list = config.get_global("ENDPOINTS", [])

        if service:
            endpoints: list = [
                endpoint for endpoint in endpoints if endpoint.get("service") == service
            ]

        if endpoint_type == "INTERNAL":
            for endpoint in endpoints:
                endpoint["endpoint"] = None
        else:
            for endpoint in endpoints:
                endpoint["internal_endpoint"] = None

        return endpoints, len(endpoints)
