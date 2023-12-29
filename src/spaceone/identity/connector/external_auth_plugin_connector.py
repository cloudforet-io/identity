import logging

from spaceone.core.connector import BaseConnector

from spaceone.identity.error.error_authentication import *

_LOGGER = logging.getLogger(__name__)


class ExternalAuthPluginConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None

    def initialize(self, endpoint):
        static_endpoint = self.config.get("endpoint")

        if static_endpoint:
            endpoint = static_endpoint

        _LOGGER.info(f"[initialize] endpoint: {endpoint}")
        self.client = self.locator.get_connector("SpaceConnector", endpoint=endpoint)

    def init(self, options: dict, domain_id: str):
        params = {"options": options, "domain_id": domain_id}

        try:
            return self.client.dispatch("ExternalAuth.init", params)

        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))

    def authorize(
        self,
        credentials,
        options,
        secret_data,
        domain_id,
        schema_id=None,
        metadata=None,
    ):
        params = {
            "options": options,
            "secret_data": secret_data,
            "credentials": credentials,
            "schema_id": schema_id,
            "domain_id": domain_id,
            "metadata": metadata or {},
        }

        try:
            user_info = self.client.dispatch("ExternalAuth.authorize", params)
            return user_info
        except ERROR_BASE as e:
            _LOGGER.error(
                f"[authorize] ExternalAuth.authorize failed. (reason={e.message})"
            )
            raise ERROR_INVALID_CREDENTIALS()
        except Exception as e:
            _LOGGER.error(
                f"[authorize] ExternalAuth.authorize failed. (reason={str(e)})"
            )
            raise ERROR_INVALID_CREDENTIALS()

    # def call_find(self, keyword, user_id, options, secret_data={}, schema=None):
    #     params = {
    #         "options": options,
    #         "secret_data": secret_data,
    #         "schema": schema,
    #         "keyword": keyword,
    #         "user_id": user_id,
    #     }
    #     _LOGGER.info(f"[call_find] params: {params}")
    #
    #     try:
    #         response = self.client.Auth.find(
    #             params, metadata=self.transaction.get_connection_meta()
    #         )
    #
    #         _LOGGER.debug(f"[call_find] MessageToDict(user_info): {users_info}")
    #         return users_info
    #
    #     except ERROR_BASE as e:
    #         raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
    #     except Exception as e:
    #         raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))
