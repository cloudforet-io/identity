from spaceone.core.service import *
from spaceone.identity.manager import APIKeyManager, UserManager

#@authentication_handler
#@authorization_handler
@event_handler
class APIKeyService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.api_key_mgr: APIKeyManager = self.locator.get_manager('APIKeyManager')

    @transaction
    @check_required(['user_id', 'domain_id'])
    def create_api_key(self, params):
        user_id = params['user_id']
        domain_id = params['domain_id']

        # Check user is exists.
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        user_mgr.get_user(user_id=user_id, domain_id=domain_id)

        return self.api_key_mgr.create_api_key(user_id=user_id, domain_id=domain_id)

    @transaction
    @check_required(['api_key_id', 'domain_id'])
    def delete_api_key(self, params):
        self.api_key_mgr.delete_api_key(params['api_key_id'], params['domain_id'])

    @transaction
    @check_required(['api_key_id', 'domain_id'])
    def enable_api_key(self, params):
        return self.api_key_mgr.enable_api_key(params['api_key_id'], params['domain_id'])

    @transaction
    @check_required(['api_key_id', 'domain_id'])
    def disable_api_key(self, params):
        return self.api_key_mgr.disable_api_key(params['api_key_id'], params['domain_id'])

    @transaction
    @check_required(['api_key_id', 'domain_id'])
    def get_api_key(self, params):
        return self.api_key_mgr.get_api_key(params['api_key_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['api_key_id', 'state', 'api_key_type', 'user_id', 'domain_id'])
    @append_keyword_filter(['api_key_id', 'user_id'])
    def list_api_keys(self, params):
        return self.api_key_mgr.list_api_keys(params.get('query', {}))

    @transaction
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.api_key_mgr.stat_api_keys(query)
