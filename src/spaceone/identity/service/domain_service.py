import logging

from spaceone.core.service import *
from spaceone.identity.manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.model import Domain


@authentication_handler(methods=['update', 'get'])
@authorization_handler(methods=['update', 'get'])
@mutation_handler
@event_handler
class DomainService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')

    @transaction
    @check_required(['name'])
    def create(self, params):
        """ Create domain

        Args:
            params (dict): {
                'name': 'str',
                'config': 'dict',
                'plugin_info': 'dict',
                'tags': 'list'
            }

        Returns:
            domain_vo (object)
        """

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
                'tags': 'list'
            }

        Returns:
            domain_vo (object)
        """

        return self.domain_mgr.update_domain(params)

    @transaction
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

    @transaction
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

    @transaction
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

    @transaction
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

    @transaction
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
