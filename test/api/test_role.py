import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestRole(unittest.TestCase):
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
        super(TestRole, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestRole, cls).tearDownClass()
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
        self.roles = []
        self.role = None

    def tearDown(self):
        print()
        for role in self.roles:
            self.identity_v1.Role.delete(
                {
                    'role_id': role.role_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete role: {role.name} ({role.role_id})')

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

    def _test_create_policy(self, permissions=None):
        if permissions is None:
            permissions = [
                'identity.Domain.get',
                'identity.Domain.list',
                'identity.Project.*',
                'identity.ProjectGroup.*',
                'identity.User.get',
                'identity.User.update',
            ]

        params = {
            'name': 'Policy-' + utils.random_string(),
            'permissions': permissions,
            'domain_id': self.domain.domain_id
        }

        self.policy = self.identity_v1.Policy.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.policies.append(self.policy)

    def test_create_role(self, name=None, **kwargs):
        """ Create Role
        """

        if name is None:
            name = 'Role-' + utils.random_string()

        self._test_create_policy()
        self._test_create_policy(['inventory.*'])

        params = {
            'name': name,
            'role_type': 'PROJECT',
            'policies': list(map(lambda policy: {
                'policy_id': policy.policy_id,
                'policy_type': 'CUSTOM'
            }, self.policies)),
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

        self.role = self.identity_v1.Role.create(
            params,
            metadata=metadata)

        self.roles.append(self.role)
        self._print_data(self.role, 'test_create_role')
        self.assertEqual(self.role.name, name)

    def test_update_role(self, name=None):
        """ Update Role
        """
        update_name = 'Role-' + utils.random_string()
        update_tags = [
            {
                'key': 'update_key',
                'value': 'update_value'
            }
        ]

        self.test_create_role()

        self.role = self.identity_v1.Role.update(
            {
                'role_id': self.role.role_id,
                'name': update_name,
                'tags': update_tags,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role, 'test_update_role')
        role_data = MessageToDict(self.role)

        self.assertEqual(self.role.name, update_name)
        self.assertEqual(role_data['tags'], update_tags)

    def test_update_role_policies(self):
        """ Update Role Policies
        """
        self.test_create_role()
        self._test_create_policy(['identity.*'])

        update_policies = list(map(lambda policy: {
            'policy_id': policy.policy_id,
            'policy_type': 'CUSTOM'
        }, self.policies))

        self.role = self.identity_v1.Role.update(
            {
                'role_id': self.role.role_id,
                'policies': update_policies,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.policy, 'test_update_role_policies')
        role_info = MessageToDict(self.role, preserving_proto_field_name=True)
        self.assertEqual(role_info['policies'], update_policies)

    def test_get_role(self):
        self.test_create_role()

        role = self.identity_v1.Role.get(
            {
                'role_id': self.role.role_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(role.name, self.role.name)

    def test_delete_role_not_exists(self):
        self.test_create_role()

        params = {
            'role_id': 'hello',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Role.delete(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_list_role_id(self):
        self.test_create_role()

        params = {
            'role_id': self.role.role_id,
            'domain_id': self.domain.domain_id
        }

        result = self.identity_v1.Role.list(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(1, result.total_count)

    def test_list_roles(self):
        self.test_create_role()
        self.test_create_role()
        self.test_create_role()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'role_id',
                        'v': list(map(lambda role: role.role_id, self.roles)),
                        'o': 'in'
                    }
                ]
            }
        }

        result = self.identity_v1.Role.list(
            params, metadata=(('token', self.owner_token),))

        self.assertEqual(len(self.roles), result.total_count)

    def test_stat_role(self):
        self.test_list_roles()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'role_id',
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

        result = self.identity_v1.Role.stat(
            params, metadata=(('token', self.owner_token),))

        self._print_data(result, 'test_stat_role')


if __name__ == '__main__':
    unittest.main(testRunner=RichTestRunner)
