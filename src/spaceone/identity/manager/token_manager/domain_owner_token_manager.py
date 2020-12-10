import logging
from datetime import datetime

from spaceone.identity.error.error_authentication import *
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.manager import DomainOwnerManager
from spaceone.identity.model import DomainOwner

_LOGGER = logging.getLogger(__name__)


class DomainOwnerTokenManager(JWTManager):
    user: DomainOwner = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_owner_mgr: DomainOwnerManager = self.locator.get_manager('DomainOwnerManager')

    def authenticate(self, user_id, domain_id, credentials):
        pw_to_check = self._parse_password(credentials)

        self.user = self.domain_owner_mgr.get_owner(owner_id=user_id, domain_id=domain_id)

        is_correct = PasswordCipher().checkpw(pw_to_check, self.user.password)
        _LOGGER.debug(f'[authenticate] is_correct: {is_correct}, pw_to_check: {pw_to_check}, hashed_pw: {self.user.password}')

        if is_correct:
            self.is_authenticated = True
        else:
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.owner_id)

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        # Issue token
        access_token = self.issue_access_token('DOMAIN_OWNER', self.user.owner_id, self.user.domain_id, **kwargs)
        refresh_token = self.issue_refresh_token('DOMAIN_OWNER', self.user.owner_id, self.user.domain_id, **kwargs)

        # Update user's last_accessed_at field
        self.user.update({'last_accessed_at': datetime.utcnow()})

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def refresh_token(self, user_id, domain_id, **kwargs):
        self.user = self.domain_owner_mgr.get_owner(owner_id=user_id, domain_id=domain_id)
        return self.issue_token(**kwargs)

    @staticmethod
    def _parse_password(credentials):
        pw_to_check = credentials.get('password', None)

        if pw_to_check is None:
            raise ERROR_INVALID_CREDENTIALS()

        return pw_to_check
