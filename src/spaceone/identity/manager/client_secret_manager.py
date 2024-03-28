import logging
from typing import Tuple

from spaceone.core.manager import BaseManager
from spaceone.core import utils

from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager

_LOGGER = logging.getLogger(__name__)


class ClientSecretManager(BaseManager):
    @staticmethod
    def generate_client_secret(
        app_id: str,
        domain_id: str,
        expired_at: str,
        role_type: str,
        workspace_id: str = None,
        permissions: list = None,
        injected_params: dict = None,
    ) -> Tuple[str, str]:
        domain_secret_mgr = DomainSecretManager()
        prv_jwk = domain_secret_mgr.get_domain_private_key(domain_id)
        refresh_prv_jwk = domain_secret_mgr.get_domain_refresh_private_key(domain_id)
        client_id = utils.generate_id("client")

        key_gen = KeyGenerator(
            prv_jwk,
            domain_id,
            "APP",
            app_id,
            client_id=client_id,
            refresh_prv_jwk=refresh_prv_jwk,
        )

        client_secret = key_gen.generate_token(
            "CLIENT_SECRET",
            expired_at=expired_at,
            role_type=role_type,
            workspace_id=workspace_id,
            permissions=permissions,
            injected_params=injected_params,
        )

        return client_id, client_secret
