import logging

from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)

_AUTH_CONFIG_KEYS = ["settings"]


class ConfigManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="config"
        )

    def get_auth_config(self, domain_id: str) -> dict:
        system_token = config.get_global("TOKEN")
        params = {
            "query": {
                "filter": [
                    {"k": "name", "v": _AUTH_CONFIG_KEYS, "o": "in"},
                ]
            }
        }

        response = self.list_domain_configs(
            params, token=system_token, x_domain_id=domain_id
        )

        auth_config = {}
        for config_info in response.get("results", []):
            auth_config[config_info["name"]] = config_info["data"]

        return auth_config

    def list_domain_configs(
        self, params: dict, token: str = None, x_domain_id: str = None
    ) -> dict:
        return self.config_conn.dispatch(
            "DomainConfig.list",
            params,
            token=token,
            x_domain_id=x_domain_id,
        )
