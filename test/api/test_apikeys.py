import os
import unittest

from spaceone.core import utils, pygrpc
from spaceone.core.auth.jwt.jwt_util import JWTUtil


class TestAPIKeys(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))
    domain = None
    identity_v1 = None
    owner_id = None
    owner_pw = None
    token = None
    user = None

    @classmethod
    def setUpClass(cls) -> None:
        super(TestAPIKeys, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                        version='v1')
        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_token()
        cls._create_user()

    @classmethod
    def tearDownClass(cls) -> None:
        super(TestAPIKeys, cls).tearDownClass()
        cls.identity_v1.User.delete(
            {
                'user_id': cls.user.user_id,
                'domain_id': cls.domain.domain_id
            },
            metadata=(('token', cls.token),)
        )
        cls.identity_v1.DomainOwner.delete({
            'domain_id': cls.domain.domain_id,
            'owner_id': cls.owner_id
        })
        cls.identity_v1.Domain.delete({'domain_id': cls.domain.domain_id})

    @classmethod
    def _create_domain(self):
        name = utils.random_string()
        param = {
            'name': name,
            'tags': {utils.random_string(): utils.random_string(), utils.random_string(): utils.random_string()},
            'config': {
                'aaa': 'bbbb'
            }
        }
        self.domain = self.identity_v1.Domain.create(param)

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string()[0:10]
        cls.owner_pw = 'qwerty'

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
    def _create_user(cls, user_id=None):
        if user_id is None:
            user_id = utils.random_string()[0:10]

        param = {
            'user_id': user_id,
            'password': 'qwerty123',
            'name': 'Steven' + utils.random_string()[0:5],
            'timezone': 'utc+9',
            'tags': {'aa': 'bb'},
            'email': 'Steven' + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'group': 'group-id',
            'domain_id': cls.domain.domain_id
        }

        cls.user = cls.identity_v1.User.create(
            param,
            metadata=(('token', cls.token),)
        )

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
        cls.token = issue_token.access_token

    def setUp(self) -> None:
        self.api_key = None
        self.api_keys = []
        self.versions = ['2020-03-04']

    def tearDown(self) -> None:
        for api_key in self.api_keys:
            print(f'[tearDown] Delete API Key. {api_key.api_key_id}')
            self.identity_v1.APIKey.delete({
                'api_key_id': api_key.api_key_id,
                'domain_id': self.domain.domain_id
            })

    def test_init(self):
        ...

    def test_create_api_key(self, domain_id=None):
        param = {
            'user_id': self.user.user_id,
            'domain_id': domain_id if domain_id is not None else self.domain.domain_id
        }

        api_key_vo = self.identity_v1.APIKey.create(param)
        self.api_key = api_key_vo
        self.api_keys.append(self.api_key)

        self.assertEqual(api_key_vo.user_id, param['user_id'])

        api_key = api_key_vo.api_key
        print(f'api_key: {api_key}')

        decoded = JWTUtil.unverified_decode(api_key)
        print(f'api_key(decoded): {decoded}')

        self.assertEqual(api_key_vo.user_id, param['user_id'])
        self.assertIn(decoded['ver'], self.versions)
        self.assertIsNotNone(decoded['key'])

    def test_create_api_key_no_domain(self):
        param = {
            'api_key_type': 'USER',
            'user_id': self.user.user_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.create(param)
        # TODO: Unknown domain-id

    # def test_create_api_key_unknown_type(self):
    #     param = {
    #         'api_key_type': 'hello',
    #         'user_id': self.user.user_id,
    #         'domain_id': 'domain-id-'
    #     }
    #     with self.assertRaises(ValueError):
    #         self.identity_v1.APIKey.create(param)

    def test_create_api_key_no_user_id(self):
        param = {
            'api_key_type': 'USER',
            'domain_id': 'domain-id'
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.create(param)

    def test_delete_api_key_no_key_id(self):
        param = {
            'api_key_id': None
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.delete(param)
        param['api_key_id'] = 'no-key'
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.delete(param)

    def test_enable_api_key(self):
        self.test_create_api_key()
        param = {
            'api_key_id': self.api_key.api_key_id,
            'domain_id': self.domain.domain_id
        }
        api_key_vo = self.identity_v1.APIKey.enable(param)

        self.assertEqual(api_key_vo.state, 1)

    def test_enable_api_key_no_exist(self):
        param = {
            'api_key_id': 'hello',
            'domain_id': self.domain.domain_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.enable(param)

        param = {}
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.enable(param)

    def test_disable_api_key(self):
        self.test_create_api_key()
        param = {
            'api_key_id': self.api_key.api_key_id,
            'domain_id': self.domain.domain_id
        }
        api_key_vo = self.identity_v1.APIKey.disable(param)

        self.assertEqual(2, api_key_vo.state)

    def test_disable_api_key_no_exist(self):
        param = {
            'api_key_id': 'hello',
            'domain_id': self.domain.domain_id
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.disable(param)

        param = {}
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.disable(param)

    def test_get_api_key(self):
        self.test_create_api_key()
        param = {
            'api_key_id': self.api_key.api_key_id,
            'domain_id': self.domain.domain_id
        }
        api_key_vo = self.identity_v1.APIKey.get(param)
        self.assertEqual(self.api_key.api_key_id, api_key_vo.api_key_id)

    def test_get_not_existing_api_key(self):
        param = {
            'api_key_id': 'hello'
        }
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.get(param)
        param = {}
        with self.assertRaises(Exception):
            self.identity_v1.APIKey.get(param)

    def test_list_api_keys(self):
        num = 3
        domain_id = 'domain-id-zxy'
        for x in range(num):
            self.test_create_api_key()

        query = {
            # 'count_only': True,
            # 'minimal': True,
            # 'page': {'limit': 2},
            'filter': [
                {
                    'k': 'domain_id',
                    'v': [self.domain.domain_id],
                    'o': 'regex_in'
                }
            ]
        }

        api_keys_vo = self.identity_v1.APIKey.list({
            'query': query,
            'domain_id': self.domain.domain_id
        })
        print(f'total_count: {api_keys_vo.total_count}')

        self.assertEqual(3, api_keys_vo.total_count)

    def test_stat_api_key(self):
        self.test_list_api_keys()

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'api_key_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }]
                    }
                },
                'sort': {
                    'name': 'Count',
                    'desc': True
                }
            }
        }

        result = self.identity_v1.APIKey.stat(
            params, metadata=(('token', self.token),))

        print(result)
