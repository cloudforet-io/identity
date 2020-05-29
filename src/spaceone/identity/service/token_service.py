import logging

from spaceone.core.auth.jwt import JWTAuthenticator, JWTUtil
from spaceone.core.service import *
from spaceone.identity.error.error_authentication import *
from spaceone.identity.manager import DomainManager, DomainSecretManager
from spaceone.identity.model import Domain

_LOGGER = logging.getLogger(__name__)


@authentication_handler(methods=['refresh_token'])
@event_handler
class TokenService(BaseService):

    @transaction
    @check_required(['credentials', 'domain_id'])
    def issue_token(self, params):
        user_type = params['credentials'].get('user_type', 'USER')

        domain_secret_mgr: DomainSecretManager = self.locator.get_manager('DomainSecretManager')
        private_key = domain_secret_mgr.get_domain_private_key(domain_id=params['domain_id'])

        token_manager = self._create_token_manager(params['domain_id'], user_type)
        token_manager.authenticate(params['credentials'], params['domain_id'])

        return token_manager.issue_token(private_jwk=private_key)

    @transaction
    def refresh_token(self, params):
        refresh_token = self.transaction.get_meta('token')
        domain_id = _extract_domain_id(refresh_token)

        domain_secret_mgr: DomainSecretManager = self.locator.get_manager('DomainSecretManager')
        public_jwk = domain_secret_mgr.get_domain_public_key(domain_id=domain_id)
        private_jwk = domain_secret_mgr.get_domain_private_key(domain_id=domain_id)

        token_info = _verify_refresh_token(refresh_token, public_jwk)
        token_mgr = self._create_token_manager(domain_id, token_info['user_type'])
        token_mgr.check_refreshable(token_info['key'], token_info['ttl'])

        return token_mgr.refresh_token(token_info['user_id'], domain_id,
                                       ttl=token_info['ttl']-1, private_jwk=private_jwk)

    def _create_token_manager(self, domain_id, user_type):
        if user_type == 'DOMAIN_OWNER':
            return self.locator.get_manager('DomainOwnerTokenManager')

        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain: Domain = domain_mgr.get_domain(domain_id)
        if domain.plugin_info is None:
            return self.locator.get_manager('DefaultTokenManager')
        else:
            return self.locator.get_manager('PluginTokenManager')


def _extract_domain_id(token):
    try:
        decoded = JWTUtil.unverified_decode(token)
    except Exception as e:
        _LOGGER.error(f'[_extract_domain_id] {e}')
        raise ERROR_AUTHENTICATE_FAILURE(message='Cannot decode token.')

    domain_id = decoded.get('did')

    if domain_id is None:
        raise ERROR_AUTHENTICATE_FAILURE(message='Empty domain_id provided.')

    return domain_id


def _verify_refresh_token(token, public_jwk):
    try:
        decoded = JWTAuthenticator(public_jwk).validate(token)
    except Exception as e:
        _LOGGER.error(f'[_verify_refresh_token] {e}')
        raise ERROR_AUTHENTICATE_FAILURE(message='Token validation failed.')

    if decoded.get('cat') != 'REFRESH_TOKEN':
        raise ERROR_INVALID_REFRESH_TOKEN()

    return {
        'user_id': decoded['aud'],
        'user_type': decoded['user_type'],
        'key': decoded['key'],
        'ttl': decoded['ttl']
    }
