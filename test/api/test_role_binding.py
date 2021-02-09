import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestRoleBinding(unittest.TestCase):
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
        super(TestRoleBinding, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestRoleBinding, cls).tearDownClass()
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
        self.users = []
        self.user = None
        self.project_groups = []
        self.project_group = None
        self.projects = []
        self.project = None
        self.role_bindings = []
        self.role_binding = None

    def tearDown(self):
        print()
        for role_binding in self.role_bindings:
            self.identity_v1.RoleBinding.delete(
                {
                    'role_binding_id': role_binding.role_binding_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete role_binding: {role_binding.role_binding_id}')

        for project in self.projects:
            self.identity_v1.Project.delete(
                {
                    'project_id': project.project_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete project: {project.name} ({project.project_id})')

        for project_group in reversed(self.project_groups):
            self.identity_v1.ProjectGroup.delete(
                {
                    'project_group_id': project_group.project_group_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete project group: {project_group.name} ({project_group.project_group_id})')

        for user in self.users:
            self.identity_v1.User.delete(
                {
                    'user_id': user.user_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete user: {user.name} ({user.user_id})')

        for role in self.roles:
            self.identity_v1.Role.delete(
                {
                    'role_id': role.role_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )
            print(f'>> delete policy: {role.name} ({role.role_id})')

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
        params = {
            'name': 'Policy-' + utils.random_string(),
            'permissions': permissions or [
                'identity.Domain.get',
                'identity.Domain.list',
                'identity.Project.*',
                'identity.ProjectGroup.*',
                'identity.User.get',
                'identity.User.update',
            ],
            'domain_id': self.domain.domain_id
        }

        self.policy = self.identity_v1.Policy.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.policies.append(self.policy)

    def _test_create_role(self, role_type='DOMAIN', policies=None):
        if self.policy is None:
            self._test_create_policy()

        params = {
            'name': 'Role-' + utils.random_string(),
            'role_type': role_type,
            'policies': policies or [{
                'policy_type': 'CUSTOM',
                'policy_id': self.policy.policy_id
            }],
            'domain_id': self.domain.domain_id
        }

        self.role = self.identity_v1.Role.create(
            params,
            metadata=(('token', self.owner_token),))

        self.roles.append(self.role)

    def _test_create_user(self, name=None, user_id=None):
        if self.role is None:
            self._test_create_role()

        if user_id is None:
            user_id = utils.random_string() + '@mz.co.kr'

        params = {
            'user_id': user_id,
            'domain_id': self.domain.domain_id,
            'password': utils.generate_password(),
            'name': name or 'test' + utils.random_string(),
            'timezone': 'Asia/Seoul',
            'email': user_id
        }

        self.user = self.identity_v1.User.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.users.append(self.user)

        return self.user

    def _test_create_project_group(self):
        params = {
            'name': utils.random_string(),
            'domain_id': self.domain.domain_id
        }

        self.project_group = self.identity_v1.ProjectGroup.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.project_groups.append(self.project_group)

    def _test_create_project(self, project_group_id=None):
        if project_group_id is None:
            self._test_create_project_group()

        params = {
            'name': utils.random_string(),
            'domain_id': self.domain.domain_id
        }

        if project_group_id is None:
            params['project_group_id'] = self.project_group.project_group_id
        else:
            params['project_group_id'] = project_group_id

        self.project = self.identity_v1.Project.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.projects.append(self.project)

    def test_create_domain_role_binding(self):
        self._test_create_user()
        self._test_create_role('DOMAIN')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_domain_role_binding')
        self.role_bindings.append(self.role_binding)
        self.assertEqual(self.role_binding.resource_type, 'identity.User')
        self.assertEqual(self.role_binding.resource_id, self.user.user_id)
        self.assertEqual(self.role_binding.role_info.role_id, self.role.role_id)

    def test_create_duplicate_domain_role_binding(self):
        self._test_create_user()
        self._test_create_role('DOMAIN')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_duplicate_domain_role_binding')

        with self.assertRaisesRegex(Exception, 'ERROR_DUPLICATE_ROLE_BOUND'):
            self.role_binding = self.identity_v1.RoleBinding.create(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_create_system_role_binding(self):
        self._test_create_user()
        self._test_create_role('SYSTEM')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_system_role_binding')
        self.role_bindings.append(self.role_binding)
        self.assertEqual(self.role_binding.resource_type, 'identity.User')
        self.assertEqual(self.role_binding.resource_id, self.user.user_id)
        self.assertEqual(self.role_binding.role_info.role_id, self.role.role_id)

    def test_create_duplicate_system_role_binding(self):
        self._test_create_user()
        self._test_create_role('SYSTEM')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_duplicate_system_role_binding')

        with self.assertRaisesRegex(Exception, 'ERROR_DUPLICATE_ROLE_BOUND'):
            self.role_binding = self.identity_v1.RoleBinding.create(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_create_project_role_binding_with_project_id(self):
        self._test_create_user()
        self._test_create_role('PROJECT')
        self._test_create_project()

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'project_id': self.project.project_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_project_role_binding_with_project_id')
        self.role_bindings.append(self.role_binding)
        self.assertEqual(self.role_binding.resource_type, 'identity.User')
        self.assertEqual(self.role_binding.resource_id, self.user.user_id)
        self.assertEqual(self.role_binding.role_info.role_id, self.role.role_id)
        self.assertEqual(self.role_binding.project_info.project_id, self.project.project_id)

    def test_create_project_duplicate_project_role_binding(self):
        self._test_create_user()
        self._test_create_role('PROJECT')
        self._test_create_project()

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'project_id': self.project.project_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_project_duplicate_project_role_binding')

        with self.assertRaisesRegex(Exception, 'ERROR_DUPLICATE_RESOURCE_IN_PROJECT'):
            self.role_binding = self.identity_v1.RoleBinding.create(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_create_project_role_binding_with_project_group_id(self):
        self._test_create_user()
        self._test_create_role('PROJECT')
        self._test_create_project_group()

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'project_group_id': self.project_group.project_group_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_project_role_binding_with_project_group_id')
        self.role_bindings.append(self.role_binding)
        self.assertEqual(self.role_binding.resource_type, 'identity.User')
        self.assertEqual(self.role_binding.resource_id, self.user.user_id)
        self.assertEqual(self.role_binding.role_info.role_id, self.role.role_id)
        self.assertEqual(self.role_binding.project_group_info.project_group_id, self.project_group.project_group_id)

    def test_create_project_duplicate_project_group_role_binding(self):
        self._test_create_user()
        self._test_create_role('PROJECT')
        self._test_create_project_group()

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'role_id': self.role.role_id,
            'project_group_id': self.project_group.project_group_id,
            'labels': ['aaa', 'bbb'],
            'domain_id': self.domain.domain_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_create_project_duplicated_project_group_role_binding')

        with self.assertRaisesRegex(Exception, 'ERROR_DUPLICATE_RESOURCE_IN_PROJECT_GROUP'):
            self.role_binding = self.identity_v1.RoleBinding.create(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_update_role_binding(self):
        self.test_create_domain_role_binding()

        labels = ['developer', 'operator']

        self.role_binding = self.identity_v1.RoleBinding.update(
            {
                'role_binding_id': self.role_binding.role_binding_id,
                'labels': labels,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.role_binding, 'test_update_role_binding')

        self.assertEqual(sorted(self.role_binding.labels), sorted(labels))

    def test_get_role_binding(self):
        self.test_create_domain_role_binding()

        role_binding = self.identity_v1.RoleBinding.get(
            {
                'role_binding_id': self.role_binding.role_binding_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(role_binding.role_binding_id, self.role_binding.role_binding_id)

    def test_delete_role_binding_not_exists(self):
        self.test_create_domain_role_binding()

        params = {
            'role_binding_id': 'hello',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Role.delete(
                params,
                metadata=(('token', self.owner_token),)
            )

    def test_list_role_binding_id(self):
        self.test_create_domain_role_binding()

        params = {
            'role_binding_id': self.role_binding.role_binding_id,
            'domain_id': self.domain.domain_id
        }

        result = self.identity_v1.RoleBinding.list(
            params,
            metadata=(('token', self.owner_token),)
        )

        self.assertEqual(1, result.total_count)

    def test_list_role_bindings(self):
        self.test_create_domain_role_binding()
        self.test_create_domain_role_binding()
        self.test_create_domain_role_binding()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'filter': [
                    {
                        'k': 'role_binding_id',
                        'v': list(map(lambda role_binding: role_binding.role_binding_id, self.role_bindings)),
                        'o': 'in'
                    }
                ]
            }
        }

        result = self.identity_v1.RoleBinding.list(
            params, metadata=(('token', self.owner_token),))

        self.assertEqual(len(self.role_bindings), result.total_count)

    def test_stat_role_binding(self):
        self.test_list_role_bindings()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': [{
                    'group': {
                        'keys': [{
                            'key': 'role_binding_id',
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

        result = self.identity_v1.RoleBinding.stat(
            params, metadata=(('token', self.owner_token),))

        self._print_data(result, 'test_stat_role_binding')


if __name__ == '__main__':
    unittest.main(testRunner=RichTestRunner)
