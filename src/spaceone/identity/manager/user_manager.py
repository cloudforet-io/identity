import re
import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.connector import AuthPluginConnector
from spaceone.identity.connector import SecretConnector
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.model import Domain
from spaceone.identity.model.user_model import User
from spaceone.identity.error.error_user import *
from spaceone.identity.manager.domain_manager import DomainManager

_LOGGER = logging.getLogger(__name__)


class UserManager(BaseManager):

    def __init__(self, transaction):
        super().__init__(transaction)
        self.user_model: User = self.locator.get_model('User')

    def create_user(self, params, domain_vo: Domain):
        def _rollback(user_vo):
            _LOGGER.info(f'[create_user._rollback] Delete user : {user_vo.name} ({user_vo.user_id})')
            user_vo.delete()

        params['state'] = params.get('state', 'ENABLED')

        # If user create external authentication, call find action.
        if params['backend'] == 'EXTERNAL':
            found_users, count = self.find_user(
                {
                    'user_id': params['user_id']
                },
                domain_vo
            )

            if count == 1:
                found_user = found_users[0]
                if found_user.get('state') in ['ENABLED', 'DISABLED']:
                    params['state'] = found_user['state']
                else:
                    params['state'] = 'PENDING'

                    if 'name' not in params:
                        params['name'] = found_user.get('name')

                    if 'email' not in params:
                        params['email'] = found_user.get('email')

            elif count > 1:
                raise ERROR_TOO_MANY_USERS_IN_EXTERNAL_AUTH(user_id=params['user_id'])
            else:
                raise ERROR_NOT_FOUND_USER_IN_EXTERNAL_AUTH(user_id=params['user_id'])

        else:
            if params['user_type'] == 'API_USER':
                params['password'] = None
            else:
                self._check_user_id_format(params['user_id'])

                password = params.get('password')
                if password:
                    self._check_password_format(password)
                else:
                    raise ERROR_REQUIRED_PARAMETER(key='password')

                hashed_pw = PasswordCipher().hashpw(password)
                params['password'] = hashed_pw

        user_vo = self.user_model.create(params)

        self.transaction.add_rollback(_rollback, user_vo)

        return user_vo

    def update_user(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_user._rollback] Revert Data : {old_data["name"], ({old_data["user_id"]})}')
            user_vo.update(old_data)

        if params.get('password'):
            self._check_password_format(params['password'])
            hashed_pw = PasswordCipher().hashpw(params['password'])
            params['password'] = hashed_pw

        user_vo: User = self.get_user(params['user_id'], params['domain_id'])
        self.transaction.add_rollback(_rollback, user_vo.to_dict())

        user_vo.update(params)
        return user_vo

    def delete_user(self, user_id, domain_id):
        user_vo = self.get_user(user_id, domain_id)
        user_vo.delete()

        cache.delete_pattern(f'user-state:{domain_id}:{user_id}')
        cache.delete_pattern(f'role-bindings:{domain_id}:{user_id}*')
        cache.delete_pattern(f'user-permissions:{domain_id}:{user_id}*')
        cache.delete_pattern(f'user-scopes:{domain_id}:{user_id}*')

    def enable_user(self, user_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_user._rollback] Revert Data : {old_data}')
            user_vo.update(old_data)

        user_vo: User = self.get_user(user_id, domain_id)

        if user_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, user_vo.to_dict())
            user_vo.update({'state': 'ENABLED'})

            cache.delete_pattern(f'user-state:{domain_id}:{user_id}')

        return user_vo

    def disable_user(self, user_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_user._rollback] Revert Data : {old_data}')
            user_vo.update(old_data)

        user_vo: User = self.get_user(user_id, domain_id)

        if user_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, user_vo.to_dict())
            user_vo.update({'state': 'DISABLED'})

            cache.delete_pattern(f'user-state:{domain_id}:{user_id}')

        return user_vo

    def get_user(self, user_id, domain_id, only=None):
        return self.user_model.get(user_id=user_id, domain_id=domain_id, only=only)

    def filter_users(self, **conditions):
        return self.user_model.filter(**conditions)

    def list_users(self, query):
        return self.user_model.query(**query)

    def stat_users(self, query):
        return self.user_model.stat(**query)

    def find_user(self, search, domain_vo: Domain):
        keyword = search.get('keyword')
        user_id = search.get('user_id')

        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')

        endpoint = domain_mgr.get_auth_plugin_endpoint_by_vo(domain_vo)

        response = self._call_find(keyword, user_id, domain_vo, endpoint)
        results = response.get('results', [])
        total_count = response.get('total_count', 0)

        return results, total_count

    @staticmethod
    def _check_user_id_format(user_id):
        rule = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(rule, user_id):
            raise ERROR_INCORRECT_USER_ID_FORMAT(rule='Email format required.')

    @staticmethod
    def _check_password_format(password):
        if len(password) < 8:
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule='At least 9 characters long.')
        elif not re.search("[a-z]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule='Contains at least one lowercase character')
        elif not re.search("[A-Z]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule='Contains at least one uppercase character')
        elif not re.search("[0-9]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule='Contains at least one number')

    def _call_find(self, keyword, user_id, domain_vo, endpoint):
        options = domain_vo.plugin_info.options

        auth_plugin_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth_plugin_conn.initialize(endpoint)

        secret_data, schema = self._get_auth_plugin_secret(domain_vo.to_dict())
        return auth_plugin_conn.call_find(keyword, user_id, options, secret_data, schema)

    def _get_auth_plugin_secret(self, domain_data):
        """
        Return: (secret_data, schema)
                Default: ({}, None)
        """
        domain_id = domain_data['domain_id']
        plugin_info = domain_data.get('plugin_info', {})
        secret_id = plugin_info.get('secret_id')

        if secret_id is None:
            return {}, None

        # Secret exists
        # WARNING: DO NOT USE SpaceConnector for secret service
        # secret connector may decrypt secret_data
        secret_connector: SecretConnector = self.locator.get_connector('SecretConnector')
        secret = secret_connector.get(secret_id, domain_id)
        secret_data = secret_connector.get_data(secret_id, domain_id)

        return secret_data.get('data', {}), secret_data.get('schema')
