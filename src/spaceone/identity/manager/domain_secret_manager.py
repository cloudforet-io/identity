import logging
from spaceone.core.auth.jwt import JWTUtil
from spaceone.core import cache
from spaceone.core.manager import *
from spaceone.core import utils
from spaceone.identity.model.domain.database import Domain, DomainSecret
from spaceone.identity.manager.domain_manager import DomainManager

_LOGGER = logging.getLogger(__name__)


class DomainSecretManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_secret_model = DomainSecret
        self.domain_mgr = DomainManager()

    def create_domain_secret(self, domain_vo: Domain) -> None:
        def _rollback(vo: DomainSecret):
            _LOGGER.info(
                f"[create_domain_secret._rollback] Delete domain secret: {vo.domain_id}"
            )
            vo.delete()

        # Generate Domain-secret
        secret = self._generate_domain_secret(domain_vo)

        # Generate Domain Key
        secret["domain_key"] = utils.random_string(16)

        domain_secret_vo: DomainSecret = self.domain_secret_model.create(secret)
        self.transaction.add_rollback(_rollback, domain_secret_vo)

    def delete_domain_secret(self, domain_id: str) -> None:
        domain_secret_vos = self.domain_secret_model.filter(domain_id=domain_id)
        domain_secret_vos.delete()
        cache.delete(f"identity:public-jwk:{domain_id}")
        cache.delete(f"identity:private-jwk:{domain_id}")
        cache.delete(f"identity:refresh-public-jwk:{domain_id}")
        cache.delete(f"identity:refresh-private-jwk:{domain_id}")

    @cache.cacheable(key="identity:public-jwk:{domain_id}", expire=600)
    def get_domain_public_key(self, domain_id: str) -> dict:
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(
            domain_id=domain_id
        )
        return domain_secret_vo.pub_jwk

    @cache.cacheable(key="identity:private-jwk:{domain_id}", expire=600)
    def get_domain_private_key(self, domain_id: str) -> dict:
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(
            domain_id=domain_id
        )
        return domain_secret_vo.prv_jwk

    @cache.cacheable(key="identity:refresh-public-jwk:{domain_id}", expire=600)
    def get_domain_refresh_public_key(self, domain_id: str) -> dict:
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(
            domain_id=domain_id
        )
        return domain_secret_vo.refresh_pub_jwk

    @cache.cacheable(key="identity:refresh-private-jwk:{domain_id}", expire=600)
    def get_domain_refresh_private_key(self, domain_id: str) -> dict:
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(
            domain_id=domain_id
        )
        return domain_secret_vo.refresh_prv_jwk

    @staticmethod
    def _generate_domain_secret(domain_vo: Domain) -> dict:
        private_jwk, public_jwk = JWTUtil.generate_jwk()
        refresh_private_jwk, refresh_public_jwk = JWTUtil.generate_jwk()
        data = {
            "pub_jwk": public_jwk,
            "prv_jwk": private_jwk,
            "refresh_pub_jwk": refresh_public_jwk,
            "refresh_prv_jwk": refresh_private_jwk,
            "domain_id": domain_vo.domain_id,
            "domain": domain_vo,
        }
        return data
