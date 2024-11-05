import logging
from typing import Tuple

from spaceone.core.manager import BaseManager

from spaceone.identity.connector.account_collector_plugin_connector import (
    AccountCollectorPluginConnector,
)
from spaceone.identity.manager.plugin_manager import PluginManager
from spaceone.identity.manager.provider_manager import ProviderManager
from spaceone.identity.model.provider.database import Provider
from spaceone.core.connector.space_connector import SpaceConnector

__ALL__ = ["AccountCollectorPluginManager"]

_LOGGER = logging.getLogger(__name__)


class AccountCollectorPluginManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.acp_connector = AccountCollectorPluginConnector()

    def initialize(self, endpoint: str) -> None:
        _LOGGER.debug(f"[initialize] account collector plugin endpoint: {endpoint}")
        self.acp_connector.initialize(endpoint)

    def init_plugin(self, domain_id: str, options: dict) -> dict:
        plugin_info = self.acp_connector.init(domain_id, options)

        _LOGGER.debug(f"[plugin_info] {plugin_info}")
        plugin_metadata = plugin_info.get("metadata", {})

        return plugin_metadata

    def sync(
        self,
        endpoint: str,
        options: dict,
        secret_data: dict,
        domain_id: str,
        schema_id: str = None,
    ) -> dict:
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

    def get_account_collector_plugin_endpoint_by_vo(self, provider_vo: Provider) -> str:
        plugin_info = provider_vo.plugin_info
        endpoint, updated_version = self.get_account_collector_plugin_endpoint(
            plugin_info, provider_vo.domain_id
        )

        if updated_version:
            _LOGGER.debug(
                f'[get_account_collector_plugin_endpoint_by_vo] upgrade plugin version: {plugin_info.get("version")} -> {updated_version}'
            )
            self.upgrade_account_collector_plugin_version(
                provider_vo, endpoint, updated_version
            )

        return endpoint

    def get_account_collector_plugin_endpoint(
        self, plugin_info: dict, domain_id: str
    ) -> Tuple[str, str]:
        plugin_mgr: PluginManager = self.locator.get_manager("PluginManager")
        return plugin_mgr.get_plugin_endpoint(plugin_info, domain_id)

    def upgrade_account_collector_plugin_version(
        self, provider_vo: Provider, endpoint: str, updated_version: str
    ) -> None:
        plugin_info = provider_vo.plugin_info
        domain_id = provider_vo.domain_id

        self.initialize(endpoint)

        plugin_options = plugin_info.get("options", {})

        plugin_metadata = self.init_plugin(domain_id, plugin_options)
        plugin_info["version"] = updated_version
        plugin_info["metadata"] = plugin_metadata

        provider_mgr = ProviderManager()
        provider_mgr.update_provider_by_vo({"plugin_info": plugin_info}, provider_vo)
