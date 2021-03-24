import logging
from datetime import datetime

from spaceone.identity.connector import PluginServiceConnector, AuthPluginConnector
from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATUS_CHECK_FAILURE
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.manager import DomainManager
from spaceone.identity.model import Domain, User

_LOGGER = logging.getLogger(__name__)


class ExternalTokenManager(JWTManager):
    domain: Domain = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        self.user_mgr: UserManager = self.locator.get_manager('UserManager')

    def authenticate(self, user_id, domain_id, credentials):
        _LOGGER.debug(f'[authenticate] domain_id: {domain_id}')

        # Add User ID for External Authentication
        credentials[user_id] = user_id

        self.domain: Domain = self.domain_mgr.get_domain(domain_id)
        self.user: User = self.user_mgr.get_user(user_id, domain_id)

        self._check_domain_state()

        endpoint = self._get_plugin_endpoint()
        auth_user_info = self._authenticate_with_plugin(endpoint, credentials)
        _LOGGER.info(f'[authenticate] Authentication success. (user_id={auth_user_info.get("user_id")})')

        self._match_user_id(user_id, auth_user_info)

        self._check_user_state()
        self.is_authenticated = True

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        if self.user.state == 'PENDING':
            self.user: User = self.user.update({'state': 'ENABLED'})

        # Issue token
        access_token = self.issue_access_token('USER', self.user.user_id, self.user.domain_id, **kwargs)
        refresh_token = self.issue_refresh_token('USER', self.user.user_id, self.user.domain_id, **kwargs)

        # Update user's last_accessed_at field
        self.user.update({'last_accessed_at': datetime.utcnow()})

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def refresh_token(self, user_id, domain_id, **kwargs):
        self.user: User = self.user_mgr.get_user(user_id, domain_id)
        self._check_user_state()

        return self.issue_token(**kwargs)

    @staticmethod
    def _match_user_id(user_id, auth_user_info):
        if user_id != auth_user_info['user_id']:
            raise ERROR_AUTHENTICATION_FAILURE()

    def _authenticate_with_plugin(self, endpoint, credentials):
        options = self.domain.plugin_info.options

        auth_plugin_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        return auth_plugin_conn.call_login(endpoint, credentials, options, {})

    def _get_plugin_endpoint(self):
        plugin_id = self.domain.plugin_info.plugin_id
        version = self.domain.plugin_info.version
        plugin_svc_conn: PluginServiceConnector = self.locator.get_connector('PluginServiceConnector')
        return plugin_svc_conn.get_plugin_endpoint(plugin_id, version, self.domain.domain_id)

    def _check_domain_state(self):
        if not self.domain.plugin_info:
            _LOGGER.error('[_get_token_manager] This domain does not allow external authentication.')
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.user_id)

    def _check_user_state(self):
        if self.user.state not in ['ENABLED', 'PENDING']:
            raise ERROR_USER_STATUS_CHECK_FAILURE(user_id=self.user.user_id)
