import logging
from spaceone.core import cache
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
class ProjectGroupService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'authorization.project_group_id': 'parent_project_group_id',
        'authorization.require_project_group_id': True
    })
    @check_required(['name', 'domain_id'])
    def create(self, params):
        """ Create project group

        Args:
            params (dict): {
                'name': 'str',
                'parent_project_group_id': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_group_vo (object)
        """

        params['created_by'] = self.transaction.get_meta('user_id')

        if 'parent_project_group_id' in params:
            params['parent_project_group'] = self._get_parent_project_group(params['parent_project_group_id'],
                                                                            params['domain_id'])
        else:
            params['parent_project_group'] = None

        return self.project_group_mgr.create_project_group(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'domain_id'])
    def update(self, params):
        """ Update project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'parent_project_group_id': 'str',
                'release_parent_project_group': 'bool',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_group_vo (object)
        """

        domain_id = params['domain_id']
        release_parent_project_group = params.get('release_parent_project_group', False)

        project_group_vo = self.project_group_mgr.get_project_group(params['project_group_id'], domain_id)

        if release_parent_project_group:
            params['parent_project_group'] = None
            params['parent_project_group_id'] = None
        else:
            if 'parent_project_group_id' in params:
                params['parent_project_group'] = self._get_parent_project_group(
                    params['parent_project_group_id'], params['domain_id'], params['project_group_id'])

        return self.project_group_mgr.update_project_group_by_vo(params, project_group_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'domain_id'])
    def delete(self, params):
        """ Delete project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        project_group_vo = self.project_group_mgr.get_project_group(params['project_group_id'], params['domain_id'])
        self.project_group_mgr.delete_project_group_by_vo(project_group_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'domain_id'])
    @change_only_key({'parent_project_group_info': 'parent_project_group'})
    def get(self, params):
        """ Get project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            project_group_vo
        """

        return self.project_group_mgr.get_project_group(params['project_group_id'], params['domain_id'],
                                                        params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @change_only_key({'parent_project_group_info': 'parent_project_group'}, key_path='query.only')
    @append_query_filter(['project_group_id', 'name', 'parent_project_group_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_group_id', 'name'])
    def list(self, params):
        """ List project groups

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'parent_project_group_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_project_groups': 'list', # from meta
            }

        Returns:
            results (list): 'list of project_group_vo'
            total_count (int)
        """
        query = params.get('query', {})
        user_project_groups = self.transaction.get_meta('authorization.project_groups')
        domain_id = params['domain_id']

        # Temporary code for DB migration
        if 'only' in query:
            query['only'] += ['parent_project_group_id']

        # For Access Control
        self._append_user_project_group_filter(query, user_project_groups, domain_id)

        return self.project_group_mgr.list_project_groups(query)

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'mutation.append_parameter': {'user_project_groups': 'authorization.project_groups'}
    })
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id', 'user_project_groups'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_id', 'name'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'user_project_groups': 'list', # from meta
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.project_group_mgr.stat_project_groups(query)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'user_id', 'role_id', 'domain_id'])
    def add_member(self, params):
        """ Add project group member

        Args:
            params (dict): {
                'project_group_id': 'str',
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
    @check_required(['project_group_id', 'user_id', 'domain_id'])
    def modify_member(self, params):
        """ Modify project group member

        Args:
            params (dict): {
                'project_group_id': 'str',
                'user_id': 'str',
                'labels': 'list',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        project_group_id = params['project_group_id']
        user_id = params['user_id']
        domain_id = params['domain_id']

        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')
        role_binding_vos = role_binding_mgr.get_project_role_binding('identity.User', user_id, domain_id,
                                                                     project_group_vo=project_group_vo)

        if role_binding_vos.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        return role_binding_mgr.update_role_binding_by_vo(params, role_binding_vos[0])

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'domain_id', 'user_id'])
    def remove_member(self, params):
        """ Remove project group member

        Args:
            params (dict): {
                'project_group_id': 'str',
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        project_group_id = params['project_group_id']
        user_id = params['user_id']
        domain_id = params['domain_id']

        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')
        role_binding_vos = role_binding_mgr.get_project_role_binding('identity.User', user_id, domain_id,
                                                                     project_group_vo=project_group_vo)

        if role_binding_vos.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        for role_binding_vo in role_binding_vos:
            role_binding_mgr.delete_role_binding_by_vo(role_binding_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['project_group_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group', 'project_info': 'project', 'role_info': 'role'},
                     key_path='query.only')
    @append_query_filter(['project_group_id', 'user_id', 'role_id'])
    @append_keyword_filter(['resource_id'])
    def list_members(self, params):
        """ List users in project group

        Args:
            params (dict): {
                'project_group_id': 'str',
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
    @check_required(['project_group_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group'}, key_path='query.only')
    @append_keyword_filter(['project_id', 'name'])
    @change_tag_filter('tags')
    @append_keyword_filter(['project_id', 'name'])
    def list_projects(self, params):
        """ List projects in project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'recursive': 'bool',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of project_vo'
            total_count (int)
        """

        project_group_id = params['project_group_id']
        domain_id = params['domain_id']
        recursive = params.get('recursive', False)
        query = params.get('query', {})

        project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')

        if 'filter' not in query:
            query['filter'] = []

        related_project_groups = []
        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
        related_project_groups.append(project_group_vo)

        if recursive:
            related_project_groups = self._get_related_project_group(project_group_vo, related_project_groups)

        query['filter'].append({
            'k': 'project_group',
            'v': related_project_groups,
            'o': 'in'
        })

        # Temporary code for DB migration
        if 'only' in query:
            query['only'] += ['project_group_id']

        return project_mgr.list_projects(query)

    @staticmethod
    def _change_filter(condition):
        if condition.get('key') == 'user_id':
            condition['key'] = 'resource_id'
        elif condition.get('k') == 'user_id':
            condition['k'] = 'resource_id'

        return condition

    def _get_related_project_group(self, project_group_vo, related_project_groups):
        query = {
            'filter': [{
                'k': 'parent_project_group',
                'v': project_group_vo,
                'o': 'eq'
            }]
        }

        project_group_vos, total_count = self.project_group_mgr.list_project_groups(query)

        if total_count > 0:
            related_project_groups += project_group_vos
            for pg_vo in project_group_vos:
                related_project_groups = self._get_related_project_group(pg_vo, related_project_groups)

        return related_project_groups

    def _get_parent_project_group(self, parent_project_group_id, domain_id, project_group_id=None):
        query_filter = [{
            'k': 'project_group_id',
            'v': parent_project_group_id,
            'o': 'eq'
        }, {
            'k': 'domain_id',
            'v': domain_id,
            'o': 'eq'
        }]

        if project_group_id:
            query_filter.append({
                'k': 'project_group_id',
                'v': project_group_id,
                'o': 'not'
            })

        parent_project_group_vos, total_count = self.project_group_mgr.list_project_groups({'filter': query_filter})

        if total_count == 0:
            ERROR_NOT_FOUND(key='parent_project_group_id', value=parent_project_group_id)

        return parent_project_group_vos[0]

    def _append_user_project_group_filter(self, query, user_project_groups, domain_id):
        query['filter'] = query.get('filter', [])
        if user_project_groups:
            all_user_project_groups = user_project_groups[:]
            for project_group_id in user_project_groups:
                if project_group_id is not None:
                    project_group_path = self._get_project_group_path(project_group_id, domain_id)
                    all_user_project_groups += project_group_path

            query['filter'].append({
                'k': 'user_project_groups',
                'v': list(set(all_user_project_groups)),
                'o': 'in'
            })

        return query

    @cache.cacheable(key='project-path:{domain_id}:None:{project_group_id}', expire=3600)
    def _get_project_group_path(self, project_group_id, domain_id):
        project_group_path = []
        try:
            project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
            project_group_path = [project_group_id]
            project_group_path += self._get_parent_project_group_path(project_group_vo.parent_project_group, [])
        except Exception as e:
            _LOGGER.debug(f'[_get_all_parent_project_groups] Project group could not be found. '
                          f'(project_group_id={project_group_id}, reason={e})')

        return project_group_path

    def _get_parent_project_group_path(self, project_group_vo, project_group_path):
        project_group_id = project_group_vo.project_group_id
        project_group_path.append(project_group_id)

        if project_group_vo.parent_project_group:
            project_group_path = self._get_parent_project_group_path(project_group_vo.parent_project_group, project_group_path)

        return project_group_path
