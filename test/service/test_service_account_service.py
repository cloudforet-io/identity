import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.core.transaction import Transaction
from spaceone.identity.service.service_account_service import ServiceAccountService
from spaceone.identity.model.service_account_model import ServiceAccount
from spaceone.identity.model.project_model import Project
from spaceone.identity.info.service_account_info import *
from spaceone.identity.info.common_info import StatisticsInfo
from spaceone.identity.connector import SecretConnector
from test.factory.service_account_factory import ServiceAccountFactory
from test.factory.provider_factory import ProviderFactory
from test.factory.project_factory import ProjectFactory


class TestServiceAccountService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.identity')
        connect('test', host='mongomock://localhost')
        ProviderFactory(provider='aws', name='AWS', template={
            'service_account': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'account_id': {
                            'title': 'Account ID',
                            'type': 'string'
                        }
                    },
                    'required': ['account_id']
                }
            }
        })
        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'identity',
            'api_class': 'ServiceAccount'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    def setUp(self) -> None:
        self.project_vo = ProjectFactory(domain_id=self.domain_id)
        self.project_id = self.project_vo.project_id

    @patch.object(MongoModel, 'connect', return_value=None)
    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all service accounts')
        service_account_vos = ServiceAccount.objects.filter()
        service_account_vos.delete()

        print('(tearDown) ==> Delete project')
        self.project_vo.delete()

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_service_account(self, *args):
        params = {
            'name': 'SpaceONE',
            'provider': 'aws',
            'data': {
                'account_id': '000321654'
            },
            'tags': [
                {
                    'key': 'tag_key',
                    'value': 'tag_value'
                }
            ],
            'domain_id': utils.generate_id('domain')
        }

        self.transaction.method = 'create'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.create(params.copy())

        print_data(service_account_vo.to_dict(), 'test_create_service_account')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)
        self.assertEqual(params['name'], service_account_vo.name)
        self.assertEqual(params['provider'], service_account_vo.provider)
        self.assertEqual(params['domain_id'], service_account_vo.domain_id)
        self.assertEqual(params.get('data', {}), service_account_vo.data)
        self.assertEqual(params.get('tags', {}), service_account_vo.to_dict()['tags'])

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_service_account_invalid_data(self, *args):
        params = {
            'name': 'SpaceONE',
            'provider': 'aws',
            'data': {
                'account_id2': '000321654'
            },
            'domain_id': utils.generate_id('domain')
        }

        self.transaction.method = 'create'
        service_account_svc = ServiceAccountService(transaction=self.transaction)

        with self.assertRaises(ERROR_INVALID_PARAMETER):
            service_account_svc.create(params)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_service_account_invalid_data_type(self, *args):
        params = {
            'name': 'SpaceONE',
            'provider': 'aws',
            'data': {
                'account_id': 32
            },
            'domain_id': utils.generate_id('domain')
        }

        self.transaction.method = 'create'
        service_account_svc = ServiceAccountService(transaction=self.transaction)

        with self.assertRaises(ERROR_INVALID_PARAMETER):
            service_account_svc.create(params)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_create_service_account_with_project(self, *args):
        params = {
            'name': 'SpaceONE',
            'provider': 'aws',
            'data': {
                'account_id': '000321654'
            },
            'project_id': self.project_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.create(params.copy())

        print_data(service_account_vo.to_dict(), 'test_create_service_account_with_project')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)
        self.assertIsInstance(service_account_vo.project, Project)
        self.assertEqual(service_account_vo.project.project_id, params['project_id'])

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_update_service_account(self, *args):
        new_service_account_vo = ServiceAccountFactory(domain_id=self.domain_id)
        params = {
            'service_account_id': new_service_account_vo.service_account_id,
            'name': 'Update Account Name',
            'data': {
                'account_id': 'update-1234'
            },
            'tags': [
                {
                    'key': 'update_key',
                    'value': 'update_value'
                }
            ],
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.update(params.copy())

        print_data(service_account_vo.to_dict(), 'test_update_service_account')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)
        self.assertEqual(new_service_account_vo.service_account_id, service_account_vo.service_account_id)
        self.assertEqual(params['name'], service_account_vo.name)
        self.assertEqual(params['data'], service_account_vo.data)
        self.assertEqual(params['tags'], service_account_vo.to_dict()['tags'])

    @patch.object(MongoModel, 'connect', return_value=None)
    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'list_secrets', return_value={'results': [], 'total_count': 0})
    @patch.object(SecretConnector, 'update_secret_project', return_value=None)
    def test_update_service_account_project(self, *args):
        new_service_account_vo = ServiceAccountFactory(domain_id=self.domain_id)
        params = {
            'service_account_id': new_service_account_vo.service_account_id,
            'project_id': self.project_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.update(params.copy())

        print_data(service_account_vo.to_dict(), 'test_update_service_account_project')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)
        self.assertIsInstance(service_account_vo.project, Project)
        self.assertEqual(service_account_vo.project.project_id, params['project_id'])

    @patch.object(MongoModel, 'connect', return_value=None)
    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'list_secrets', return_value={'results': [], 'total_count': 0})
    @patch.object(SecretConnector, 'release_secret_project', return_value=None)
    def test_release_service_account_project(self, *args):
        new_service_account_vo = ServiceAccountFactory(domain_id=self.domain_id, project=self.project_vo)
        params = {
            'service_account_id': new_service_account_vo.service_account_id,
            'release_project': True,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'update'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.update(params.copy())

        print_data(service_account_vo.to_dict(), 'test_release_service_account_project')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)
        self.assertIsNone(service_account_vo.project)

    @patch.object(MongoModel, 'connect', return_value=None)
    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'list_secrets', return_value={'results': [], 'total_count': 0})
    @patch.object(SecretConnector, 'delete_secret', return_value=None)
    def test_delete_service_account(self, *args):
        new_service_account_vo = ServiceAccountFactory(domain_id=self.domain_id)
        params = {
            'service_account_id': new_service_account_vo.service_account_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        result = service_account_svc.delete(params)

        self.assertIsNone(result)

    @patch.object(MongoModel, 'connect', return_value=None)
    @patch.object(SecretConnector, '__init__', return_value=None)
    @patch.object(SecretConnector, 'list_secrets', return_value={'results': [], 'total_count': 0})
    @patch.object(SecretConnector, 'delete_secret', return_value=None)
    def test_delete_project_exist_service_account(self, *args):
        params = {
            'name': 'SpaceONE',
            'provider': 'aws',
            'data': {
                'account_id': '000321654'
            },
            'project_id': self.project_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'create'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.create(params.copy())
        ServiceAccountInfo(service_account_vo)

        with self.assertRaises(ERROR_EXIST_RESOURCE):
            self.project_vo.delete()

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_get_service_account(self, *args):
        new_service_account_vo = ServiceAccountFactory(domain_id=self.domain_id)
        params = {
            'service_account_id': new_service_account_vo.service_account_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        service_account_vo = service_account_svc.get(params)

        print_data(service_account_vo.to_dict(), 'test_get_service_account')
        ServiceAccountInfo(service_account_vo)

        self.assertIsInstance(service_account_vo, ServiceAccount)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_service_accounts_by_service_account_id(self, *args):
        service_account_vos = ServiceAccountFactory.build_batch(10, project=None,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        params = {
            'service_account_id': service_account_vos[0].service_account_id,
            'domain_id': self.domain_id
        }

        service_account_svc = ServiceAccountService()
        service_accounts_vos, total_count = service_account_svc.list(params)

        ServiceAccountsInfo(service_account_vos, total_count)

        self.assertEqual(len(service_accounts_vos), 1)
        self.assertIsInstance(service_accounts_vos[0], ServiceAccount)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_service_accounts_by_name(self, *args):
        service_account_vos = ServiceAccountFactory.build_batch(10, project=None,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        params = {
            'name': service_account_vos[0].name,
            'domain_id': self.domain_id
        }

        service_account_svc = ServiceAccountService()
        service_accounts_vos, total_count = service_account_svc.list(params)

        ServiceAccountsInfo(service_account_vos, total_count)

        self.assertEqual(len(service_accounts_vos), 1)
        self.assertIsInstance(service_accounts_vos[0], ServiceAccount)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_service_accounts_by_project(self, *args):
        service_account_vos = ServiceAccountFactory.build_batch(3, project=self.project_vo,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        service_account_vos = ServiceAccountFactory.build_batch(7, project=None,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        params = {
            'project_id': self.project_id,
            'domain_id': self.domain_id
        }

        service_account_svc = ServiceAccountService()
        service_accounts_vos, total_count = service_account_svc.list(params)

        ServiceAccountsInfo(service_account_vos, total_count)

        self.assertEqual(len(service_accounts_vos), 3)
        self.assertIsInstance(service_accounts_vos[0], ServiceAccount)
        self.assertEqual(total_count, 3)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_list_service_accounts_by_tag(self, *args):
        ServiceAccountFactory(tags=[{'key': 'tag_key_1', 'value': 'tag_value_1'}], domain_id=self.domain_id)
        service_account_vos = ServiceAccountFactory.build_batch(9, project=None,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        params = {
            'query': {
                'filter': [{
                    'k': 'tags.tag_key_1',
                    'v': 'tag_value_1',
                    'o': 'eq'
                }]
            },
            'domain_id': self.domain_id
        }

        service_account_svc = ServiceAccountService()
        service_accounts_vos, total_count = service_account_svc.list(params)

        ServiceAccountsInfo(service_account_vos, total_count)

        self.assertEqual(len(service_accounts_vos), 1)
        self.assertIsInstance(service_accounts_vos[0], ServiceAccount)
        self.assertEqual(total_count, 1)

    @patch.object(MongoModel, 'connect', return_value=None)
    def test_stat_service_account(self, *args):
        service_account_vos = ServiceAccountFactory.build_batch(10, project=None,
                                                                domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), service_account_vos))

        params = {
            'domain_id': self.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'service_account_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }, {
                            'key': 'project.project_id',
                            'name': 'project_count',
                            'operator': 'size'
                        }]
                    }
                },
                'sort': {
                    'name': 'Count',
                    'desc': True
                }
            }
        }

        self.transaction.method = 'stat'
        service_account_svc = ServiceAccountService(transaction=self.transaction)
        values = service_account_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_service_account')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
