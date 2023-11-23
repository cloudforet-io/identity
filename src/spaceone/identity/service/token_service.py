import logging

from spaceone.core import cache
from spaceone.core.auth.jwt import JWTAuthenticator, JWTUtil
from spaceone.core.service import BaseService, transaction, convert_model

from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_domain import ERROR_DOMAIN_STATE
from spaceone.identity.error.error_mfa import *
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.mfa_manager import MFAManager
from spaceone.identity.manager.token_manager import JWTManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.token.request import *
from spaceone.identity.model.token.response import *

_LOGGER = logging.getLogger(__name__)


class TokenService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.user_mgr = UserManager()

    @transaction
    @convert_model
    def issue(self, params: TokenIssueRequest) -> Union[TokenResponse, dict]:
        """Issue token
        Args:
            params (dict): {
                'credentials': 'dict', # required
                'auth_type': 'str', # required
                'timeout': 'int',
                'refresh_count': 'int',
                'verify_code': 'str',
                'domain_id': 'str', # required
            }
        Returns:
            TokenResponse:
        """

        user_id = params.credentials.get("user_id")
        domain_id = params.domain_id
        timeout = params.timeout
        refresh_count = params.refresh_count
        verify_code = params.verify_code

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)
        refresh_private_jwk = self.domain_secret_mgr.get_domain_refresh_private_key(
            domain_id=domain_id
        )

        # Check Domain state is ENABLED
        self._check_domain_state(domain_id)

        token_mgr = JWTManager.get_token_manager_by_auth_type(params.auth_type)
        token_mgr.authenticate(user_id, domain_id, params.credentials)

        user_vo = token_mgr.user
        user_mfa = user_vo.mfa.to_dict() if user_vo.mfa else {}

        if user_mfa.get("state", "DISABLED") == "ENABLED":
            mfa_manager = MFAManager.get_manager_by_mfa_type(user_mfa.get("mfa_type"))
            if verify_code:
                mfa_manager.check_mfa_verify_code(user_id, domain_id, verify_code)
            else:
                mfa_email = user_mfa["options"].get("email")
                mfa_manager.send_mfa_authentication_email(
                    user_id, domain_id, mfa_email, user_vo.language
                )
                raise ERROR_MFA_REQUIRED(user_id=user_id)

        token_info = token_mgr.issue_token(
            private_jwk=private_jwk,
            refresh_private_jwk=refresh_private_jwk,
            timeout=timeout,
            ttl=refresh_count,
        )

        return token_info

    @transaction
    @convert_model
    def refresh(self, params: dict) -> Union[TokenResponse, dict]:
        """Refresh token
        Args:
            params (dict): {}
        Returns:
            TokenResponse:
        """
        refresh_token = self.transaction.get_meta("token")

        if refresh_token is None:
            raise ERROR_INVALID_REFRESH_TOKEN()

        domain_id = self._extract_domain_id(refresh_token)

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)
        refresh_public_jwk = self.domain_secret_mgr.get_domain_refresh_public_key(
            domain_id=domain_id
        )
        refresh_private_jwk = self.domain_secret_mgr.get_domain_refresh_private_key(
            domain_id=domain_id
        )

        token_info = self._verify_refresh_token(refresh_token, refresh_public_jwk)
        user_auth_type = self._get_user_auth_type(token_info["user_id"], domain_id)

        token_mgr = JWTManager.get_token_manager_by_auth_type(user_auth_type)
        token_mgr.check_refreshable(token_info["key"], token_info["ttl"])

        token_response = token_mgr.refresh_token(
            token_info["user_id"],
            domain_id,
            ttl=token_info["ttl"] - 1,
            private_jwk=private_jwk,
            refresh_private_jwk=refresh_private_jwk,
        )

        return TokenResponse(**token_response)

    @cache.cacheable(key="user-auth-type:{domain_id}:{user_id}", expire=600)
    def _get_user_auth_type(self, user_id, domain_id):
        try:
            user_vo = self.user_mgr.get_user(user_id, domain_id)
        except Exception as e:
            _LOGGER.error(
                f'[_get_user_backend] Authentication failure: {getattr(e, "message", e)}'
            )
            raise ERROR_AUTHENTICATION_FAILURE(user_id=user_id)

        return user_vo.auth_type

    @cache.cacheable(key="domain-state:{domain_id}", expire=3600)
    def _check_domain_state(self, domain_id):
        domain_vo = self.domain_mgr.get_domain(domain_id)

        if domain_vo.state != "ENABLED":
            raise ERROR_DOMAIN_STATE(domain_id=domain_vo.domain_id)

    @staticmethod
    def _extract_domain_id(token):
        try:
            decoded = JWTUtil.unverified_decode(token)
        except Exception as e:
            _LOGGER.error(f"[_extract_domain_id] {e}")
            _LOGGER.error(token)
            raise ERROR_AUTHENTICATE_FAILURE(message="Cannot decode token.")

        domain_id = decoded.get("did")

        if domain_id is None:
            raise ERROR_AUTHENTICATE_FAILURE(message="Empty domain_id provided.")

        return domain_id

    @staticmethod
    def _verify_refresh_token(token, public_jwk):
        try:
            decoded = JWTAuthenticator(public_jwk).validate(token)
        except Exception as e:
            _LOGGER.error(f"[_verify_refresh_token] {e}")
            raise ERROR_AUTHENTICATE_FAILURE(message="Token validation failed.")

        if decoded.get("cat") != "REFRESH_TOKEN":
            raise ERROR_INVALID_REFRESH_TOKEN()

        return {
            "user_id": decoded["aud"],
            "user_type": decoded["user_type"],
            "key": decoded["key"],
            "ttl": decoded["ttl"],
            "iat": decoded["iat"],
            "exp": decoded["exp"],
        }
