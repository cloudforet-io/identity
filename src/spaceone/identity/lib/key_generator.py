import logging
import time
from typing import Tuple, Any

from spaceone.core import utils
from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.identity.error import ERROR_GENERATE_KEY_FAILURE

_LOGGER = logging.getLogger(__name__)


class KeyGenerator:
    def __init__(self, prv_jwk, domain_id, audience):
        self.prv_jwk = prv_jwk
        self.domain_id = domain_id
        self.audience = audience

        self._do_parameter_check()

    def _do_parameter_check(self):
        if self.prv_jwk is None:
            raise ERROR_GENERATE_KEY_FAILURE()
        if self.domain_id is None:
            raise ERROR_GENERATE_KEY_FAILURE()

    def generate_api_key(
        self, api_key_id: str, user_type: str = "USER"
    ) -> Tuple[str, Any]:
        payload = {
            "cat": "API_KEY",
            "user_type": user_type,
            "did": self.domain_id,
            "aud": self.audience,
            "iat": int(time.time()),
            "api_key_id": api_key_id,
            "ver": "2020-12-07",
        }

        encoded = JWTUtil.encode(payload, self.prv_jwk)

        _LOGGER.debug(
            f"[KeyGenerator] Generated payload. ( "
            f'cat: {payload.get("cat")}, '
            f'user_type: {payload.get("user_type")}, '
            f'did: {payload.get("did")}, '
            f'aud: {payload.get("aud")}, '
            f'api_key_id: {payload.get("api_key_id")}, '
            f'version: {payload.get("version")} )'
        )

        return encoded
