import os
import uuid
import random
import unittest
import pprint
from langcodes import Language

from google.protobuf.json_format import MessageToDict
from spaceone.core.error import *
from spaceone.core import config, utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner


def random_string():
    return uuid.uuid4().hex


class TestProject(unittest.TestCase):
    config = config.load_config(
        os.environ.get('SPACEONE_TEST_CONFIG_FILE', './config.yml'))

    pp = pprint.PrettyPrinter(indent=4)
    identity_v1 = None
    domain = None
    domain_owner = None
    owner_id = None
    owner_pw = None
    token = None

    @classmethod
    def setUpClass(cls):
        super(TestProject, cls).setUpClass()
        endpoints = cls.config.get('ENDPOINTS', {})
        cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        super(TestProject, cls).tearDownClass()
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
        cls.owner_id = utils.random_string()[0:10]
        cls.owner_pw = 'qwerty'

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
            'credentials': {
                'user_type': 'DOMAIN_OWNER',
                'user_id': cls.owner_id,
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_params)
        cls.token = issue_token.access_token
        print(f'token: {cls.token}')

    def setUp(self):
        self.project_group = None
        self.project_groups = []
        self.project = None
        self.projects = []
        self.user = None
        self.users = []
        self.policy = None
        self.policies = []
        self.role = None
        self.roles = []

    def tearDown(self):
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

        for project in self.projects:
            print(f'[tearDown] Delete Project. {project.project_id}')
            self.identity_v1.Project.delete(
                {'project_id': project.project_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

        for project_group in self.project_groups:
            print(f'[tearDown] Delete Project Group. {project_group.project_group_id}')
            self.identity_v1.ProjectGroup.delete(
                {'project_group_id': project_group.project_group_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.token),)
            )

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def _test_create_policy(self, permissions=None):
        params = {
            'name': 'Policy-' + random_string()[0:5],
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
            metadata=(('token', self.token),)
        )

        self.policies.append(self.policy)

    def _test_create_role(self, role_type='DOMAIN', policies=None):
        if self.policy is None:
            self._test_create_policy()

        params = {
            'name': 'Role-' + random_string()[0:5],
            'role_type': role_type,
            'policies': policies or [{
                'policy_type': 'CUSTOM',
                'policy_id': self.policy.policy_id
            }],
            'domain_id': self.domain.domain_id
        }

        self.role = self.identity_v1.Role.create(
            params,
            metadata=(('token', self.token),))

        self.roles.append(self.role)

    def _test_create_user(self, name='test', user_id=None):
        if self.role is None:
            self._test_create_role()

        if user_id is None:
            user_id = utils.random_string()[0:10]

        lang_code = random.choice(['zh-hans', 'jp', 'ko', 'en', 'es'])
        language = Language.get(lang_code)

        params = {
            'user_id': user_id,
            'domain_id': self.domain.domain_id,
            'password': 'qwerty123',
            'name': name + utils.random_string()[0:5],
            'language': language.__str__(),
            'timezone': 'utc+9',
            'tags': {'aa': 'bb'},
            'email': name + utils.random_string()[0:5] + '@mz.co.kr',
            'mobile': '+821026671234',
            'group': 'group-id'
        }

        self.user = self.identity_v1.User.create(
            params,
            metadata=(('token', self.token),)
        )

        self.user = self.identity_v1.User.update_role(
            {
                'user_id': self.user.user_id,
                'domain_id': self.domain.domain_id,
                'roles': [self.role.role_id]
            },
            metadata=(('token', self.token),)
        )

        self.users.append(self.user)

        return self.user

    def test_create_project_group(self):
        name = f'pg-{utils.random_string()[0:5]}'
        params = {
            'name': name,
            'tags': {
                 utils.random_string(): utils.random_string(),
                 utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain.domain_id
        }

        self.project_group = self.identity_v1.ProjectGroup.create(
            params,
            metadata=(('token', self.token),)
        )
        self.project_groups.append(self.project_group)
        self.assertEqual(self.project_group.name, name)

    def test_create_project(self, project_group_id=None):
        if project_group_id is None:
            self.test_create_project_group()

        name = f'prj-{utils.random_string()[0:5]}'
        params = {
            'name': name,
            'tags': {
                 utils.random_string(): utils.random_string(),
                 utils.random_string(): utils.random_string()
            },
            'domain_id': self.domain.domain_id
        }

        if project_group_id is None:
            params['project_group_id'] = self.project_group.project_group_id
        else:
            params['project_group_id'] = project_group_id

        self.project = self.identity_v1.Project.create(
            params,
            metadata=(('token', self.token),)
        )
        self.projects.append(self.project)
        self.assertEqual(self.project.name, name)

    def test_update_project_name(self):
        self.test_create_project()

        name = 'blah-blah-blah'
        params = {
            'project_id': self.project.project_id,
            'name': name,
            'domain_id': self.domain.domain_id
        }

        project = self.identity_v1.Project.update(
            params,
            metadata=(('token', self.token),)
        )

        self.assertEqual(project.name, name)

    def test_update_project_tags(self):
        self.test_create_project()

        tags = {
            'test': 'is good'
        }

        params = {
            'project_id': self.project.project_id,
            'tags': tags,
            'domain_id': self.domain.domain_id
        }

        project = self.identity_v1.Project.update(
            params,
            metadata=(('token', self.token),)
        )

        self.assertEqual(MessageToDict(project.tags), tags)

    def test_update_project_project_group(self):
        self.test_create_project()
        self.test_create_project_group()

        params = {
            'project_id': self.project.project_id,
            'project_group_id': self.project_group.project_group_id,
            'domain_id': self.domain.domain_id
        }

        project = self.identity_v1.Project.update(
            params,
            metadata=(('token', self.token),)
        )

        self.assertEqual(project.project_group_info.project_group_id, self.project_group.project_group_id)

    def test_delete_project_group_exist_project(self):
        self.test_create_project()

        params = {
            'project_group_id': self.project_group.project_group_id,
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception) as e:
            self.identity_v1.ProjectGroup.delete(
                params,
                metadata=(('token', self.token),)
            )

        self.assertIn("ERROR_EXIST_RESOURCE", str(e.exception))

    def test_delete_project_not_exist(self):
        self.test_create_project()

        params = {
            'project_id': 'blah-blah-blah',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Project.delete(
                params,
                metadata=(('token', self.token),)
            )

    def test_get_project(self):
        self.test_create_project()

        project = self.identity_v1.Project.get(
            {
                'project_id': self.project.project_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(project.project_id, self.project.project_id)

    def test_get_project_not_exist(self):
        self.test_create_project()

        params = {
            'project_id': 'blah-blah',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Project.get(
                params,
                metadata=(('token', self.token),)
            )

    def test_list_projects_project_group_id(self):
        self.test_create_project_group()

        num = 10
        for x in range(num):
            self.test_create_project(self.project_group.project_group_id)

        projects = self.identity_v1.Project.list(
            {
                'project_group_id': self.project_group.project_group_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(projects.total_count, num)

    def test_list_projects_minimal(self):
        num = 5
        for x in range(num):
            self.test_create_project()

        query = {
            'minimal': True
        }

        projects = self.identity_v1.Project.list(
            {
                'query': query,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(projects.total_count, num)

    def test_list_projects_name(self):
        self.test_create_project_group()

        num = 10
        for x in range(num):
            self.test_create_project(self.project_group.project_group_id)

        projects = self.identity_v1.Project.list(
            {
                'name': 'blah-blah',
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(projects.total_count, 0)

    def test_list_projects_with_query(self):
        self.test_create_project_group()

        num = 10
        for x in range(num):
            self.test_create_project(self.project_group.project_group_id)

        query = {
            'filter': [
                {
                    'k': 'project_group_id',
                    'v': self.project_group.project_group_id,
                    'o': 'eq'
                }
            ],
        }

        projects = self.identity_v1.Project.list(
            {
                'query': query,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(projects.total_count, num)

    def test_add_project_member(self, project=None, user=None):
        if user is None:
            user = self._test_create_user()

        self._test_create_role('PROJECT')

        if project is None:
            self.test_create_project()
            project = self.project

        params = {
            'project_id': project.project_id,
            'user_id': user.user_id,
            'roles': [self.role.role_id],
            'domain_id': self.domain.domain_id
        }

        project_member = self.identity_v1.Project.add_member(
            params,
            metadata=(('token', self.token),)
        )

        self._print_data(project_member, 'test_add_project_member')
        self.assertEqual(project_member.user_info.user_id, user.user_id)

    def test_add_project_member_exist_member(self):
        self.test_add_project_member()

        params = {
            'project_group_id': self.project.project_id,
            'user_id': self.user.user_id,
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Project.add_member(
                params,
                metadata=(('token', self.token),)
            )

    def test_modify_project_member(self):
        self.test_add_project_member()

        labels = ['developer', 'operator']

        params = {
            'project_id': self.project.project_id,
            'user_id': self.user.user_id,
            'roles': [],
            'labels': labels,
            'domain_id': self.domain.domain_id
        }

        project_member = self.identity_v1.Project.modify_member(
            params,
            metadata=(('token', self.token),)
        )

        self._print_data(project_member, 'test_modify_project_member')
        self.assertEqual(sorted(project_member.labels), sorted(labels))

    def test_modify_project_member_not_exist_member(self):
        self.test_add_project_member()

        params = {
            'project_id': self.project.project_id,
            'user_id': 'blah-blah-blah-blah',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Project.modify_member(
                params,
                metadata=(('token', self.token),)
            )

    def test_remove_project_member(self):
        self.test_add_project_member()

        self.identity_v1.Project.remove_member(
            {
                'project_id': self.project.project_id,
                'user_id': self.user.user_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        project_members = self.identity_v1.Project.list_members(
            {
                'project_id': self.project.project_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(0, project_members.total_count)

    def test_remove_project_member_not_exist_member(self):
        self.test_add_project_member()

        params = {
            'project_id': self.project.project_id,
            'user_id': 'blah-blah',
            'domain_id': self.domain.domain_id
        }

        with self.assertRaises(Exception):
            self.identity_v1.Project.remove_member(
                params,
                metadata=(('token', self.token),)
            )

    def test_list_project_members(self):
        self.test_create_project()
        self._test_create_user()
        self._test_create_user()
        self._test_create_user()

        for user in self.users:
            self.test_add_project_member(self.project, user)

        query = {
            'filter': [
                {'k': 'user_name', 'v': 'test', 'o': 'contain'}
            ]
        }

        response = self.identity_v1.Project.list_members(
            {
                'query': query,
                'project_id': self.project.project_id,
                'domain_id': self.domain.domain_id
            },
            metadata=(('token', self.token),)
        )

        self.assertEqual(len(self.users), response.total_count)

    def test_list_project_group_members_with_user_id(self):
        self.test_create_project()
        self._test_create_user()
        self._test_create_user()
        self._test_create_user()

        for user in self.users:
            self.test_add_project_member(self.project, user)

        params = {
            'project_id': self.project.project_id,
            'user_id': self.user.user_id,
            'domain_id': self.domain.domain_id
        }

        response = self.identity_v1.Project.list_members(
            params,
            metadata=(('token', self.token),)
        )

        self.assertEqual(1, response.total_count)

    def test_list_project_group_members_not_exist_user(self):
        self.test_create_project()
        self._test_create_user()
        self._test_create_user()
        self._test_create_user()

        for user in self.users:
            self.test_add_project_member(self.project, user)

        params = {
            'project_id': self.project.project_id,
            'user_id': 'TEST',
            'domain_id': self.domain.domain_id
        }
        response = self.identity_v1.Project.list_members(
            params,
            metadata=(('token', self.token),)
        )

        self.assertEqual(0, response.total_count)

    def test_stat_project(self):
        self.test_create_project()
        self.test_create_project()
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[1])
        self.test_add_project_member(self.projects[1])

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    'group': {
                        'keys': [{
                            'key': 'project_id',
                            'name': 'Id'
                        }],
                        'fields': [{
                            'operator': 'count',
                            'name': 'Count'
                        }, {
                            'key': 'project_member.user.user_id',
                            'name': 'project_member_count',
                            'operator': 'size'
                        }]
                    }
                },
                'sort': {
                    'name': 'Count',
                    'desc': True
                }
            }
        }

        result = self.identity_v1.Project.stat(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_project')

    def test_stat_project_count(self):
        self.test_create_project()
        self.test_create_project()
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[0])
        self.test_add_project_member(self.projects[1])
        self.test_add_project_member(self.projects[1])

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'aggregate': {
                    "count": {
                        "name": "project_count"
                    }
                }
            }
        }

        result = self.identity_v1.Project.stat(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_project_count_1')

        params = {
            'domain_id': self.domain.domain_id,
            'query': {
                'count_only': True
            }
        }

        result = self.identity_v1.Project.list(
            params, metadata=(('token', self.token),))

        self._print_data(result, 'test_stat_project_count_2')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
