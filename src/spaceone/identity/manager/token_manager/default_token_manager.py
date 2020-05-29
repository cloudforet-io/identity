import logging

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATUS_CHECK_FAILURE
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.model import User

_LOGGER = logging.getLogger(__name__)


class DefaultTokenManager(JWTManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr: UserManager = self.locator.get_manager('UserManager')

    def authenticate(self, credentials, domain_id):
        user_id, pw_to_check = self._parse_user_id_and_password(credentials)

        self.user = self.user_mgr.get_user(user_id, domain_id)

        self._check_user_state()

        # TODO: decrypt pw
        is_correct = PasswordCipher().checkpw(pw_to_check, self.user.password)
        _LOGGER.debug(f'[authenticate] is_correct: {is_correct}, pw_to_check: {pw_to_check}, hashed_pw: {self.user.password}')

        if is_correct:
            self.is_authenticated = True
        else:
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.user_id)

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

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

    def _parse_user_id_and_password(self, credentials):
        # Get User
        user_id = credentials.get('user_id', None)
        pw_to_check = credentials.get('password', None)

        if user_id is None or pw_to_check is None:
            raise ERROR_INVALID_CREDENTIALS()

        return user_id, pw_to_check

    def _check_user_state(self):
        if self.user.state != 'ENABLED':
            raise ERROR_USER_STATUS_CHECK_FAILURE(user_id=self.user.user_id)
