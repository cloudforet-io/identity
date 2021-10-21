import logging

from google.protobuf.json_format import MessageToDict
from spaceone.core import pygrpc
from spaceone.core.connector import BaseConnector
from spaceone.core.utils import parse_endpoint

from spaceone.identity.error.error_authentication import *

_LOGGER = logging.getLogger(__name__)


class AuthPluginConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)
        self.client = None

    def initialize(self, endpoint):
        _LOGGER.info(f'[initialize] endpoint: {endpoint}')

        e = parse_endpoint(endpoint)
        self.client = pygrpc.client(endpoint=f'{e.get("hostname")}:{e.get("port")}', version='plugin')

    def call_login(self, endpoint, credentials, options, secret_data, schema=None):
        self.initialize(endpoint)

        params = {
            'options': options,
            'secret_data': secret_data,
            'schema': schema,
            'user_credentials': credentials
        }

        try:
            response = self.client.Auth.login(params, metadata=self.transaction.get_connection_meta())
        except ERROR_BASE as e:
            _LOGGER.error(f'[call_login] Auth.login failed. (reason={e.message})')
            raise ERROR_INVALID_CREDENTIALS()
        except Exception as e:
            _LOGGER.error(f'[call_login] Auth.login failed. (reason={str(e)})')
            raise ERROR_INVALID_CREDENTIALS()

        return MessageToDict(response, preserving_proto_field_name=True)

    def init(self, options):
        params = {
            'options': options
        }

        try:
            response = self.client.Auth.init(params, metadata=self.transaction.get_connection_meta())
            return MessageToDict(response, preserving_proto_field_name=True)
        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))

    def verify(self, options, secret_data=None, schema=None):
        params = {
            'options': options,
            'secret_data': secret_data,
            'schema': schema
        }
        try:
            # TODO: meta (plugin has no meta)
            response = self.client.Auth.verify(params, metadata=self.transaction.get_connection_meta())
            return MessageToDict(response, preserving_proto_field_name=True)
        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))

    def call_find(self, keyword, user_id, options, secret_data={}, schema=None):
        params = {
            'options': options,
            'secret_data': secret_data,
            'schema': schema,
            'keyword': keyword,
            'user_id': user_id
        }
        _LOGGER.info(f'[call_find] params: {params}')

        try:
            response = self.client.Auth.find(params, metadata=self.transaction.get_connection_meta())

            users_info = MessageToDict(response, preserving_proto_field_name=True)
            _LOGGER.debug(f'[call_find] MessageToDict(user_info): {users_info}')
            return users_info

        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))
