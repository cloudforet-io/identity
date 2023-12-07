import logging
import time
from typing import Tuple

from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.identity.error import ERROR_GENERATE_KEY_FAILURE

_LOGGER = logging.getLogger(__name__)


class KeyGenerator:
    def __init__(self, prv_jwk: dict, domain_id: str, audience: str, refresh_prv_jwk: dict = None):
        self.prv_jwk = prv_jwk
        self.domain_id = domain_id
        self.audience = audience
        self.refresh_prv_jwk = refresh_prv_jwk

        self._check_parameter()

    def _check_parameter(self):
        if self.prv_jwk is None:
            raise ERROR_GENERATE_KEY_FAILURE()
        if self.domain_id is None:
            raise ERROR_GENERATE_KEY_FAILURE()

    def generate_api_key(self, api_key_id: str, expired: int) -> str:
        payload = {
            "iss": "spaceone.identity",
            "typ": "API_KEY",       # API_KEY | ACCESS_TOKEN | REFRESH_TOKEN
            "own": "USER",          # USER | APP
            "did": self.domain_id,
            "sub": api_key_id,
            "aud": self.audience,
            "exp": expired,
            "iat": int(time.time()),
            "ver": "2.0",
        }

        self._print_key(payload)
        return JWTUtil.encode(payload, self.prv_jwk)

    def generate_token(self, expired: int, ttl: int = None) -> Tuple[str, str]:
        # ttl -> ttl (REFRESH_TOKEN Only)
        # self._generate_refresh_key() -> jti
        return 'ACCESS_TOKEN', 'REFRESH_TOKEN'

    @staticmethod
    def _print_key(payload: dict):
        _LOGGER.debug(
            f"[KeyGenerator._print_key] generated payload. ( "
            f'iss: {payload.get("iss")}, '
            f'typ: {payload.get("typ")}, '
            f'own: {payload.get("own")}, '
            f'did: {payload.get("did")}, '
            f'sub: {payload.get("sub")}, '
            f'aud: {payload.get("aud")}, '
            f'exp: {payload.get("exp")}, '
            f'iat: {payload.get("iat")}, '
            f'ttl: {payload.get("ttl")}, '
            f'jti: {payload.get("jti")}, '
            f'ver: {payload.get("ver")} )'
        )
