import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestPolicy(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    pp = pprint.PrettyPrinter(indent=4)
    identity_v1 = None
    domain = None
    domain_owner = None
    owner_id = None
    owner_pw = None
    owner_token = None

    @classmethod
    def setUpClass(cls):
        super(TestPolicy, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestPolicy, cls).tearDownClass()
        cls.identity_v1.DomainOwner.delete(
            {
                'domain_id': cls.domain.domain_id,
                'owner_id': cls.owner_id
            },
            metadata=(('token', cls.owner_token),)
        )
        print(f'>> delete domain owner: {cls.owner_id}')

        if cls.domain:
            cls.identity_v1.Domain.delete(
                {
                    'domain_id': cls.domain.domain_id
                },
                metadata=(('token', cls.owner_token),)
            )
            print(f'>> delete domain: {cls.domain.name} ({cls.domain.domain_id})')

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        params = {
            'name': name
        }

        cls.domain = cls.identity_v1.Domain.create(params)
        print(f'domain_id: {cls.domain.domain_id}')
        print(f'domain_name: {cls.domain.name}')

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()
        cls.owner_pw = utils.generate_password()

        owner = cls.identity_v1.DomainOwner.create({
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'domain_id': cls.domain.domain_id
        })

        cls.domain_owner = owner
        print(f'owner_id: {cls.owner_id}')
        print(f'owner_pw: {cls.owner_pw}')

    @classmethod
    def _issue_owner_token(cls):
        token_params = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': cls.owner_id,
            'credentials': {
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_params)
        cls.owner_token = issue_token.access_token

    def setUp(self):
        self.policies = []
        self.policy = None

    def tearDown(self):
        print()
        for policy in self.policies:
            self.identity_v1.Policy.delete(
                {
                    'policy_id': policy.policy_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete policy: {policy.name} ({policy.policy_id})')

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def test_create_policy(self, name=None, **kwargs):
        """ Create Policy
        """

        if name is None:
            name = 'Policy-' + utils.random_string()

        params = {
            'name': name,
            'permissions': [
                'identity.Domain.get',
                'identity.Domain.list',
                'identity.Project.*',
                'identity.ProjectGroup.*',
                'identity.User.get',
                'identity.User.update',
            ],
            'tags': [
                {
                    'key': 'tag_key',
                    'value': 'tag_value'
                }
            ],
            'domain_id': self.domain.domain_id
        }

        metadata = (('token', self.owner_token),)
        ext_meta = kwargs.get('meta')

        if ext_meta:
            metadata += ext_meta

        self.policy = self.identity_v1.Policy.create(
            params,
            metadata=metadata)

        self.policies.append(self.policy)
        self._print_data(self.policy, 'test_create_policy')
        self.assertEqual(self.policy.name, name)

    def test_update_policy(self, name=None):
        """ Update Policy
        """
        update_name = 'Policy-' + utils.random_string()
        update_tags = [
            {
                'key': 'update_key',
                'value': 'update_value'
            }
        ]

        self.test_create_policy()

        self.policy = self.identity_v1.Policy.update(
            {
                'policy_id': self.policy.policy_id,
                'name': update_name,
                'tags': update_tags,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.policy, 'test_update_policy')
        policy_data = MessageToDict(self.policy)
        self.assertEqual(self.policy.name, update_name)
        self.assertEqual(policy_data['tags'], update_tags)

    def test_update_policy_permissions(self):
        """ Update Policy Rules
        """
        update_permissions = ['identity.*']

        self.test_create_policy()

        self.policy = self.identity_v1.Policy.update(
            {
                'policy_id': self.policy.policy_id,
                'permissions': update_permissions,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.policy, 'test_update_policy_permissions')
        policy_info = MessageToDict(self.policy)
        self.assertEqual(policy_info['permissions'], update_permissions)

    def test_get_policy(self):
        self.test_create_policy()

        policy = self.identity_v1.Policy.get(
            {
                'policy_id': self.policy.policy_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(policy.name, self.policy.name)

    def test_get_policy_not_exists(self):
        self.test_create_policy()

        with self.assertRaises(Exception):
            self.identity_v1.Policy.get(
                {
                    'policy_id': 'Guido van Rossum',
                    'domain_id': self.domain.dopmain_id
                },
                metadata=(('token', self.owner_token),)
            )

    def test_delete_policy_not_exists(self):
        self.test_create_policy()

        params = {
            'policy_id': 'hello',
            'domain_id': self.domain.domain_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.Policy.delete(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_list_policy_id(self):
        self.test_create_policy()

        params = {
            'policy_id': self.policy.policy_id,
            'domain_id': self.domain.domain_id
        }

        result = self.identity_v1.Policy.list(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(1, result.total_count)

    def test_list_query(self):
        self.test_create_policy()
        self.test_create_policy()
        self.test_create_policy()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'policy_id',
                        'v': list(map(lambda policy: policy.policy_id, self.policies)),
                        'o': 'in'
                    }
                ]
            }
        }

        result = self.identity_v1.Policy.list(
            params, metadata=(('token', self.owner_token),))

        self.assertEqual(len(self.policies), result.total_count)

    def test_stat_policy(self):
        self.test_list_query()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'policy_id',
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

        result = self.identity_v1.Policy.stat(
            params, metadata=(('token', self.owner_token),))

        self._print_data(result, 'test_stat_policy')


if __name__ == '__main__':
    unittest.main(testRunner=RichTestRunner)
