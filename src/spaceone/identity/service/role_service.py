from spaceone.core.service import *
from spaceone.core.error import *
from spaceone.core import config
from spaceone.identity.manager import RoleManager, PolicyManager, DomainManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RoleService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.role_mgr: RoleManager = self.locator.get_manager('RoleManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'role_type', 'policies', 'domain_id'])
    def create(self, params):
        """ Create role

        Args:
            params (dict): {
                'name': 'str',
                'role_type': 'str',
                'policies': 'list',
                'page_permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            role_vo (object)
        """

        # The system role type is allowed only in the root domain.
        if params['role_type'] == 'SYSTEM':
            self._check_system_role_type(params['domain_id'])

        params['policies'] = self._check_policy_info(params['policies'], params['domain_id'])

        return self.role_mgr.create_role(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_id', 'domain_id'])
    def update(self, params):
        """ Update role

        Args:
            params (dict): {
                'role_id': 'str',
                'name': 'str',
                'policies': 'list',
                'page_permissions': 'list',
                'tags': 'dict',
                'release_page_permissions': 'bool',
                'domain_id': 'str'
            }

        Returns:
            role_vo (object)
        """

        release_page_permissions = params.get('release_page_permissions', False)

        if release_page_permissions:
            params['page_permissions'] = []

        if 'policies' in params:
            params['policies'] = self._check_policy_info(params['policies'], params['domain_id'])

        return self.role_mgr.update_role(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_id', 'domain_id'])
    def delete(self, params):
        """ Delete role

        Args:
            params (dict): {
                'role_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.role_mgr.delete_role(params['role_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_id', 'domain_id'])
    def get(self, params):
        """ Get role

        Args:
            params (dict): {
                'role_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            role_vo (object)
        """

        return self.role_mgr.get_role(params['role_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['role_id', 'name', 'role_type', 'policy_id', 'domain_id'])
    @append_keyword_filter(['role_id', 'name'])
    def list(self, params):
        """ List roles

        Args:
            params (dict): {
                'role_id': 'str',
                'name': 'str',
                'role_type': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of role_vo'
            total_count (int)
        """

        return self.role_mgr.list_roles(params.get('query', {}))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @append_keyword_filter(['role_id', 'name'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.role_mgr.stat_roles(query)

    def _check_policy_info(self, policies, domain_id):
        policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')

        change_policies = []
        for policy in policies:
            if policy['policy_type'] == 'MANAGED':
                policy['policy'] = policy_mgr.get_managed_policy(policy['policy_id'], domain_id)
            elif policy['policy_type'] == 'CUSTOM':
                policy['policy'] = policy_mgr.get_policy(policy['policy_id'], domain_id)
            change_policies.append(policy)

        return change_policies

    def _check_system_role_type(self, domain_id):
        root_domain_name = config.get_global('ROOT_DOMAIN_NAME', 'root')
        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain_vo = domain_mgr.get_domain(domain_id)

        if root_domain_name != domain_vo.name:
            raise ERROR_PERMISSION_DENIED()
