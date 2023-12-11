import logging
from datetime import datetime

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_user import ERROR_USER_STATUS_CHECK_FAILURE
from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.token_manager.base import JWTManager
from spaceone.identity.model.user.database import User

_LOGGER = logging.getLogger(__name__)


class LocalTokenManager(JWTManager):
    auth_type = "LOCAL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()

    def authenticate(self, user_id, domain_id, credentials):
        pw_to_check = self._parse_password(credentials)

        self.user = self.user_mgr.get_user(user_id, domain_id)

        self._check_user_state()

        # TODO: decrypt pw
        is_correct = PasswordCipher().checkpw(pw_to_check, self.user.password)
        _LOGGER.debug(
            f"[authenticate] is_correct: {is_correct}, pw_to_check: {pw_to_check}, hashed_pw: {self.user.password}"
        )

        if is_correct:
            self.is_authenticated = True
        else:
            raise ERROR_AUTHENTICATION_FAILURE(user_id=self.user.user_id)

    def issue_temporary_token(self, user_id, domain_id, **kwargs):
        api_permissions = [
            "identity.User.get:user:read",
            "identity.User.update:user:write",
        ]
        private_jwk = self._get_private_jwk(kwargs)
        expired = kwargs["timeout"]

        key_gen = KeyGenerator(
            prv_jwk=private_jwk, domain_id=domain_id, audience=user_id
        )

        # Issue token
        access_token = key_gen.generate_access_token(
            expired=expired, api_permissions=api_permissions
        )

        return {"access_token": access_token}

    def issue_token(self, **kwargs):
        if self.is_authenticated is False:
            raise ERROR_NOT_AUTHENTICATED()

        api_permissions = self._get_permissions_from_required_actions()
        private_jwk = self._get_private_jwk(kwargs)
        refresh_private_jwk = self._get_refresh_private_jwk(kwargs)
        domain_id = kwargs.get("domain_id")

        key_gen = KeyGenerator(
            prv_jwk=private_jwk,
            domain_id=domain_id,
            audience=self.user.user_id,
            refresh_prv_jwk=refresh_private_jwk,
        )

        ttl = kwargs.get("ttl") or self.CONST_REFRESH_TTL
        timeout = kwargs.get("timeout") or self.CONST_TOKEN_TIMEOUT

        access_token = key_gen.generate_access_token(
            expired=timeout, api_permissions=api_permissions
        )

        refresh_token = key_gen.generate_refresh_token(expired=timeout, ttl=ttl)
        user = self.user.update({"last_accessed_at": datetime.utcnow()})

        return {"access_token": access_token, "refresh_token": refresh_token}

    def refresh_token(self, user_id, domain_id, **kwargs):
        self.user: User = self.user_mgr.get_user(user_id, domain_id)
        self._check_user_state()

        return self.issue_token(domain_id=domain_id, **kwargs)

    def _get_permissions_from_required_actions(self):
        if "UPDATE_PASSWORD" in self.user.required_actions:
            return ["identity.User.get:user:read", "identity.User.update:user:write"]

        return None

    @staticmethod
    def _parse_password(credentials):
        pw_to_check = credentials.get("password", None)

        if pw_to_check is None:
            raise ERROR_INVALID_CREDENTIALS()

        return pw_to_check

    def _check_user_state(self):
        if self.user.state != "ENABLED":
            raise ERROR_USER_STATUS_CHECK_FAILURE(user_id=self.user.user_id)

        if self.user.auth_type != "LOCAL":
            raise ERROR_NOT_FOUND(key="user_id", value=self.user.user_id)
