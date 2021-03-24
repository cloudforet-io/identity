import json
import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.auth.jwt import JWTUtil


class TestAuthentication(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    pp = pprint.PrettyPrinter(indent=4)
    domain = None
    api_key_info = None
    api_key = None
    identity_v1 = None
    owner_id = None
    owner_pw = utils.generate_password()
    owner_token = None

    @classmethod
    def setUpClass(cls):
        super(TestAuthentication, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                        version='v1')
        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestAuthentication, cls).tearDownClass()

        cls.identity_v1.DomainOwner.delete(
            {
                'domain_id': cls.domain.domain_id,
                'owner_id': cls.owner_id
            },
            metadata=(('token', cls.owner_token),)
        )

        cls.identity_v1.Domain.delete(
            {
                'domain_id': cls.domain.domain_id
            },
            metadata=(('token', cls.owner_token),)
        )

        if cls.api_key_info:
            cls.identity_v1.APIKey.delete(
                {
                    'api_key_id': cls.api_key_info.api_key_id
                },
                metadata=(('token', cls.owner_token),)
            )

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        params = {
            'name': name
        }
        cls.domain = cls.identity_v1.Domain.create(
            params,
            metadata=(('token', cls.owner_token),)
        )

    @classmethod
    def _create_api_key(cls):
        params = {
            'domain_id': cls.domain.domain_id
        }
        api_key_info = cls.identity_v1.APIKey.create(
            params,
            metadata=(('token', cls.owner_token),)
        )
        cls.api_key_info = api_key_info
        cls.api_key = api_key_info.api_key

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()

        params = {
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'domain_id': cls.domain.domain_id
        }

        owner = cls.identity_v1.DomainOwner.create(
            params
        )
        cls.domain_owner = owner

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

    def setUp(self):
        self.user = None
        self.user_params = None
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

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def _create_user(self, user_type=None, backend=None):
        self.user_params = {
            'user_id': utils.random_string() + '@mz.co.kr',
            'password': utils.generate_password(),
            'name': 'Steven' + utils.random_string(),
            'timezone': 'Asia/Seoul',
            'user_type': user_type or 'USER',
            'backend': backend or 'LOCAL',
            'domain_id': self.domain.domain_id
        }
        self.user = self.identity_v1.User.create(
            self.user_params,
            metadata=(('token', self.owner_token),)
        )

        self._print_data(self.user, '_create_user')

    def _issue_token(self):
        params = {
            'user_id': self.user.user_id,
            'credentials': {
                'password': self.user_params['password']
            },
            'domain_id': self.domain.domain_id
        }

        self.token = self.identity_v1.Token.issue(params)

        decoded = JWTUtil.unverified_decode(self.token.access_token)
        print()
        print('[ _issue_token: decoded token ]')
        self.pp.pprint(decoded)

    def _get_user(self):
        params = {
            'user_id': self.user.user_id
        }

        user = self.identity_v1.User.get(
            params,
            metadata=(
                ('token', self.token.access_token),
            )
        )
        self._print_data(user, '_get_user')

    def test_id_pw_authentication(self):
        self._create_user()
        self._issue_token()

        self._get_user()

    def test_get_public_key(self):
        params = {
            'domain_id': self.domain.domain_id
        }
        secret = self.identity_v1.Domain.get_public_key(params)
        self.assertEqual(self.domain.domain_id, secret.domain_id)

        key = json.loads(secret.public_key)
        self.assertEqual("RSA", key['kty'])
