import logging
from typing import Generator, Union
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

__ALL__ = ["AccountCollectorPluginManager"]

_LOGGER = logging.getLogger(__name__)


class AccountCollectorPluginManager(BaseManager):
    def init_plugin(self, endpoint: str, options: dict, domain_id: str) -> dict:
        plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint, token="NO_TOKEN"
        )
        return plugin_connector.dispatch(
            "AccountCollector.init",
            {
                "domain_id": domain_id,
                "options": options,
            },
        )

    def sync(
        self,
        endpoint: str,
        options: dict,
        secret_data: dict,
        domain_id: str,
        schema_id: str = None,
    ) -> Generator[dict, None, None]:
        plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint, token="NO_TOKEN"
        )

        params = {
            "options": options,
            "secret_data": secret_data,
            "domain_id": domain_id,
        }
        if schema_id:
            params["schema_id"] = schema_id

        return plugin_connector.dispatch("AccountCollector.sync", params)
