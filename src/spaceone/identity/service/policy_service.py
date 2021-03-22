from spaceone.core.service import *
from spaceone.core import utils
from spaceone.identity.manager import PolicyManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PolicyService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['name', 'permissions', 'domain_id'])
    def create(self, params):
        """ Create policy

        Args:
            params (dict): {
                'name': 'str',
                'permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            policy_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.policy_mgr.create_policy(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'domain_id'])
    def update(self, params):
        """ Update policy

        Args:
            params (dict): {
                'policy_id': 'str',
                'name': 'str',
                'permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            policy_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.policy_mgr.update_policy(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'domain_id'])
    def delete(self, params):
        """ Delete policy

        Args:
            params (dict): {
                'policy_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.policy_mgr.delete_policy(params['policy_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['policy_id', 'domain_id'])
    def get(self, params):
        """ Get policy

        Args:
            params (dict): {
                'policy_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            domain_vo (object)
        """

        return self.policy_mgr.get_policy(params['policy_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['policy_id', 'name', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['policy_id', 'name'])
    def list(self, params):
        """ List polices

        Args:
            params (dict): {
                'policy_id': 'str',
                'name': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of policy_vo'
            total_count (int)
        """

        query = self._append_policy_type_filter(params.get('query', {}))
        return self.policy_mgr.list_policies(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['policy_id', 'name'])
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

        query = self._append_policy_type_filter(params.get('query', {}))
        return self.policy_mgr.stat_policies(query)

    @staticmethod
    def _append_policy_type_filter(query):
        query['filter'] = query.get('filter', [])
        query['filter'].append({
            'k': 'policy_type',
            'v': 'CUSTOM',
            'o': 'eq'
        })

        return query
