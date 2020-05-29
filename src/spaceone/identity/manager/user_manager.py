import logging

from spaceone.core.manager import BaseManager

from spaceone.identity.connector import PluginServiceConnector, AuthPluginConnector
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.model import Domain
from spaceone.identity.model.user_model import User

_LOGGER = logging.getLogger(__name__)


class UserManager(BaseManager):

    def __init__(self, transaction):
        super().__init__(transaction)
        self.user_model: User = self.locator.get_model('User')

    def create_user(self, params, domain_vo):
        def _rollback(user_vo):
            _LOGGER.info(f'[create_user._rollback] Delete user : {user_vo.name} ({user_vo.user_id})')
            user_vo.delete()

        params['state'] = params.get('state', 'ENABLED')

        # Password might None when a domain using OAuth plugin.
        if params.get('password'):
            hashed_pw = PasswordCipher().hashpw(params['password'])
            params['password'] = hashed_pw
        else:
            # TODO: should I create random generated password?
            ...

        # If authentication plugin backed Domain, call find action.
        if domain_vo.plugin_info:
            found_users, count = self.find_user({'user_id': params['user_id']}, domain_vo)
            if count == 1:
                params['state'] = found_users[0]['state']
            elif count > 1:
                _LOGGER.warning(f'[create_user] Too many users found. count: {count}')
            else:
                _LOGGER.warning('[create_user] No such user.')

        user_vo = self.user_model.create(params)

        self.transaction.add_rollback(_rollback, user_vo)

        return user_vo

    def update_user(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_user._rollback] Revert Data : {old_data["name"], ({old_data["user_id"]})}')
            user_vo.update(old_data)

        if len(params.get('password', '')) > 0:
            hashed_pw = PasswordCipher().hashpw(params['password'])
            params['password'] = hashed_pw

        user_vo: User = self.get_user(params['user_id'], params['domain_id'])
        self.transaction.add_rollback(_rollback, user_vo.to_dict())

        user_vo.update(params)
        return user_vo

    def delete_user(self, user_id, domain_id):
        user_vo = self.get_user(user_id, domain_id)
        user_vo.delete()

    def enable_user(self, user_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_user._rollback] Revert Data : {old_data}')
            user_vo.update(old_data)

        user_vo: User = self.get_user(user_id, domain_id)

        if user_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, user_vo.to_dict())
            user_vo.update({'state': 'ENABLED'})

        return user_vo

    def disable_user(self, user_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_user._rollback] Revert Data : {old_data}')
            user_vo.update(old_data)

        user_vo: User = self.get_user(user_id, domain_id)

        if user_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, user_vo.to_dict())
            user_vo.update({'state': 'DISABLED'})

        return user_vo

    def update_role(self, params, role_vos):
        def _rollback(old_data):
            _LOGGER.info(f'[update_role._rollback] Revert Data : {old_data["user_id"]}')
            user_vo.update(old_data)

        user_vo: User = self.get_user(params['user_id'], params['domain_id'])
        self.transaction.add_rollback(_rollback, user_vo.to_dict())

        return user_vo.update({'roles': role_vos})

    def get_user(self, user_id, domain_id, only=None):
        return self.user_model.get(user_id=user_id, domain_id=domain_id, only=only)

    def list_users(self, query):
        return self.user_model.query(**query)

    def stat_users(self, query):
        return self.user_model.stat(**query)

    def find_user(self, search, domain_vo: Domain):
        keyword = search.get('keyword', None)
        user_id = search.get('user_id', None)

        endpoint = self._get_plugin_endpoint(domain_vo)

        ret = self._call_find(keyword, user_id, domain_vo, endpoint)

        return ret.get('results'), ret.get('total_count')

    def _call_find(self, keyword, user_id, domain, endpoint):
        auth_plugin_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        auth_plugin_conn.initialize(endpoint)
        return auth_plugin_conn.call_find(keyword, user_id, domain)

    def _get_plugin_endpoint(self, domain):
        """
        Return: endpoint
        """
        plugin_id = domain.plugin_info.plugin_id
        version = domain.plugin_info.version
        plugin_svc_conn: PluginServiceConnector = self.locator.get_connector('PluginServiceConnector')
        return plugin_svc_conn.get_plugin_endpoint(plugin_id, version, domain.domain_id)
