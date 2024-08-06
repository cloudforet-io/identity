import logging

from spaceone.core.connector import BaseConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

__all__ = ["AccountCollectorPluginConnector"]

_LOGGER = logging.getLogger(__name__)


class AccountCollectorPluginConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.secret_data = None
        self.options = None
        self.schema = None
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")

    def initialize(self, endpoint: str) -> None:
        static_endpoint = self.config.get("endpoint")

        if static_endpoint:
            endpoint = static_endpoint

        self.client = self.locator.get_connector(
            "SpaceConnector", endpoint=endpoint, token="NO_TOKEN"
        )

        self.secret_data = self.config.get("secret_data")
        self.options = self.config.get("options")
        self.schema = self.config.get("schema")

    def init(self, domain_id: str, options: dict):
        return self.client.dispatch(
            "AccountCollector.init", {"options": options, "domain_id": domain_id}
        )

    def sync(
        self,
        options: dict,
        secret_data: dict,
        schema: str,
        domain_id: str,
    ):
        params = {
            "options": self.options or options,
            "secret_data": self.secret_data or secret_data,
            "schema": self.schema or schema,
            "domain_id": domain_id,
        }
        return self.client.dispatch("AccountCollector.sync", params)
