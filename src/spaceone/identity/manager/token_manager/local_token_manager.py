import logging

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATE_DISABLED
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager.base import TokenManager

_LOGGER = logging.getLogger(__name__)


class LocalTokenManager(TokenManager):
    auth_type = "LOCAL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()

    def authenticate(self, domain_id, **kwargs):
        credentials = kwargs.get("credentials", {})
        self._check_credentials(credentials)
        user_id = credentials["user_id"]
        password = credentials["password"]

        self.user = self.user_mgr.get_user(user_id, domain_id)

        self._check_user_state()

        # TODO: decrypt pw
        is_correct = PasswordCipher().checkpw(password, self.user.password)
        _LOGGER.debug(f"[authenticate] is_correct: {is_correct}")

        if is_correct:
            self.is_authenticated = True

            if self.user.state == "PENDING":
                self.user_mgr.update_user_by_vo({"state": "ENABLED"}, self.user)

        else:
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.user_id)

    def _check_user_state(self):
        if self.user.state == "DISABLED":
            raise ERROR_USER_STATE_DISABLED(user_id=self.user.user_id)

        if self.user.auth_type != "LOCAL":
            raise ERROR_NOT_FOUND(key="user_id", value=self.user.user_id)

    @staticmethod
    def _check_credentials(credentials):
        if credentials.get("user_id") is None:
            raise ERROR_INVALID_CREDENTIALS()

        if credentials.get("password") is None:
            raise ERROR_INVALID_CREDENTIALS()
