from spaceone.core.service import *
from spaceone.identity.manager import PolicyManager


@authentication_handler
@authorization_handler
@event_handler
class PolicyService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')

    @transaction
    @check_required(['name', 'permissions', 'domain_id'])
    def create_policy(self, params):
        return self.policy_mgr.create_policy(params)

    @transaction
    @check_required(['policy_id', 'domain_id'])
    def update_policy(self, params):
        return self.policy_mgr.update_policy(params)

    @transaction
    @check_required(['policy_id', 'domain_id'])
    def delete_policy(self, params):
        self.policy_mgr.delete_policy(params['policy_id'], params['domain_id'])

    @transaction
    @check_required(['policy_id', 'domain_id'])
    def get_policy(self, params):
        return self.policy_mgr.get_policy(params['policy_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['policy_id', 'name', 'domain_id'])
    @append_keyword_filter(['policy_id', 'name'])
    def list_policies(self, params):
        return self.policy_mgr.list_policies(params.get('query', {}))

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
        return self.policy_mgr.stat_policies(query)
