import logging
from spaceone.core.auth.jwt import JWTUtil
from spaceone.core.cache import cacheable
from spaceone.core.manager import *
from spaceone.core import utils
from spaceone.identity.lib.key_generator import KeyGenerator
from spaceone.identity.model.domain_secret_model import DomainSecret

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
        secret['domain_key'] = utils.random_string()

        secret_vo: DomainSecret = self.domain_secret_model.create(secret)
        self.transaction.add_rollback(_rollback, secret_vo)

    def delete_domain_secret(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        domain_secret_vo.delete()

    @cacheable(key='pub-jwk:{domain_id}', expire=600)
    def get_domain_public_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        pub_jwk = domain_secret_vo.pub_jwk
        return pub_jwk

    @cacheable(key='pri-jwk:{domain_id}', expire=600)
    def get_domain_private_key(self, domain_id):
        domain_secret_vo: DomainSecret = self.domain_secret_model.get(domain_id=domain_id)
        prv_jwk = domain_secret_vo.prv_jwk
        return prv_jwk

    @staticmethod
    def _generate_domain_secret(domain_id: str) -> dict:
        prv_jwk, pub_jwk = JWTUtil.generate_jwk()
        data = {
            'domain_id': domain_id,
            'pub_jwk': pub_jwk,
            'prv_jwk': prv_jwk
        }
        return data
