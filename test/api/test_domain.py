import os
import unittest

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestDomain(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    @classmethod
    def setUpClass(cls):
        super(TestDomain, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestDomain, cls).tearDownClass()

    def setUp(self):
        endpoints = self.config.get('ENDPOINTS', {})
        self.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                         version='v1')

        self.domain = None
        self.owner_id = 'DomainOwner'
        self.owner_pw = utils.generate_password()
        self.owner = None
        self.owner_token = None

    def tearDown(self):
        if self.owner:
            self.identity_v1.DomainOwner.delete(
                {
                    'domain_id': self.domain.domain_id,
                    'owner_id': self.owner_id
                },
                metadata=(('token', self.owner_token),)
            )

        if self.domain:
            print(f'[TearDown] Delete domain. (domain_id: {self.domain.domain_id}')
            self.identity_v1.Domain.delete(
                {
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

    def _create_domain_owner(self):
        params = {
            'owner_id': self.owner_id,
            'password': self.owner_pw,
            'domain_id': self.domain.domain_id
        }

        self.owner = self.identity_v1.DomainOwner.create(
            params
        )

    def _issue_owner_token(self):
        token_params = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': self.owner_id,
            'credentials': {
                'password': self.owner_pw
            },
            'domain_id': self.domain.domain_id
        }

        issue_token = self.identity_v1.Token.issue(token_params)
        self.owner_token = issue_token.access_token

    def test_create_domain(self):
        """ Create Domain
        """
        name = utils.random_string()
        params = {
            'name': name,
            'tags': [
                {
                    'key': utils.random_string(4),
                    'value': utils.random_string(4)
                }, {
                    'key': utils.random_string(4),
                    'value': utils.random_string(4)
                }
            ]
        }
        self.domain = self.identity_v1.Domain.create(params)
        self.assertEqual(self.domain.name, name)

        self._create_domain_owner()
        self._issue_owner_token()

    def test_update_domain_tag(self):
        """ Update domain tag
        """
        self.test_create_domain()

        tags = [
            {
                'key': 'a',
                'value': '123'
            }
        ]
        params = {'domain_id': self.domain.domain_id, 'tags': tags}
        self.domain = self.identity_v1.Domain.update(
            params,
            metadata=(('token', self.owner_token),)
        )
        domain_info = MessageToDict(self.domain)
        self.assertEqual(domain_info['tags'], tags)

    def test_update_domain_config(self):
        """ Update domain config
        """
        self.test_create_domain()
        config = {'TEST': 'BLAH-BLAH'}
        params = {'domain_id': self.domain.domain_id, 'config': config}
        self.domain = self.identity_v1.Domain.update(
            params,
            metadata=(('token', self.owner_token),)
        )
        domain_info = MessageToDict(self.domain)
        self.assertEqual(domain_info['config'], config)

    def test_enable_domain(self):
        """ enable Domain
        """
        self.test_create_domain()

        self.domain = self.identity_v1.Domain.enable(
            {'domain_id': self.domain.domain_id},
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(self.domain.state, 1)

    def test_disable_domain(self):
        """ disable Domain
        """
        self.test_create_domain()

        self.domain = self.identity_v1.Domain.disable(
            {'domain_id': self.domain.domain_id},
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(self.domain.state, 2)

    def test_get_domain(self):
        """ Get Domain
        """
        self.test_create_domain()

        domain = self.identity_v1.Domain.get(
            {'domain_id': self.domain.domain_id},
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(self.domain.name, domain.name)

    def test_list_domains(self):
        """ list Domains
        """
        self.test_create_domain()

        params = {
            'query': {
                'filter': [
                    {'k': 'state', 'v': 'ENABLED', 'o': 'eq'}
                ]
            }, 'name': self.domain.name
        }

        result = self.identity_v1.Domain.list(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(result.total_count, 1)

    def test_list_domains_query_filter(self):
        self.test_create_domain()

        params = {
            'name': self.domain.name
        }

        result = self.identity_v1.Domain.list(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(result.total_count, 1)

    def test_stat_domain(self):
        self.test_list_domains()

        params = {
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'domain_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                }, {
                    'sort': {
                        'key': 'Count',
                        'desc': True
                    }
                }]
            }
        }

        result = self.identity_v1.Domain.stat(
            params, metadata=(('token', self.owner_token),))

        print(result)

    def test_stat_domain_distinct(self):
        self.test_list_domains()

        params = {
            'query': {
                'distinct': 'name',
                'page': {
                    'start': 2,
                    'limit': 3
                }
            }
        }

        result = self.identity_v1.Domain.stat(
            params, metadata=(('token', self.owner_token),))

        print(result)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
