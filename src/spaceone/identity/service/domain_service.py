import logging

from spaceone.core.service import *
from spaceone.identity.manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.model import Domain


# @authentication_handler(exclude=[
#     'list_domains', 'get_public_key', 'get_domain_key'
# ])
#@authorization_handler
@event_handler
class DomainService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.domain_mgr: DomainManager = self.locator.get_manager('DomainManager')

    @transaction
    @check_required(['name'])
    def create_domain(self, params):
        # Create Domain
        domain_vo: Domain = self.domain_mgr.create_domain(params)

        # Create domain secret
        domain_secret_mgr: DomainSecretManager = self._get_domain_secret_manager()
        domain_secret_mgr.create_domain_secret(domain_vo.domain_id)

        return domain_vo

    @transaction
    @check_required(['domain_id'])
    def update_domain(self, params):
        return self.domain_mgr.update_domain(params)

    @transaction
    @check_required(['domain_id'])
    def delete_domain(self, params):
        self.domain_mgr.delete_domain(params['domain_id'])

        domain_secret_mgr: DomainSecretManager = self._get_domain_secret_manager()
        domain_secret_mgr.delete_domain_secret(params['domain_id'])

    @transaction
    @check_required(['domain_id'])
    def enable_domain(self, params):
        return self.domain_mgr.enable_domain(params['domain_id'])

    @transaction
    @check_required(['domain_id'])
    def disable_domain(self, params):
        return self.domain_mgr.disable_domain(params['domain_id'])

    @transaction
    @check_required(['domain_id'])
    def get_domain(self, params):
        return self.domain_mgr.get_domain(params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    def get_public_key(self, params):
        domain_id = params['domain_id']
        domain_secret_mgr: DomainSecretManager = self._get_domain_secret_manager()
        pub_jwk = domain_secret_mgr.get_domain_public_key(domain_id=domain_id)

        return {
            'pub_jwk': pub_jwk,
            'domain_id': domain_id
        }

    @transaction
    @append_query_filter(['domain_id', 'name'])
    @append_keyword_filter(['domain_id', 'name'])
    def list_domains(self, params):
        query = params.get('query', {})
        return self.domain_mgr.list_domains(query)

    @transaction
    @check_required(['query'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.domain_mgr.stat_domains(query)

    def _get_domain_secret_manager(self):
        return self.locator.get_manager('DomainSecretManager')
