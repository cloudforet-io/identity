# -*- coding: utf-8 -*-
import logging
import time
from typing import Tuple, Any

from spaceone.core import utils
from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.identity.error import ERROR_GENERATE_KEY_FAILURE

_LOGGER = logging.getLogger(__name__)


class KeyGenerator:

    def __init__(self, prv_jwk, domain_id, aud_id):
        self.prv_jwk = prv_jwk
        self.domain_id = domain_id
        self.aud_id = aud_id

        self._do_parameter_check()

    def _do_parameter_check(self):
        if self.prv_jwk is None:
            raise ERROR_GENERATE_KEY_FAILURE()
        if self.domain_id is None:
            raise ERROR_GENERATE_KEY_FAILURE()

    def generate_api_key(self) -> Tuple[str, Any]:
        key = utils.random_string()

        payload = {
            'cat': 'API_KEY',
            'did': self.domain_id,
            'aud': self.aud_id,
            'iat': int(time.time()),
            'key': key,
            'ver': '2020-03-04'
        }

        encoded = JWTUtil.encode(payload, self.prv_jwk)

        _LOGGER.debug(f'[KeyGenerator] Generated payload. ( '
                      f'cat: {payload.get("cat")}, '
                      f'ver: {payload.get("ver")}, '
                      f'key(masked): {payload.get("key")[0:8]}*****, '
                      f'aud: {payload.get("aud")}, '
                      f'did: {payload.get("did")} )')

        return key, encoded
