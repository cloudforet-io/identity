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
    token = None

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
        cls.identity_v1.DomainOwner.delete({
            'domain_id': cls.domain.domain_id,
            'owner_id': cls.owner_id
        })
        print(f'>> delete domain owner: {cls.owner_id}')

        if cls.domain:
            cls.identity_v1.Domain.delete({'domain_id': cls.domain.domain_id})
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
        token_params = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': cls.owner_id,
            'credentials': {
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_params)
        cls.token = issue_token.access_token
        print(f'token: {cls.token}')

    def setUp(self) -> None:
        self.user = None
        self.users = []
        self.policy = None
        self.policies = []
        self.role = None
        self.roles = []

    def tearDown(self) -> None:
        print()
        for user in self.users:
            print(f'[tearDown] Delete User. {user.user_id}')
            self.identity_v1.User.delete(
                {'user_id': user.user_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

        for role in self.roles:
            print(f'[tearDown] Delete Role. {role.role_id}')
            self.identity_v1.Role.delete(
                {'role_id': role.role_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

        for policy in self.policies:
            print(f'[tearDown] Delete Policy. {policy.policy_id}')
            self.identity_v1.Policy.delete(
                {'policy_id': policy.policy_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

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
            metadata=(('token', self.token),)
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
            metadata=(('token', self.token),))

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

        user = self.identity_v1.User.create(
            params,
            metadata=(('token', self.token),)
        )
        self.user = user
        self.users.append(user)
        self.assertEqual(self.user.name, params['name'])

    def _test_update_domain_role(self):
        self._test_create_policy([
            'identity.Domain.get',
            'identity.Domain.list',
            'identity.Project.*',
            'identity.ProjectGroup.*',
            'identity.User.get',
            'identity.User.update',
        ])
        self._test_create_role([{
            'policy_type': 'CUSTOM',
            'policy_id': self.policy.policy_id}], 'DOMAIN')

        params = {
            'user_id': self.user.user_id,
            'domain_id': self.domain.domain_id,
            'roles': list(map(lambda role: role.role_id, self.roles))
        }
        self.user = self.identity_v1.User.update_role(
            params,
            metadata=(('token', self.token),)
        )

        self._print_data(self.user, 'test_update_domain_role')

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

    def test_check_domain_owner_permissions(self):
        """ Check Domain Owner Permissions
        """

        self._test_create_user()
        user = self.identity_v1.User.get(
            {
                'user_id': self.user.user_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(user.user_id, self.user.user_id)

    def test_authorization_verify_domain_role(self):
        """ Verify Authorization
        """

        self._test_create_user('domain_user@mz.co.kr')
        self._test_update_domain_role()
        self._test_issue_user_token()

        params = {
            'service': 'identity',
            'resource': 'User',
            'verb': 'get',
            'parameter': {
                'domain_id': self.domain.domain_id,
                'test': 1,
                'test2': 2.0
            }
        }

        response = self.identity_v1.Authorization.verify(
            params,
            metadata=(('token', self.user_token),))

        print(response)
        self._print_data(response, 'test_authorization_verify')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
