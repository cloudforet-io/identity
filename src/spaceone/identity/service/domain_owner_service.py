import logging
from spaceone.core.service import *
from spaceone.identity.manager import DomainManager, DomainOwnerManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.model import Domain


#@authentication_handler
#@authorization_handler
@event_handler
class DomainOwnerService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.domain_owner_mgr: DomainOwnerManager = self.locator.get_manager('DomainOwnerManager')

    @transaction
    @check_required(['owner_id', 'password', 'domain_id'])
    def create_owner(self, params):
        return self.domain_owner_mgr.create_owner(params)

    @transaction
    @check_required(['owner_id', 'domain_id'])
    def update_owner(self, params):
        return self.domain_owner_mgr.update_owner(params)

    @transaction
    @check_required(['domain_id', 'owner_id'])
    def delete_owner(self, params):
        self.domain_owner_mgr.delete_owner(params['domain_id'], params['owner_id'])

    @transaction
    @check_required(['domain_id'])
    def get_owner(self, params):
        return self.domain_owner_mgr.get_owner(params['domain_id'], params.get('owner_id'), params.get('only'))
