import logging
from spaceone.core.auth.jwt import JWTUtil
from spaceone.core.cache import cacheable
from spaceone.core.manager import *
from spaceone.core import utils
from spaceone.identity.model.domain_secret_model import DomainSecret
from spaceone.identity.model.domain_model import Domain

_LOGGER = logging.getLogger(__name__)


class DomainSecretManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_secret_model: DomainSecret = self.locator.get_model('DomainSecret')

    def create_domain_secret(self, domain_id):
        def _rollback(vo):
            _LOGGER.info(f'[create_domain_secret._rollback] Delete domain-secret : {vo.domain_id} ({vo.secret[0:6]}...)')
            vo.delete()

        # Generate Domain-secret
        secret = self._generate_domain_secret(domain_id)

        # Generate Domain Key
        secret['domain_key'] = utils.random_string(16)

        domain_secret_vo: DomainSecret = self.domain_secret_model.create(secret)
        self.transaction.add_rollback(_rollback, domain_secret_vo)

    @cacheable(key='public-jwk:{domain_id}', expire=600)
    def get_domain_public_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        return domain_secret_vo.pub_jwk

    @cacheable(key='private-jwk:{domain_id}', expire=600)
    def get_domain_private_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        return domain_secret_vo.prv_jwk

    @cacheable(key='refresh-public-jwk:{domain_id}', expire=600)
    def get_domain_refresh_public_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        if not domain_secret_vo.refresh_pub_jwk:
            domain_secret_vo: DomainSecret = self._create_refresh_key(domain_secret_vo, domain_id)

        return domain_secret_vo.refresh_pub_jwk

    @cacheable(key='refresh-private-jwk:{domain_id}', expire=600)
    def get_domain_refresh_private_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        if not domain_secret_vo.refresh_pub_jwk:
            domain_secret_vo: DomainSecret = self._create_refresh_key(domain_secret_vo, domain_id)

        return domain_secret_vo.refresh_prv_jwk

    def _create_refresh_key(self, domain_secret_vo: DomainSecret, domain_id):
        domain_model: Domain = self.locator.get_model('Domain')
        domain_vo = domain_model.get(domain_id=domain_id)
        refresh_private_jwk, refresh_public_jwk = JWTUtil.generate_jwk()

        return domain_secret_vo.update({
            'refresh_pub_jwk': refresh_public_jwk,
            'refresh_prv_jwk': refresh_private_jwk,
            'domain': domain_vo,
        })

    def _generate_domain_secret(self, domain_id: str) -> dict:
        domain_model: Domain = self.locator.get_model('Domain')
        domain_vo = domain_model.get(domain_id=domain_id)

        private_jwk, public_jwk = JWTUtil.generate_jwk()
        refresh_private_jwk, refresh_public_jwk = JWTUtil.generate_jwk()
        data = {
            'pub_jwk': public_jwk,
            'prv_jwk': private_jwk,
            'refresh_pub_jwk': refresh_public_jwk,
            'refresh_prv_jwk': refresh_private_jwk,
            'domain_id': domain_id,
            'domain': domain_vo
        }
        return data
