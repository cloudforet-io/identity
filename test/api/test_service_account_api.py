import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect
from google.protobuf.json_format import MessageToDict
from google.protobuf.empty_pb2 import Empty

from spaceone.core.unittest.result import print_message
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.service import BaseService
from spaceone.core.locator import Locator
from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v1 import service_account_pb2
from spaceone.identity.api.v1.service_account import ServiceAccount
from test.factory.service_account_factory import ServiceAccountFactory


class _MockServiceAccountService(BaseService):

    def create(self, params):
        return ServiceAccountFactory(**params)

    def update(self, params):
        return ServiceAccountFactory(**params)

    def delete(self, params):
        pass

    def get(self, params):
        return ServiceAccountFactory(**params)

    def list(self, params):
        return ServiceAccountFactory.build_batch(10, **params), 10


class TestServiceAccountAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.identity')
        connect('test', host='mongomock://localhost')
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockServiceAccountService())
    @patch.object(BaseAPI, 'parse_request')
    def test_create_service_account(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'data': {
                'account_id': '000123456'
            },
            'provider': 'aws',
            'tags': [
                {
                    'key': 'tag_key',
                    'value': 'tag_value'
                }
            ],
            'domain_id': utils.generate_id('domain')
        }
        mock_parse_request.return_value = (params, {})

        service_account_servicer = ServiceAccount()
        service_account_info = service_account_servicer.create({}, {})

        print_message(service_account_info, 'test_create_service_account')

        service_account_data = MessageToDict(service_account_info)
        self.assertIsInstance(service_account_info, service_account_pb2.ServiceAccountInfo)
        self.assertEqual(service_account_info.name, params['name'])
        self.assertDictEqual(MessageToDict(service_account_info.data), params['data'])
        self.assertListEqual(service_account_data['tags'], params['tags'])
        self.assertEqual(service_account_info.domain_id, params['domain_id'])
        self.assertIsNotNone(getattr(service_account_info, 'created_at', None))

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockServiceAccountService())
    @patch.object(BaseAPI, 'parse_request')
    def test_update_service_account(self, mock_parse_request, *args):
        params = {
            'name': utils.random_string(),
            'tags': [
                {
                    'key': 'update_key',
                    'value': 'update_value'
                }
            ]
        }
        mock_parse_request.return_value = (params, {})

        service_account_servicer = ServiceAccount()
        service_account_info = service_account_servicer.update({}, {})

        print_message(service_account_info, 'test_update_service_account')

        service_account_data = MessageToDict(service_account_info)
        self.assertIsInstance(service_account_info, service_account_pb2.ServiceAccountInfo)
        self.assertEqual(service_account_info.name, params['name'])
        self.assertListEqual(service_account_data['tags'], params['tags'])

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockServiceAccountService())
    @patch.object(BaseAPI, 'parse_request')
    def test_delete_service_account(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        service_account_servicer = ServiceAccount()
        service_account_info = service_account_servicer.delete({}, {})

        print_message(service_account_info, 'test_delete_service_account')

        self.assertIsInstance(service_account_info, Empty)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockServiceAccountService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_service_account(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        service_account_servicer = ServiceAccount()
        service_account_info = service_account_servicer.get({}, {})

        print_message(service_account_info, 'test_get_service_account')

        self.assertIsInstance(service_account_info, service_account_pb2.ServiceAccountInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockServiceAccountService())
    @patch.object(BaseAPI, 'parse_request')
    def test_list_service_accounts(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        service_account_servicer = ServiceAccount()
        service_accounts_info = service_account_servicer.list({}, {})

        print_message(service_accounts_info, 'test_list_service_account')

        self.assertIsInstance(service_accounts_info, service_account_pb2.ServiceAccountsInfo)
        self.assertIsInstance(service_accounts_info.results[0], service_account_pb2.ServiceAccountInfo)
        self.assertEqual(service_accounts_info.total_count, 10)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
