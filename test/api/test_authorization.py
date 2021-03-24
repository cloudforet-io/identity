import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestAuthorization(unittest.TestCase):
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
    def setUpClass(cls) -> None:
        super(TestAuthorization, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls) -> None:
        super(TestAuthorization, cls).tearDownClass()
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
            'name': name,
            'config': {
                'config_key': 'config_value'
            }
        }
        cls.domain = cls.identity_v1.Domain.create(params)

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
        token_param = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': cls.owner_id,
            'credentials': {
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_param)
        cls.owner_token = issue_token.access_token

    def setUp(self) -> None:
        self.policy = None
        self.policies = []
        self.role = None
        self.roles = []
        self.user = None
        self.users = []
        self.project_groups = []
        self.project_group = None
        self.projects = []
        self.project = None
        self.role_binding = None
        self.role_bindings = []

    def tearDown(self) -> None:
        print()
        for role_binding in self.role_bindings:
            print(f'[tearDown] Delete Role Binding. {role_binding.role_binding_id}')
            self.identity_v1.RoleBinding.delete({
                'role_binding_id': role_binding.role_binding_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

        for project in self.projects:
            print(f'>> delete project: {project.name} ({project.project_id})')
            self.identity_v1.Project.delete({
                'project_id': project.project_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

        for project_group in reversed(self.project_groups):
            print(f'>> delete project group: {project_group.name} ({project_group.project_group_id})')
            self.identity_v1.ProjectGroup.delete({
                'project_group_id': project_group.project_group_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

        for user in self.users:
            print(f'[tearDown] Delete User. {user.user_id}')
            self.identity_v1.User.delete({
                'user_id': user.user_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

        for role in self.roles:
            print(f'[tearDown] Delete Role. {role.role_id}')
            self.identity_v1.Role.delete({
                'role_id': role.role_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

        for policy in self.policies:
            print(f'[tearDown] Delete Policy. {policy.policy_id}')
            self.identity_v1.Policy.delete({
                'policy_id': policy.policy_id,
                'domain_id': self.domain.domain_id
            }, metadata=(('token', self.owner_token),))

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def _test_create_policy(self, permissions):
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

    def _test_create_role(self, policies, role_type='PROJECT'):
        params = {
            'name': 'Role-' + utils.random_string(),
            'role_type': role_type,
            'policies': policies,
            'domain_id': self.domain.domain_id
        }

        self.role = self.identity_v1.Role.create(
            params,
            metadata=(('token', self.owner_token),))

        self.roles.append(self.role)

    def _test_create_user(self, user_id=None):
        if user_id is None:
            user_id = utils.random_string() + '@mz.co.kr'

        self.user_password = utils.generate_password()

        params = {
            'user_id': user_id,
            'password': self.user_password,
            'name': utils.random_string(),
            'domain_id': self.domain.domain_id
        }

        self.user = self.identity_v1.User.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.users.append(self.user)

    def _test_create_project_group(self, project_group_id=None):
        params = {
            'name': utils.random_string(),
            'domain_id': self.domain.domain_id,
            'parent_project_group_id': project_group_id
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

    def _test_create_domain_role_binding(self, permissions=None):
        if permissions is None:
            permissions = ['*']

        self._test_create_policy(permissions)
        self._test_create_role([{
            'policy_type': 'CUSTOM',
            'policy_id': self.policy.policy_id}], 'DOMAIN')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'domain_id': self.domain.domain_id,
            'role_id': self.role.role_id
        }
        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.role_bindings.append(self.role_binding)
        self._print_data(self.user, '_test_create_domain_role_binding')

    def _test_create_system_role_binding(self, permissions=None):
        if permissions is None:
            permissions = ['*']

        self._test_create_policy(permissions)
        self._test_create_role([{
            'policy_type': 'CUSTOM',
            'policy_id': self.policy.policy_id}], 'SYSTEM')

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'domain_id': self.domain.domain_id,
            'role_id': self.role.role_id
        }
        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.role_bindings.append(self.role_binding)
        self._print_data(self.user, '_test_create_system_role_binding')

    def _test_create_project_role_binding(self, project_id=None, project_group_id=None, permissions=None):
        if permissions is None:
            permissions = ['*']

        self._test_create_policy(permissions)

        self._test_create_role(
            [{
                'policy_type': 'CUSTOM',
                'policy_id': self.policy.policy_id
            }], 'PROJECT'
        )

        params = {
            'resource_type': 'identity.User',
            'resource_id': self.user.user_id,
            'domain_id': self.domain.domain_id,
            'role_id': self.role.role_id,
            'project_id': project_id,
            'project_group_id': project_group_id
        }

        self.role_binding = self.identity_v1.RoleBinding.create(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.role_bindings.append(self.role_binding)
        self._print_data(self.user, '_test_create_project_role_binding')

    def _test_issue_user_token(self):
        token_params = {
            'user_type': 'USER',
            'user_id': self.user.user_id,
            'credentials': {
                'password': self.user_password
            },
            'domain_id': self.domain.domain_id
        }

        response = self.identity_v1.Token.issue(token_params)
        self.user_token = response.access_token

    def test_authorization_verify_no_roles(self):
        self._test_create_user()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN'
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_no_roles_access_default_permissions_my_id(self):
        self._test_create_user()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'get',
            'scope': 'DOMAIN',
            'user_id': self.user.user_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_no_roles_access_default_permissions')
        self.assertEqual('USER', response.role_type)

    def test_authorization_verify_no_roles_access_default_permissions_other_id(self):
        self._test_create_user()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'get',
            'scope': 'DOMAIN',
            'user_id': utils.random_string() + '@mz.co.kr'
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_domain_role_no_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding(['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN'
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_domain_role_with_no_domain_id(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN'
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_domain_role_with_no_domain_id')
        self.assertEqual('DOMAIN', response.role_type)

    def test_authorization_verify_domain_role_with_same_domain_id(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN',
            'domain_id': self.domain.domain_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_domain_role_with_same_domain_id')
        self.assertEqual('DOMAIN', response.role_type)

    def test_authorization_verify_domain_role_with_other_domain_id(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN',
            'domain_id': utils.generate_id('domain')
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_system_role_no_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding(['identity.Domain.get_public_key'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN'
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_domain_role_access_system_api(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'SYSTEM',
            'domain_id': utils.generate_id('domain')
        }

        # with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
        #     self.identity_v1.Authorization.verify(
        #         params,
        #         metadata=(('token', self.user_token),))

    def test_authorization_verify_domain_role_access_project_api_not_in_project(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': utils.generate_id('project')
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_domain_role_access_project_api_not_in_project')
        self.assertEqual('DOMAIN', response.role_type)

    def test_authorization_verify_domain_role_access_project_api_in_project_has_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id,
                                               permissions=['identity.User.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_domain_role_access_project_api_in_project_has_permissions')
        self.assertEqual('DOMAIN', response.role_type)

    def test_authorization_verify_domain_role_access_project_api_in_project_group_has_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_create_project()
        self._test_create_project_role_binding(project_group_id=self.project_group.project_group_id,
                                               permissions=['identity.User.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_domain_role_access_project_api_in_project_group_has_permissions')
        self.assertEqual('DOMAIN', response.role_type)

    def test_authorization_verify_domain_role_access_project_api_override_no_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_create_project()
        self._test_create_project_role_binding(project_group_id=self.project_group.project_group_id,
                                               permissions=['identity.User.*'])
        self._test_create_project_role_binding(project_id=self.project.project_id,
                                               permissions=['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_domain_role_access_project_api_in_project_no_permissions(self):
        self._test_create_user()
        self._test_create_domain_role_binding()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id,
                                               permissions=['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_system_role_with_no_domain_id(self):
        self._test_create_user()
        self._test_create_system_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'SYSTEM'
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_system_role_with_no_domain_id')
        self.assertEqual('SYSTEM', response.role_type)

    def test_authorization_verify_system_role_with_other_domain_id(self):
        self._test_create_user()
        self._test_create_system_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'SYSTEM',
            'domain_id': utils.generate_id('domain')
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_system_role_with_other_domain_id')
        self.assertEqual('SYSTEM', response.role_type)

    def test_authorization_verify_system_role_access_domain_api(self):
        self._test_create_user()
        self._test_create_system_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN',
            'domain_id': utils.generate_id('domain')
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_system_role_access_domain_api')
        self.assertEqual('SYSTEM', response.role_type)

    def test_authorization_verify_system_role_access_project_api(self):
        self._test_create_user()
        self._test_create_system_role_binding()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'domain_id': utils.generate_id('domain')
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_system_role_access_project_api')
        self.assertEqual('SYSTEM', response.role_type)

    def test_authorization_verify_project_role_no_permissions(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id, permissions=['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN'
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_no_project_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT'
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_no_project_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_no_project_id_require_project_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'require_project_id': True
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_no_project_group_id_require_project_group_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'require_project_group_id': True
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_no_domain_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_no_domain_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_other_domain_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'domain_id': utils.generate_id('domain'),
            'project_id': self.project.project_id
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_other_project_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'domain_id': self.domain.domain_id,
            'project_id': utils.generate_id('project')
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_same_project_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_same_project_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_same_project_group_id(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_group_id=self.project_group.project_group_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_group_id': self.project_group.project_group_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_same_project_group_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_child_project_group_id(self):
        self._test_create_user()
        self._test_create_project_group()
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project_role_binding(project_group_id=self.project_groups[0].project_group_id,
                                               permissions=['identity.User.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_group_id': self.project_group.project_group_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_no_domain_id_and_project_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_child_project_id(self):
        self._test_create_user()
        self._test_create_project_group()
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project_role_binding(project_group_id=self.project_groups[0].project_group_id,
                                               permissions=['identity.User.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_with_no_domain_id_and_project_id')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_with_child_override_no_permissions_project_group(self):
        self._test_create_user()
        self._test_create_project_group()
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project_role_binding(project_group_id=self.project_groups[0].project_group_id,
                                               permissions=['identity.User.*'])
        self._test_create_project_role_binding(project_group_id=self.project_group.project_group_id,
                                               permissions=['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_with_child_override_no_permissions_project(self):
        self._test_create_user()
        self._test_create_project_group()
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project_group(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project(self.project_group.project_group_id)
        self._test_create_project_role_binding(project_group_id=self.project_groups[0].project_group_id,
                                               permissions=['identity.User.*'])
        self._test_create_project_role_binding(project_id=self.project.project_id,
                                               permissions=['identity.Domain.*'])
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'PROJECT',
            'project_id': self.project.project_id
        }

        with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
            self.identity_v1.Authorization.verify(
                params,
                metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_access_system_api(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'SYSTEM',
            'domain_id': utils.generate_id('domain')
        }

        # with self.assertRaisesRegex(Exception, 'ERROR_PERMISSION_DENIED'):
        #     self.identity_v1.Authorization.verify(
        #         params,
        #         metadata=(('token', self.user_token),))

    def test_authorization_verify_project_role_access_domain_api(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'list',
            'scope': 'DOMAIN',
            'domain_id': self.domain.domain_id
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_access_domain_api')
        self.assertEqual('PROJECT', response.role_type)

    def test_authorization_verify_project_role_list_users(self):
        self._test_create_user()
        self._test_create_project()
        self._test_create_project_role_binding(project_id=self.project.project_id)
        self._test_issue_user_token()

        params = {
            'user_id': self.user.user_id,
            'domain_id': self.domain.domain_id
        }

        response = self.identity_v1.User.list(
            params,
            metadata=(('token', self.user_token),))

        self._print_data(response, 'test_authorization_verify_project_role_get_user')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
