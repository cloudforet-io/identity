import logging

from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

_LOGGER = logging.getLogger(__name__)


class SecretManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")

        self.secret_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )

    def get_secret_data(self, secret_id: str, domain_id: str) -> dict:
        system_token = config.get_global("TOKEN")

        response = self.secret_conn.dispatch(
            "Secret.get_data",
            {"secret_id": secret_id, "domain_id": domain_id},
            token=system_token,
        )
        return response["data"]

    def get_trusted_secret_data(self, trusted_secret_id: str, domain_id: str) -> dict:
        system_token = config.get_global("TOKEN")

        response = self.secret_conn.dispatch(
            "TrustedSecret.get_data",
            {"trusted_secret_id": trusted_secret_id, "domain_id": domain_id},
            token=system_token,
        )
        return response["data"]

    def create_trusted_secret(self, params: dict) -> dict:
        return self.secret_conn.dispatch("TrustedSecret.create", params)

    def update_trusted_secret_data(
        self, trusted_secret_id: str, schema_id: str, data: dict
    ) -> None:
        self.secret_conn.dispatch(
            "TrustedSecret.update_data",
            {
                "trusted_secret_id": trusted_secret_id,
                "schema_id": schema_id,
                "data": data,
            },
        )

    def delete_related_trusted_secrets(self, trusted_account_id: str):
        response = self.list_trusted_secrets({"trusted_account_id": trusted_account_id})

        for trusted_secret_info in response.get("results", []):
            trusted_secret_id = trusted_secret_info["trusted_secret_id"]
            self.secret_conn.dispatch(
                "TrustedSecret.delete",
                {"trusted_secret_id": trusted_secret_id},
            )

    def list_trusted_secrets(self, params: dict) -> dict:
        return self.secret_conn.dispatch("TrustedSecret.list", params)

    def create_secret(self, params: dict, domain_id: str = None) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.secret_conn.dispatch(
                "Secret.create", params, x_domain_id=domain_id
            )
        else:
            return self.secret_conn.dispatch("Secret.create", params)

    def update_secret(self, params: dict) -> dict:
        return self.secret_conn.dispatch("Secret.update", params)

    def delete_secret(self, secret_id: str, domain_id: str = None) -> None:
        if self.token_type == "SYSTEM_TOKEN":
            self.secret_conn.dispatch(
                "Secret.delete", {"secret_id": secret_id}, x_domain_id=domain_id
            )
        else:
            self.secret_conn.dispatch("Secret.delete", {"secret_id": secret_id})

    def update_secret_data(
        self,
        params: dict,
        domain_id: str = None,
        workspace_id: str = None,
    ) -> None:
        if self.token_type == "SYSTEM_TOKEN":
            self.secret_conn.dispatch(
                "Secret.update_data",
                params,
                x_domain_id=domain_id,
                x_workspace_id=workspace_id,
            )
        else:
            self.secret_conn.dispatch("Secret.update_data", params)

    def delete_related_secrets(self, service_account_id: str):
        response = self.list_secrets({"service_account_id": service_account_id})

        for secret_info in response.get("results", []):
            secret_id = secret_info["secret_id"]
            self.secret_conn.dispatch(
                "Secret.delete",
                {"secret_id": secret_id},
            )

    def list_secrets(self, params: dict, domain_id: str = None) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.secret_conn.dispatch(
                "Secret.list", params, x_domain_id=domain_id
            )
        else:
            return self.secret_conn.dispatch("Secret.list", params)
