import logging

from spaceone.core.service import *
from spaceone.core import utils
from spaceone.identity.error import *
from spaceone.identity.manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.model import Domain

_LOGGER = logging.getLogger(__name__)


@authentication_handler(exclude=['create', 'list', 'get_public_key'])
@authorization_handler(exclude=['create', 'list', 'get_public_key'])
@mutation_handler(exclude=['create', 'list', 'get_public_key'])
@event_handler
class DomainService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name'])
    def create(self, params):
        """ Create domain

        Args:
            params (dict): {
                'name': 'str',
                'config': 'dict',
                'plugin_info': 'dict',
                'tags': 'dict'
            }

        Returns:
            domain_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        # Create Domain
        domain_vo: Domain = self.domain_mgr.create_domain(params)

        # Create domain secret
        domain_secret_mgr: DomainSecretManager = self._get_domain_secret_manager()
        domain_secret_mgr.create_domain_secret(domain_vo.domain_id)

        return domain_vo

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def update(self, params):
        """ Update domain

        Args:
            params (dict): {
                'domain_id': 'str',
                'config': 'dict',
                'tags': 'dict'
            }

        Returns:
            domain_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.domain_mgr.update_domain(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def change_auth_plugin(self, params):
        """ Change domain auth plugin

        Args:
            params (dict): {
                'domain_id': 'str',
                'plugin_info': 'dict',
                'release_auth_plugin': 'bool'
            }

        Returns:
            domain_vo (object)
        """

        domain_id = params['domain_id']
        plugin_info = params.get('plugin_info')
        release_auth_plugin = params.get('release_auth_plugin', False)

        if release_auth_plugin:
            # release auth plugin
            _LOGGER.debug(f'[change_auth_plugin] release auth plugin')
            return self.domain_mgr.release_auth_plugin(domain_id)
        else:
            if plugin_info is None:
                raise ERROR_REQUIRED_PARAMETER(key='plugin_info')

            _LOGGER.debug(f'[change_auth_plugin] update plugin_info: {plugin_info}')
            return self.domain_mgr.change_auth_plugin(domain_id, plugin_info)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def update_plugin(self, params):
        """ Update Plugin
        Args:
            params (dict): {
                'domain_id': 'str',
                'version': 'str',
                'options': 'dict',
                'upgrade_mode': 'str',
            }

        Returns:
            domain_vo (object)
        """

        domain_id = params['domain_id']
        version = params.get('version')
        options = params.get('options')
        upgrade_mode = params.get('upgrade_mode')

        return self.domain_mgr.update_domain_plugin(domain_id, version, options, upgrade_mode)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def verify_plugin(self, params):
        """ Update Plugin
        Args:
            params (dict): {
                'domain_id': 'str',
            }

        Returns:
            domain_vo (object)
        """
        domain_id = params['domain_id']
        return self.domain_mgr.verify_auth_plugin(domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def delete(self, params):
        """ Delete domain

        Args:
            params (dict): {
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.domain_mgr.delete_domain(params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def enable(self, params):
        """ Enable domain

        Args:
            params (dict): {
                'domain_id': 'str'
            }

        Returns:
            domain_vo (object)
        """

        return self.domain_mgr.enable_domain(params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def disable(self, params):
        """ Disable domain

        Args:
            params (dict): {
                'domain_id': 'str'
            }

        Returns:
            domain_vo (object)
        """

        return self.domain_mgr.disable_domain(params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def get(self, params):
        """ Disable domain

        Args:
            params (dict): {
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            domain_vo (object)
        """

        return self.domain_mgr.get_domain(params['domain_id'], params.get('only'))

    @transaction(append_meta={'auth.scope': 'SYSTEM'})
    @check_required(['domain_id'])
    def get_public_key(self, params):
        """ Get domain's public key for authentication

        Args:
            params (dict): {
                'domain_id': 'str'
            }

        Returns:
            result (dict): {
                'pub_jwk': 'str',
                'domain_id': 'str'
            }
        """

        domain_id = params['domain_id']
        domain_secret_mgr: DomainSecretManager = self._get_domain_secret_manager()
        pub_jwk = domain_secret_mgr.get_domain_public_key(domain_id=domain_id)

        return {
            'pub_jwk': pub_jwk,
            'domain_id': domain_id
        }

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @append_query_filter(['domain_id', 'name'])
    @change_tag_filter('tags')
    @append_keyword_filter(['domain_id', 'name'])
    def list(self, params):
        """ List api keys

        Args:
            params (dict): {
                'domain_id': 'str',
                'name': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of domain_vo'
            total_count (int)
        """

        query = params.get('query', {})
        return self.domain_mgr.list_domains(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query'])
    @change_tag_filter('tags')
    @append_keyword_filter(['domain_id', 'name'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.domain_mgr.stat_domains(query)

    def _get_domain_secret_manager(self):
        return self.locator.get_manager('DomainSecretManager')
