import os
import random
import unittest
from langcodes import Language

from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


class TestDomainOwner(unittest.TestCase):
    config = utils.load_yaml_from_file(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    @classmethod
    def setUpClass(cls):
        super(TestDomainOwner, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestDomainOwner, cls).tearDownClass()

    def setUp(self):
        endpoints = self.config.get('ENDPOINTS', {})
        self.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'),
                                         version='v1')

        self.domain = None
        self.domain_owner = None
        self._create_domain()

    def tearDown(self):
        if self.domain_owner:
            print(f'[TearDown] Delete domain owner. (domain_id: {self.domain.domain_id})')
            params = {
                'domain_id': self.domain.domain_id,
                'owner_id': self.domain_owner.owner_id
            }
            self.identity_v1.DomainOwner.delete(
                params,
                metadata=(('token', self.owner_token),)
            )

        if self.domain:
            print(f'[TearDown] Delete domain. (domain_id: {self.domain.domain_id})')
            self.identity_v1.Domain.delete(
                {
                    'domain_id': self.domain.domain_id
                },
                metadata=(('token', self.owner_token),)
            )

    def _create_domain(self):
        name = utils.random_string()
        params = {
            'name': name
        }
        self.domain = self.identity_v1.Domain.create(params)

    def _issue_owner_token(self, owner_id, owner_pw):
        token_params = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': owner_id,
            'credentials': {
                'password': owner_pw
            },
            'domain_id': self.domain.domain_id
        }

        issue_token = self.identity_v1.Token.issue(token_params)
        self.owner_token = issue_token.access_token

    def test_create_owner(self):
        lang_code = random.choice(['zh-hans', 'jp', 'ko', 'en', 'es'])
        language = Language.get(lang_code)
        owner_id = utils.random_string()

        params = {
            'owner_id': owner_id,
            'password': utils.generate_password(),
            'name': 'Steven' + utils.random_string(),
            'language': language.__str__(),
            'timezone': 'Asia/Seoul',
            'email': 'Steven' + utils.random_string() + '@mz.co.kr',
            'domain_id': self.domain.domain_id
        }

        owner = self.identity_v1.DomainOwner.create(
            params
        )
        self.domain_owner = owner
        self.params = params
        self.assertEqual(params['name'], self.domain_owner.name)

        self._issue_owner_token(params['owner_id'], params['password'])

    def test_failure_create_two_owners(self):
        self.test_create_owner()
        with self.assertRaises(Exception) as e:
            self.test_create_owner()

        self.assertIn("ERROR_NOT_UNIQUE", str(e.exception))

    def test_update_owner(self):
        self.test_create_owner()
        self.params['owner_id'] = self.domain_owner.owner_id
        self.params['name'] = 'John Doe'
        owner = self.identity_v1.DomainOwner.update(
            self.params,
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(owner.name, self.params['name'])

    def test_get_domain_owner(self):
        self.test_create_owner()
        params = {
            'owner_id': self.domain_owner.owner_id,
            'domain_id': self.domain.domain_id
        }
        owner = self.identity_v1.DomainOwner.get(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(owner.name, self.domain_owner.name)

    def test_get_domain_owner_with_domain_id(self):
        self.test_create_owner()
        params = {
            'domain_id': self.domain.domain_id
        }
        owner = self.identity_v1.DomainOwner.get(
            params,
            metadata=(('token', self.owner_token),)
        )
        self.assertEqual(owner.name, self.domain_owner.name)

    def test_failure_get_not_exist_owner(self):
        self.test_create_owner()
        params = {
            'domain_id': 'no-domain',
            'owner_id': 'no-owner'
        }

        with self.assertRaises(Exception) as e:
            self.identity_v1.DomainOwner.get(
                params,
                metadata=(('token', self.owner_token),)
            )
        self.assertIn('ERROR_NOT_FOUND', str(e.exception))


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
