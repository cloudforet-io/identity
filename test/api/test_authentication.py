import json
import os
import unittest

from langcodes import Language

from spaceone.core import utils, pygrpc
from spaceone.core.auth.jwt import JWTUtil


class TestAuthentication(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))
    domain = None
    api_key = None
    api_key_obj = None
    identity_v1 = None
    owner_id = None
    owner_pw = 'qwerty'
    owner_token = None

    @classmethod
    def setUpClass(cls):
        super(TestAuthentication, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                        version='v1')
        cls._create_domain()
        cls._create_domain_owner()
        cls._owner_issue_token()

    @classmethod
    def tearDownClass(cls):
        super(TestAuthentication, cls).tearDownClass()

        cls.identity_v1.DomainOwner.delete({
            'domain_id': cls.domain.domain_id,
            'owner_id': cls.owner_id
        })

        if cls.domain:
            cls.identity_v1.Domain.delete(
                {'domain_id': cls.domain.domain_id},
                metadata=(('token', cls.api_key),)
            )
        if cls.api_key_obj:
            cls.identity_v1.APIKey.delete({'api_key_id': cls.api_key_obj.api_key_id})

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        param = {
            'name': name,
            'tags': {utils.random_string(): utils.random_string(), utils.random_string(): utils.random_string()},
            'config': {
                'aaa': 'bbbb'
            }
        }
        cls.domain = cls.identity_v1.Domain.create(param)

    @classmethod
    def _create_api_key(cls):
        param = {
            'api_key_type': 'USER',
            'domain_id': cls.domain.domain_id
        }
        api_key_vo = cls.identity_v1.APIKey.create(param)
        cls.api_key_obj = api_key_vo
        cls.api_key = api_key_vo.api_key

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()[0:10]

        param = {
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'name': 'Steven' + utils.random_string()[0:5],
            'timezone': 'utc+9',
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'domain_id': cls.domain.domain_id
        }

        owner = cls.identity_v1.DomainOwner.create(
            param
        )
        cls.domain_owner = owner

    @classmethod
    def _owner_issue_token(cls):
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


    def setUp(self):
        self.user = None
        self.user_param = None
        self.token = None

    def tearDown(self):
        if self.user:
            print(f'[tearDown] Delete User. {self.user.user_id}')
            self.identity_v1.User.delete(
                {
                    'user_id': self.user.user_id,
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

    def _create_user(self):
        self.user_param = {
            'user_id': (utils.random_string()[0:10]),
            'password': 'qwerty123',
            'name': 'Steven' + utils.random_string()[0:5],
            'language': Language.get('jp').__str__(),
            'timezone': 'utc+9',
            'tags': {'aa': 'bb'},
            'domain_id': self.domain.domain_id,
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'group': 'group-id',
        }
        self.user = self.identity_v1.User.create(
            self.user_param,
            metadata=(('token', self.owner_token),)
        )

    def _issue_token(self):
        token_param = {
            'credentials': {
                'user_id': self.user.user_id,
                'password': self.user_param['password']
            },
            'domain_id': self.domain.domain_id
        }

        self.token = self.identity_v1.Token.issue(token_param)

        decoded = JWTUtil.unverified_decode(self.token.access_token)
        print(f'decode: {decoded}')

    def _get_domain(self):
        domain = self.identity_v1.Domain.get(
            {'domain_id': self.domain.domain_id},
            metadata=(
                ('token', self.token.access_token),
            )
        )
        print(f'domain: {domain}')

    def test_id_pw_authentication(self):
        self._create_user()
        self._issue_token()

        self._get_domain()

    def test_get_public_key(self):
        param = {
            'domain_id': self.domain.domain_id
        }
        secret = self.identity_v1.Domain.get_public_key(param)
        self.assertEqual(self.domain.domain_id, secret.domain_id)

        key = json.loads(secret.public_key)
        self.assertEqual("RSA", key['kty'])
