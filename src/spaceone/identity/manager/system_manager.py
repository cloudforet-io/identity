import logging

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager

_LOGGER = logging.getLogger(__name__)


class SystemManager(BaseManager):
    @staticmethod
    def get_root_domain_id():
        return "domain-root"

    @staticmethod
    def create_system_token(root_domain_id: str, admin_user_id: str) -> str:
        domain_secret_mgr = DomainSecretManager()
        prv_jwk = domain_secret_mgr.get_domain_private_key(root_domain_id)

        key_gen = KeyGenerator(prv_jwk, root_domain_id, "SYSTEM", admin_user_id)
        return key_gen.generate_token("SYSTEM_TOKEN")
