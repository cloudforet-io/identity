import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class SecretManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secret_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )

    def get_secret_data(self, secret_id: str, domain_id: str) -> dict:
        return self.secret_conn.dispatch(
            "Secret.get_data", {"secret_id": secret_id, "domain_id": domain_id}
        )

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

    def create_secret(self, params: dict) -> dict:
        return self.secret_conn.dispatch("Secret.create", params)

    def update_secret(self, params: dict) -> dict:
        return self.secret_conn.dispatch("Secret.update", params)

    def delete_secret(self, secret_id: str) -> None:
        self.secret_conn.dispatch("Secret.delete", {"secret_id": secret_id})

    def update_secret_data(self, secret_id: str, schema_id: str, data: dict) -> None:
        self.secret_conn.dispatch(
            "Secret.update_data",
            {"secret_id": secret_id, "schema_id": schema_id, "data": data},
        )

    def delete_related_secrets(self, service_account_id: str):
        response = self.list_secrets({"service_account_id": service_account_id})

        for secret_info in response.get("results", []):
            secret_id = secret_info["secret_id"]
            self.secret_conn.dispatch(
                "Secret.delete",
                {"secret_id": secret_id},
            )

    def list_secrets(self, params: dict) -> dict:
        return self.secret_conn.dispatch("Secret.list", params)
