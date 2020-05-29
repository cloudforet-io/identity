from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.identity.manager import RoleManager, PolicyManager

@authentication_handler
@authorization_handler
@event_handler
class RoleService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.role_mgr: RoleManager = self.locator.get_manager('RoleManager')

    @transaction
    @check_required(['name', 'role_type', 'policies', 'domain_id'])
    def create_role(self, params):
        params['policies'] = self._check_policy_info(params['policies'], params['domain_id'])
        return self.role_mgr.create_role(params)

    @transaction
    @check_required(['role_id', 'domain_id'])
    def update_role(self, params):
        if 'policies' in params:
            params['policies'] = self._check_policy_info(params['policies'], params['domain_id'])

        return self.role_mgr.update_role(params)

    @transaction
    @check_required(['role_id', 'domain_id'])
    def delete_role(self, params):
        self.role_mgr.delete_role(params['role_id'], params['domain_id'])

    @transaction
    @check_required(['role_id', 'domain_id'])
    def get_role(self, params):
        return self.role_mgr.get_role(params['role_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['role_id', 'name', 'role_type', 'domain_id'])
    @append_keyword_filter(['role_id', 'name'])
    def list_roles(self, params):
        return self.role_mgr.list_roles(params.get('query', {}))

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
        return self.role_mgr.stat_roles(query)

    def _check_policy_info(self, policies, domain_id):
        policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')

        change_policies = []
        for policy in policies:
            if policy['policy_type'] == 'MANAGED':
                # TODO: Check External URL
                pass
            elif policy['policy_type'] == 'CUSTOM':
                policy['policy'] = policy_mgr.get_policy(policy['policy_id'], domain_id)
                del policy['policy_id']
            change_policies.append(policy)

        return change_policies
