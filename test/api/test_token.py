import os
import unittest

from spaceone.core import utils, pygrpc
from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.core.unittest.runner import RichTestRunner


class TestToken(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))
    identity_v1 = None
    domain = None
    token = None
    owner_token = None
    api_key_obj = None
    owner_id = None
    owner_pw = None
    user = None

    @classmethod
    def setUpClass(cls):
        super(TestToken, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                        version='v1')
        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_token()

    @classmethod
    def tearDownClass(cls):
        super(TestToken, cls).tearDownClass()
        cls.identity_v1.DomainOwner.delete({
            'domain_id': cls.domain.domain_id,
            'owner_id': cls.owner_id
        })
        cls.identity_v1.Domain.delete({'domain_id': cls.domain.domain_id})

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        param = {
            'name': name
        }
        cls.domain = cls.identity_v1.Domain.create(param)

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()[0:10]
        cls.owner_pw = 'qwerty'

        param = {
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'name': 'Steven' + utils.random_string()[0:5],
            'timezone': 'Asia/Seoul',
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'domain_id': cls.domain.domain_id
        }

        owner = cls.identity_v1.DomainOwner.create(
            param
        )
        cls.domain_owner = owner

    @classmethod
    def _issue_token(cls):
        token_param = {
            'credentials': {
                'user_type': 'DOMAIN_OWNER',
                'user_id': cls.owner_id,
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_param)
        cls.owner_token = issue_token.access_token

    @classmethod
    def _create_api_key(cls):
        param = {
            'api_key_type': 'USER',
            'domain_id': cls.domain.domain_id
        }
        api_key_vo = cls.identity_v1.APIKey.create(param)
        cls.api_key_obj = api_key_vo
        cls.token = api_key_vo.api_key

    def setUp(self):
        self.token = None
        self.user = None
        self.policy = None
        self.role = None
        self.pw = None
        self._create_user()
        self._update_domain_role()

    def tearDown(self):
        if self.user:
            self.identity_v1.User.delete(
                {
                    'user_id': self.user.user_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

        if self.role:
            self.identity_v1.Role.delete(
                {
                    'role_id': self.role.role_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

        if self.policy:
            self.identity_v1.Policy.delete(
                {
                    'policy_id': self.policy.policy_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

    def _create_policy(self, permissions):
        params = {
            'name': 'Policy-' + utils.random_string()[0:5],
            'permissions': permissions,
            'domain_id': self.domain.domain_id
        }

        self.policy = self.identity_v1.Policy.create(
            params,
            metadata=(('token', self.owner_token),)
        )

    def _create_role(self, policies, role_type='DOMAIN'):
        params = {
            'name': 'Role-' + utils.random_string()[0:5],
            'role_type': role_type,
            'policies': policies,
            'domain_id': self.domain.domain_id
        }

        self.role = self.identity_v1.Role.create(
            params,
            metadata=(('token', self.owner_token),))

    def _create_user(self):
        user_id = utils.random_string()[0:10]
        self.pw = 'qwerty123'
        user_param = {
            'user_id': user_id,
            'password': self.pw,
            'name': 'Steven' + utils.random_string()[0:5],
            'language': 'en',
            'timezone': 'Asia/Seoul',
            'domain_id': self.domain.domain_id,
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'group': 'group-id'
        }
        self.user = self.identity_v1.User.create(
            user_param,
            metadata=(('token', self.owner_token),)
        )

    def _update_domain_role(self):
        self._create_policy(['*'])
        self._create_role([{
            'policy_type': 'CUSTOM',
            'policy_id': self.policy.policy_id}], 'DOMAIN')

        params = {
            'user_id': self.user.user_id,
            'domain_id': self.domain.domain_id,
            'roles': [self.role.role_id]
        }
        self.user = self.identity_v1.User.update_role(
            params,
            metadata=(('token', self.owner_token),)
        )

    def test_issue_token(self):
        token_param = {
            'credentials': {
                'user_id': self.user.user_id,
                'password': self.pw
            },
            'domain_id': self.domain.domain_id
        }

        issue_token = self.identity_v1.Token.issue(token_param)

        self.token = issue_token
        print(f'issued_token: {issue_token}')

        self.assertIsNotNone(issue_token.access_token)
        self.assertIsNotNone(issue_token.refresh_token)
        decoded = JWTUtil.unverified_decode(issue_token.access_token)

        self.assertEqual(self.user.user_id, decoded['aud'])

    def test_issue_token_disabled_user(self):
        self.user = self.identity_v1.User.disable(
            {
                'user_id': self.user.user_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        with self.assertRaises(Exception) as e:
            self.test_issue_token()

        self.assertIn("ERROR_USER_STATUS_CHECK_FAILURE", str(e.exception))

    def test_refresh_token_disabled_user(self):
        self.test_issue_token()

        self.user = self.identity_v1.User.disable(
            {
                'user_id': self.user.user_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.owner_token),)
        )

        with self.assertRaises(Exception) as e:
            self.identity_v1.Token.refresh(
                {},
                metadata=(('token', self.token.refresh_token),)
            )

        self.assertIn("ERROR_USER_STATUS_CHECK_FAILURE", str(e.exception))

    def test_issue_token_not_existing_user(self):
        token_param = {
            'user_id': 'mzc',
            'password': 'pwd',
            'domain_id': self.domain.domain_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.Token.issue(token_param)

    def test_issue_token_with_wrong_password(self):
        token_param = {
            'user_id': self.user.user_id,
            'password': 'pwd',
            'domain_id': self.domain.domain_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.Token.issue(token_param)

    def test_refresh_token(self):
        self.test_issue_token()
        decoded = JWTUtil.unverified_decode(self.token.access_token)
        user_id = decoded['aud']

        self.token = self.identity_v1.Token.refresh(
            {},
            metadata=(('token', self.token.refresh_token),)
        )

        decoded = JWTUtil.unverified_decode(self.token.access_token)

        self.assertIsNotNone(self.token.access_token)
        self.assertEqual(user_id, decoded['aud'])

    def test_refresh_using_same_token(self):
        self.test_issue_token()
        self.identity_v1.Token.refresh(
            {},
            metadata=(('token', self.token.refresh_token),)
        )

        with self.assertRaises(Exception) as e:
            self.identity_v1.Token.refresh(
                {},
                metadata=(('token', self.token.refresh_token),)
            )

        self.assertIn("ERROR_INVALID_REFRESH_TOKEN", str(e.exception))

    def test_exceeded_maximum_refresh_count(self):
        self.test_issue_token()
        decoded = JWTUtil.unverified_decode(self.token.refresh_token)
        refresh_limit = decoded['ttl']

        for i in range(refresh_limit):
            self.token = self.identity_v1.Token.refresh(
                {},
                metadata=(('token', self.token.refresh_token),)
            )

        with self.assertRaises(Exception) as e:
            self.identity_v1.Token.refresh(
                {},
                metadata=(('token', self.token.refresh_token),)
            )

        self.assertIn("ERROR_REFRESH_COUNT", str(e.exception))


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
