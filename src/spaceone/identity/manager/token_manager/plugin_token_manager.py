import logging

from spaceone.identity.connector import PluginServiceConnector, AuthPluginConnector
from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATUS_CHECK_FAILURE
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.manager import DomainManager
from spaceone.identity.model import Domain, User

_LOGGER = logging.getLogger(__name__)


class PluginTokenManager(JWTManager):
    domain: Domain = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        self.user_mgr: UserManager = self.locator.get_manager('UserManager')

    def authenticate(self, credentials, domain_id):
        _LOGGER.debug(f'[authenticate] domain_id: {domain_id}')
        self.domain = self.domain_mgr.get_domain(domain_id)

        endpoint = self._get_plugin_endpoint(self.domain)

        oauth_user_info = self._authenticate_with_plugin(endpoint, credentials)
        _LOGGER.info(f'[authenticate] OAuth authenticate success. (user_id={oauth_user_info.user_id})')

        self.user: User = self._find_matched_user(oauth_user_info)

        if self.user is None:
            _LOGGER.info(f'[authenticate] OAuth user not found in local. '
                         f'Make this request is not authenticated and raise error.')
            self.is_authenticated = False
            raise ERROR_AUTHENTICATED_WITHOUT_USER()

        self._check_user_state()

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        if self.user.state == 'UNIDENTIFIED':
            self.user = self.user.update({'state': 'ENABLED'})

        # Issue token
        access_token = self.issue_access_token('USER', self.user.user_id, self.user.domain_id, **kwargs)
        refresh_token = self.issue_refresh_token('USER', self.user.user_id, self.user.domain_id, **kwargs)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def refresh_token(self, user_id, domain_id, **kwargs):
        self.user: User = self.user_mgr.get_user(user_id, domain_id)
        self._check_user_state()

        return self.issue_token(**kwargs)

    def _find_matched_user(self, oauth_user_info):
        # Get user from db
        return self._get_user_info_from_db(user_id=oauth_user_info.user_id, domain_id=self.domain.domain_id)

    def _get_user_info_from_db(self, user_id, domain_id):
        try:
            user = self.user_mgr.get_user(user_id=user_id, domain_id=domain_id)
        except ERROR_NOT_FOUND as e:
            _LOGGER.info(f'[_get_user_info_from_db] OAuth user is not exists. (user_id: {user_id})')
            user = None
        return user

    def _authenticate_with_plugin(self, endpoint, credentials):
        auth_plugin_conn: AuthPluginConnector = self.locator.get_connector('AuthPluginConnector')
        user_info = auth_plugin_conn.call_login(endpoint, credentials)
        if user_info:
            self.is_authenticated = True
        return user_info

    def _get_plugin_endpoint(self, domain):
        plugin_id = domain.plugin_info.plugin_id
        version = domain.plugin_info.version
        plugin_svc_conn: PluginServiceConnector = self.locator.get_connector('PluginServiceConnector')
        return plugin_svc_conn.get_plugin_endpoint(plugin_id, version, domain.domain_id)

    def _check_user_state(self):
        if self.user.state not in ['ENABLED', 'UNIDENTIFIED']:
            raise ERROR_USER_STATUS_CHECK_FAILURE(user_id=self.user.user_id)