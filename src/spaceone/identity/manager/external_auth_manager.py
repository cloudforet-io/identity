import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core import config
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.manager import BaseManager

from spaceone.identity.connector.external_auth_plugin_connector import (
    ExternalAuthPluginConnector,
)
from spaceone.identity.model.domain.database import Domain
from spaceone.identity.model.external_auth.database import ExternalAuth

_LOGGER = logging.getLogger(__name__)


class ExternalAuthManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.external_auth_model = ExternalAuth

    def set_external_auth(self, params: dict, domain_vo: Domain) -> ExternalAuth:
        def _rollback(old_data):
            _LOGGER.info(
                f'[set_external_auth._rollback] Revert Data: {old_data["domain_id"]}'
            )
            external_auth_vo.update(old_data)

        if plugin_info := params.get("plugin_info"):
            domain_id = domain_vo.domain_id
            options = plugin_info.get("options", {})
            endpoint, updated_version = self.get_auth_plugin_endpoint(
                domain_id, plugin_info
            )

            if updated_version:
                params["plugin_info"]["version"] = updated_version

            response = self.init_auth_plugin(endpoint, options, domain_id)
            params["plugin_info"]["metadata"] = response["metadata"]

            secret_data = plugin_info.get("secret_data")

            if secret_data:
                schema = plugin_info.get("schema")
                secret_id = self._create_secret(domain_id, secret_data, schema)

                if secret_id:
                    params["plugin_info"]["secret_id"] = secret_id
                    del params["plugin_info"]["secret_data"]

        params.update({"state": "ENABLED"})
        external_auth_vo = self.external_auth_model.create(params)
        self.transaction.add_rollback(_rollback, external_auth_vo.to_dict())

        return external_auth_vo

    @staticmethod
    def delete_external_auth_by_vo(external_auth_vo: ExternalAuth):
        external_auth_vo.delete()

    def get_external_auth(self, domain_id: str) -> ExternalAuth:
        return self.external_auth_model.get(domain_id=domain_id)

    def get_auth_info(self, domain_vo: Domain) -> dict:
        external_auth_vos = self.filter_external_auth(domain_id=domain_vo.domain_id)

        if external_auth_vos.count() > 0:
            external_auth_state = "ENABLED"
            plugin_info = external_auth_vos[0].plugin_info
            metadata = plugin_info.get("metadata", {})
            # if secret_id := plugin_info.get("secret_id"):
            #     secret_mgr = SecretManager()
            #     secret_data = secret_mgr.get_secret_data(secret_id, domain_vo.domain_id)

        else:
            external_auth_state = "DISABLED"
            metadata = {}

        return {
            "domain_id": domain_vo.domain_id,
            "name": domain_vo.name,
            "external_auth_state": external_auth_state,
            "metadata": metadata,
        }

    def filter_external_auth(self, **conditions) -> QuerySet:
        return self.external_auth_model.filter(**conditions)

    def get_auth_plugin_endpoint(
        self, domain_id: str, plugin_info: dict
    ) -> Tuple[str, str]:
        system_token = config.get_global("TOKEN")
        plugin_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="plugin"
        )
        response = plugin_connector.dispatch(
            "Plugin.get_plugin_endpoint",
            {
                "plugin_id": plugin_info["plugin_id"],
                "version": plugin_info.get("version"),
                "upgrade_mode": plugin_info.get("upgrade_mode", "AUTO"),
                "domain_id": domain_id,
            },
            token=system_token,
        )

        return response["endpoint"], response.get("updated_version")

    @staticmethod
    def init_auth_plugin(endpoint: str, options: dict, domain_id: str) -> dict:
        external_auth_conn = ExternalAuthPluginConnector()
        external_auth_conn.initialize(endpoint)

        return external_auth_conn.init(options, domain_id)

    def _create_secret(self, domain_id: str, secret_data: dict, schema: dict) -> str:
        secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )

        params = {
            "name": f"{domain_id}-auth-plugin-credentials",
            "data": secret_data,
            # "schema_id": schema_id,
            "domain_id": domain_id,
            "resource_group": "DOMAIN",
        }

        response = secret_connector.dispatch("Secret.create", params)
        _LOGGER.debug(f"[_create_secret] {response}")
        return response.get("secret_id")
