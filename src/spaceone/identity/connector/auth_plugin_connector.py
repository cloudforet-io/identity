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

        endpoint = endpoint.replace('"', '')
        e = parse_endpoint(endpoint)
        protocol = e['scheme']
        if protocol == 'grpc':
            self.client = pygrpc.client(endpoint="%s:%s" % (e['hostname'], e['port']), version='plugin')
        elif protocol == 'http':
            # TODO:
            pass

        if self.client is None:
            raise ERROR_GRPC_CONFIGURATION

    def call_login(self, endpoint, credentials):
        self.initialize(endpoint)

        # TODO: secret_data
        params = {
            'secret_data': {},
            'user_credentials': credentials,
            'options': {}
        }
        try:
            meta = self.transaction.get_meta('transaction_id')
            user_info = self.client.Auth.login(
                params
                # metadata=meta
            )
        except ERROR_BASE as e:
            _LOGGER.error(f'[call_login] Auth.login failed. (reason={e.message})')
            raise ERROR_INVALID_CREDENTIALS()
        except Exception as e:
            _LOGGER.error(f'[call_login] Auth.login failed. (reason={str(e)})')
            raise ERROR_INVALID_CREDENTIALS()

        return user_info

    def verify(self, options, secret_data):
        params = {
            'options': options,
            'secret_data': secret_data
        }
        try:
            # TODO: meta (plugin has no meta)
            auth_verify_info = self.client.Auth.verify(params)
            return MessageToDict(auth_verify_info)
        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))

    def call_find(self, keyword, user_id, domain):
        params = {
            'options': domain.plugin_info.options,
            'secret_data': {},
            'keyword': keyword,
            'user_id': user_id
        }
        _LOGGER.info(f'[call_find] params: {params}')

        try:
            user_info = self.client.Auth.find(
                params
            )
            _LOGGER.debug(f'[call_find] MessageToDict(user_info): '
                          f'{MessageToDict(user_info, preserving_proto_field_name=True)}')
            return MessageToDict(user_info, preserving_proto_field_name=True)
        except ERROR_BASE as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(message=e.message)
        except Exception as e:
            raise ERROR_AUTHENTICATION_FAILURE_PLUGIN(messsage=str(e))
