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

    def delete_trusted_secret(self, trusted_secret_id: str):
        self.secret_conn.dispatch(
            "TrustedSecret.delete", {"trusted_secret_id": trusted_secret_id}
        )

    def create_secret(self, params: dict) -> dict:
        return self.secret_conn.dispatch("Secret.create", params)

    def update_secret_data(self, secret_id: str, schema_id: str, data: dict) -> None:
        self.secret_conn.dispatch(
            "Secret.update_data",
            {"secret_id": secret_id, "schema_id": schema_id, "data": data},
        )

    def delete_secret(self, secret_id: str):
        self.secret_conn.dispatch("Secret.delete", {"secret_id": secret_id})
