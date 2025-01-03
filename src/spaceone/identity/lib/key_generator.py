import logging
import time

from spaceone.core.auth.jwt.jwt_util import JWTUtil
from spaceone.core import utils

from spaceone.identity.error import ERROR_GENERATE_KEY_FAILURE

_LOGGER = logging.getLogger(__name__)


class KeyGenerator:
    def __init__(
        self,
        prv_jwk: dict,
        domain_id: str,
        owner_type: str,
        audience: str,
        client_id: str = None,
        refresh_prv_jwk: dict = None,
    ):
        self.prv_jwk = prv_jwk
        self.domain_id = domain_id
        self.owner_type = owner_type
        self.audience = audience
        self.token_id = client_id or utils.random_string(16)
        self.refresh_prv_jwk = refresh_prv_jwk

        self._check_parameter()

    def _check_parameter(self):
        if not (self.prv_jwk and self.domain_id and self.audience):
            raise ERROR_GENERATE_KEY_FAILURE()

    def generate_token(
        self,
        token_type: str,
        expired_at: str = None,
        timeout: int = None,
        role_type: str = None,
        workspace_id: str = None,
        permissions: list = None,
        users_group: list = None,
        projects: list = None,
        injected_params: dict = None,
        identity_base_url: str = None,
    ) -> str:
        payload = {
            "iss": "spaceone.identity",
            "typ": token_type,
            "own": self.owner_type,
            "did": self.domain_id,
            "aud": self.audience,
            "jti": self.token_id,
            "iat": int(time.time()),
            "ver": "2.0",
        }

        if expired_at:
            payload["exp"] = int(utils.iso8601_to_datetime(expired_at).timestamp())
        elif timeout:
            payload["exp"] = int(time.time() + timeout)

        if role_type:
            payload["rol"] = role_type

        if workspace_id:
            payload["wid"] = workspace_id

        if permissions and len(permissions) > 0:
            payload["permissions"] = permissions

        if projects and len(projects) > 0:
            payload["projects"] = projects

        if users_group and len(users_group) > 0:
            payload["user_groups"] = users_group

        if injected_params:
            payload["injected_params"] = injected_params

        if identity_base_url:
            payload["identity_base_url"] = identity_base_url

        if token_type == "REFRESH_TOKEN":
            return JWTUtil.encode(payload, self.refresh_prv_jwk)
        else:
            return JWTUtil.encode(payload, self.prv_jwk)

    @staticmethod
    def _print_key(payload: dict):
        _LOGGER.debug(
            f"[KeyGenerator._print_key] generated payload. ( "
            f'iss: {payload.get("iss")}, '
            f'rol: {payload.get("rol")}, '
            f'typ: {payload.get("typ")}, '
            f'own: {payload.get("own")}, '
            f'did: {payload.get("did")}, '
            f'wid: {payload.get("wid")}, '
            f'aud: {payload.get("aud")}, '
            f'exp: {payload.get("exp")}, '
            f'iat: {payload.get("iat")}, '
            f'jti: {payload.get("jti")}, '
            f'projects: {payload.get("projects")},'
            f'user_groups: {payload.get("user_groups")},'
            f'permissions: {payload.get("permissions")},'
            f'injected_params: {payload.get("injected_params")},'
            f'identity_base_url: {payload.get("identity_base_url")},'
            f'ver: {payload.get("ver")} )'
        )
