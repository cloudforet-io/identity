from spaceone.core.service import *
from spaceone.core import utils
from spaceone.identity.manager import RoleBindingManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RoleBindingService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['resource_type', 'resource_id', 'role_id', 'domain_id'])
    def create(self, params):
        """ Create role binding

        Args:
            params (dict): {
                'resource_type': 'str',
                'resource_id': 'str',
                'role_id': 'str',
                'project_id': 'str',
                'project_group_id': 'str',
                'labels': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.role_binding_mgr.create_role_binding(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_binding_id', 'domain_id'])
    def update(self, params):
        """ Update role binding

        Args:
            params (dict): {
                'role_binding_id': 'str',
                'labels': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.role_binding_mgr.update_role_binding(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_binding_id', 'domain_id'])
    def delete(self, params):
        """ Delete role binding

        Args:
            params (dict): {
                'role_binding_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.role_binding_mgr.delete_role_binding(params['role_binding_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['role_binding_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group', 'project_info': 'project', 'role_info': 'role'})
    def get(self, params):
        """ Get role binding

        Args:
            params (dict): {
                'role_binding_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            role_binding_vo (object)
        """

        return self.role_binding_mgr.get_role_binding(params['role_binding_id'], params['domain_id'],
                                                      params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @change_only_key({'project_group_info': 'project_group', 'project_info': 'project', 'role_info': 'role'},
                     key_path='query.only')
    @append_query_filter(['role_binding_id', 'resource_type', 'resource_id', 'role_id', 'role_type',
                          'project_id', 'project_group_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['role_binding_id', 'resource_id', 'name'])
    def list(self, params):
        """ List role bindings

        Args:
            params (dict): {
                'role_binding_id': 'str',
                'resource_type': 'str',
                'resource_id': 'str',
                'role_id': 'str',
                'role_type': 'str',
                'project_id': 'str',
                'project_group_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of role_binding_vo'
            total_count (int)
        """
        query = params.get('query', {})

        return self.role_binding_mgr.list_role_bindings(params.get('query', {}))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['role_binding_id', 'resource_type', 'resource_id'])
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
        return self.role_binding_mgr.stat_role_bindings(query)
