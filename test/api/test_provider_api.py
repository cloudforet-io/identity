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
from spaceone.api.identity.v1 import provider_pb2
from spaceone.identity.api.v1.provider import Provider
from test.factory.provider_factory import ProviderFactory


class _MockProviderService(BaseService):

    def create(self, params):
        return ProviderFactory(**params)

    def update(self, params):
        return ProviderFactory(**params)

    def delete(self, params):
        pass

    def get(self, params):
        return ProviderFactory(**params)

    def list(self, params):
        return ProviderFactory.build_batch(10, **params), 10


class TestProviderAPI(unittest.TestCase):

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
    @patch.object(Locator, 'get_service', return_value=_MockProviderService())
    @patch.object(BaseAPI, 'parse_request')
    def test_create_provider(self, mock_parse_request, *args):
        params = {
            'provider': utils.random_string(),
            'name': utils.random_string(),
            'template': {
                'data': [{
                    'key': 'account_id',
                    'name': 'Account ID',
                    'type': 'str',
                    'is_required': True
                }]
            },
            'metadata': {
                'view': {
                    'layouts': {
                        'help:service_account:create': {
                            'name': 'Creation Help',
                            'type': 'markdown',
                            'options': {
                                'markdown': {
                                    'en': (
                                        '### Finding Your AWS Account ID\n'
                                        'You can find your account ID in the AWS Management Console, or using the AWS CLI or AWS API.\n'
                                        '#### Finding your account ID (Console)\n'
                                        'In the navigation bar, choose **Support**, and then **Support Center**. ' 
                                        'Your currently signed-in 12-digit account number (ID) appears in the **Support Center** title bar.\n'
                                    )
                                }
                            }
                        }
                    }
                }
            },
            'capability': {
                'supported_schema': ['schema-aaa', 'schema-bbb']
            },
            'tags': [
                {
                    'key': 'tag_key',
                    'value': 'tag_value'
                }
            ]
        }
        mock_parse_request.return_value = (params, {})

        provider_servicer = Provider()
        provider_info = provider_servicer.create({}, {})

        print_message(provider_info, 'test_create_provider')

        provider_data = MessageToDict(provider_info)
        self.assertIsInstance(provider_info, provider_pb2.ProviderInfo)
        self.assertEqual(provider_info.provider, params['provider'])
        self.assertEqual(provider_info.name, params['name'])
        self.assertDictEqual(MessageToDict(provider_info.template), params['template'])
        self.assertDictEqual(MessageToDict(provider_info.metadata), params['metadata'])
        self.assertDictEqual(MessageToDict(provider_info.capability), params['capability'])
        self.assertListEqual(provider_data['tags'], params['tags'])
        self.assertIsNotNone(getattr(provider_info, 'created_at', None))

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockProviderService())
    @patch.object(BaseAPI, 'parse_request')
    def test_update_provider(self, mock_parse_request, *args):
        params = {
            'provider': utils.random_string(),
            'name': utils.random_string(),
            'tags': [
                {
                    'key': 'update_key',
                    'value': 'update_value'
                }
            ]
        }
        mock_parse_request.return_value = (params, {})

        provider_servicer = Provider()
        provider_info = provider_servicer.update({}, {})

        print_message(provider_info, 'test_update_provider')

        provider_data = MessageToDict(provider_info)
        self.assertIsInstance(provider_info, provider_pb2.ProviderInfo)
        self.assertEqual(provider_info.name, params['name'])
        self.assertListEqual(provider_data['tags'], params['tags'])

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockProviderService())
    @patch.object(BaseAPI, 'parse_request')
    def test_delete_provider(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        provider_servicer = Provider()
        provider_info = provider_servicer.delete({}, {})

        print_message(provider_info, 'test_delete_provider')

        self.assertIsInstance(provider_info, Empty)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockProviderService())
    @patch.object(BaseAPI, 'parse_request')
    def test_get_provider(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        provider_servicer = Provider()
        provider_info = provider_servicer.get({}, {})

        print_message(provider_info, 'test_get_provider')

        self.assertIsInstance(provider_info, provider_pb2.ProviderInfo)

    @patch.object(BaseAPI, '__init__', return_value=None)
    @patch.object(Locator, 'get_service', return_value=_MockProviderService())
    @patch.object(BaseAPI, 'parse_request')
    def test_list_providers(self, mock_parse_request, *args):
        mock_parse_request.return_value = ({}, {})

        provider_servicer = Provider()
        providers_info = provider_servicer.list({}, {})

        print_message(providers_info, 'test_list_provider')

        self.assertIsInstance(providers_info, provider_pb2.ProvidersInfo)
        self.assertIsInstance(providers_info.results[0], provider_pb2.ProviderInfo)
        self.assertEqual(providers_info.total_count, 10)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
