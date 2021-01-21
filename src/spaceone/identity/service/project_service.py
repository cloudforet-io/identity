import logging
from spaceone.core.service import *
from spaceone.identity.error.error_project import *
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProjectService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['name', 'project_group_id', 'domain_id'])
    def create(self, params):
        """ Create project

        Args:
            params (dict): {
                'name': 'str',
                'project_group_id': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_vo (object)
        """

        params['created_by'] = self.transaction.get_meta('user_id')

        if 'project_group_id' in params:
            project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')
            params['project_group'] = project_group_mgr.get_project_group(params['project_group_id'],
                                                                          params['domain_id'])

        return self.project_mgr.create_project(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'domain_id'])
    def update(self, params):
        """ Update project

        Args:
            params (dict): {
                'project_id': 'str',
                'name': 'str',
                'project_group_id': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_vo (object)
        """

        domain_id = params['domain_id']

        project_vo = self.project_mgr.get_project(params['project_id'], domain_id)

        if 'project_group_id' in params:
            project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')
            params['project_group'] = project_group_mgr.get_project_group(params['project_group_id'], domain_id)

        return self.project_mgr.update_project_by_vo(params, project_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'domain_id'])
    def delete(self, params):
        """ Delete project

        Args:
            params (dict): {
                'project_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        project_vo = self.project_mgr.get_project(params['project_id'], params['domain_id'])
        self.project_mgr.delete_project_by_vo(project_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group'})
    def get(self, params):
        """ Get project

        Args:
            params (dict): {
                'project_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            project_vo (object)
        """

        return self.project_mgr.get_project(params['project_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'PROJECT',
                              'mutation.append_parameter': {'project_id': 'authorization.projects'}})
    @check_required(['domain_id'])
    @change_only_key({'project_group_info': 'project_group'}, key_path='query.only')
    @append_query_filter(['project_id', 'name', 'project_group_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_id', 'name'])
    def list(self, params):
        """ List projects

        Args:
            params (dict): {
                'project_id': 'str',
                'name': 'str',
                'project_group_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of project_vo'
            total_count (int)
        """
        query = params.get('query', {})

        # Temporary code for DB migration
        if 'only' in query:
            query['only'] += ['project_group_id']

        return self.project_mgr.list_projects(params.get('query', {}))

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'user_id', 'role_id', 'domain_id'])
    def add_member(self, params):
        """ Add project member

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'role_id': 'str',
                'labels': 'list',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        params['resource_type'] = 'identity.User'
        params['resource_id'] = params['user_id']
        del params['user_id']

        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

        role_vo = role_mgr.get_role(params['role_id'], params['domain_id'])
        if role_vo.role_type != 'PROJECT':
            raise ERROR_ONLY_PROJECT_ROLE_TYPE_ALLOWED()

        return role_binding_mgr.create_role_binding(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'user_id', 'domain_id'])
    def modify_member(self, params):
        """ Modify project member

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'labels': 'list',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        project_id = params['project_id']
        user_id = params['user_id']
        domain_id = params['domain_id']

        project_vo = self.project_mgr.get_project(project_id, domain_id)

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')
        role_binding_vos = role_binding_mgr.get_project_role_binding('identity.User', user_id, domain_id,
                                                                     project_vo=project_vo)

        if role_binding_vos.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        return role_binding_mgr.update_role_binding_by_vo(params, role_binding_vos[0])

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'user_id', 'domain_id'])
    def remove_member(self, params):
        """ Remove project member

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        project_id = params['project_id']
        user_id = params['user_id']
        domain_id = params['domain_id']

        project_vo = self.project_mgr.get_project(project_id, domain_id)

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')
        role_binding_vos = role_binding_mgr.get_project_role_binding('identity.User', user_id, domain_id,
                                                                     project_vo=project_vo)

        if role_binding_vos.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        for role_binding_vo in role_binding_vos:
            role_binding_mgr.delete_role_binding_by_vo(role_binding_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group', 'project_info': 'project', 'role_info': 'role'},
                     key_path='query.only')
    @append_query_filter(['project_id', 'user_id', 'role_id'])
    @append_keyword_filter(['resource_id'])
    def list_members(self, params):
        """ List project members

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'role_id': 'str',
                'domain_id': 'str',
                'include_parent_member': 'bool',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of role_binding_vo'
            total_count (int)
        """

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

        query = params.get('query', {})

        # TODO: include_parent_member filter
        query['filter'] = list(map(self._change_filter, query.get('filter', [])))

        return role_binding_mgr.list_role_bindings(query)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_id', 'name'])
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
        return self.project_mgr.stat_projects(query)

    @staticmethod
    def _change_filter(condition):
        if condition.get('key') == 'user_id':
            condition['key'] = 'resource_id'
        elif condition.get('k') == 'user_id':
            condition['k'] = 'resource_id'

        return condition
