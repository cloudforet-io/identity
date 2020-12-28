import logging

from spaceone.core import cache
from spaceone.core.auth.jwt import JWTAuthenticator, JWTUtil
from spaceone.core.service import *
from spaceone.identity.error.error_authentication import *
from spaceone.identity.error.error_domain import *
from spaceone.identity.manager import DomainManager, DomainSecretManager, UserManager
from spaceone.identity.model import User, Domain

_LOGGER = logging.getLogger(__name__)


@event_handler
class TokenService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.user_mgr: UserManager = self.locator.get_manager('UserManager')
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        self.domain_secret_mgr: DomainSecretManager = self.locator.get_manager('DomainSecretManager')

    @transaction
    @check_required(['user_id', 'credentials', 'domain_id'])
    def issue(self, params):
        """ Issue token

        Args:
            params (dict): {
                'user_id': 'str',
                'credentials': 'dict'
                'user_type': 'str',
                'domain_id': 'str'
            }

        Returns:
            result (dict): {
                'access_token': 'str',
                'refresh_token': 'str'
            }
        """

        user_id = params['user_id']
        user_type = params.get('user_type', 'USER')
        domain_id = params['domain_id']

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)
        refresh_private_jwk = self.domain_secret_mgr.get_domain_refresh_private_key(domain_id=domain_id)

        token_manager = self._get_token_manager(user_id, user_type, domain_id)
        token_manager.authenticate(user_id, domain_id, params['credentials'])

        return token_manager.issue_token(private_jwk=private_jwk, refresh_private_jwk=refresh_private_jwk)

    @transaction
    def refresh(self, params):
        """ Refresh token

        Args:
            params (dict): {}

        Returns:
            result (dict): {
                'access_token': 'str',
                'refresh_token': 'str'
            }
        """

        refresh_token = self.transaction.get_meta('token')
        domain_id = _extract_domain_id(refresh_token)

        private_jwk = self.domain_secret_mgr.get_domain_private_key(domain_id=domain_id)
        refresh_public_jwk = self.domain_secret_mgr.get_domain_refresh_public_key(domain_id=domain_id)
        refresh_private_jwk = self.domain_secret_mgr.get_domain_refresh_private_key(domain_id=domain_id)

        token_info = _verify_refresh_token(refresh_token, refresh_public_jwk)
        token_mgr = self._get_token_manager(token_info['user_id'], token_info['user_type'], domain_id)
        token_mgr.check_refreshable(token_info['key'], token_info['ttl'])

        return token_mgr.refresh_token(token_info['user_id'], domain_id, ttl=token_info['ttl']-1,
                                       private_jwk=private_jwk, refresh_private_jwk=refresh_private_jwk)

    def _get_token_manager(self, user_id, user_type, domain_id):
        self._check_domain_state(domain_id)

        # user_type = USER | API_USER | DOMAIN_OWNER
        if user_type == 'DOMAIN_OWNER':
            return self.locator.get_manager('DomainOwnerTokenManager')

        user_backend = self._get_user_backend(user_id, domain_id)

        if user_backend == 'LOCAL':
            return self.locator.get_manager('LocalTokenManager')
        else:
            return self.locator.get_manager('ExternalTokenManager')

    @cache.cacheable(key='user-backend:{domain_id}:{user_id}', expire=600)
    def _get_user_backend(self, user_id, domain_id):
        try:
            user_vo: User = self.user_mgr.get_user(user_id, domain_id)
        except Exception as e:
            _LOGGER.error(f'[_get_user_backend] Authentication failure: {getattr(e, "message", e)}')
            raise ERROR_AUTHENTICATION_FAILURE(user_id=user_id)

        return user_vo.backend

    @cache.cacheable(key='domain-state:{domain_id}', expire=3600)
    def _check_domain_state(self, domain_id):
        domain_vo: Domain = self.domain_mgr.get_domain(domain_id)

        if domain_vo.state != 'ENABLED':
            raise ERROR_DOMAIN_STATE(domain_id=domain_vo.domain_id)


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
