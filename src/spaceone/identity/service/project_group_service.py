import logging
from spaceone.core.service import *
from spaceone.core import utils
from spaceone.identity.error.error_project import *
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.project_group_model import ProjectGroup
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
                'tags': 'dict',
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

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'authorization.project_group_id': 'parent_project_group_id'
    })
    @check_required(['project_group_id', 'domain_id'])
    def update(self, params):
        """ Update project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'parent_project_group_id': 'str',
                'release_parent_project_group': 'bool',
                'tags': 'dict',
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
    @append_keyword_filter(['project_group_id', 'name'])
    def list(self, params):
        """ List project groups

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'parent_project_group_id': 'str',
                'author_within': 'bool',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of project_group_vo'
            total_count (int)
        """
        role_type = self.transaction.get_meta('authorization.role_type')
        user_projects = self.transaction.get_meta('authorization.projects')
        user_project_groups = self.transaction.get_meta('authorization.project_groups')
        author_within = params.get('author_within', False)
        query = params.get('query', {})
        domain_id = params['domain_id']

        if 'only' in query and 'parent_project_group' in query['only']:
            query['only'].append('parent_project_group_id')

        # For Access Control
        if role_type == 'PROJECT':
            if author_within:
                query['filter'].append({
                    'k': 'user_project_groups',
                    'v': user_project_groups,
                    'o': 'in'
                })
            else:
                self._append_user_project_group_filter(query, user_projects, user_project_groups, domain_id)

        project_group_vos, total_count = self.project_group_mgr.list_project_groups(query)

        return project_group_vos, total_count, self._get_parent_project_groups_info(project_group_vos)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id', 'user_project_groups'])
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
                'is_external_user': 'bool',
                'role_id': 'str',
                'labels': 'list',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            role_binding_vo (object)
        """

        is_external_user = params.get('is_external_user', False)
        user_id = params['user_id']
        domain_id = params['domain_id']

        if is_external_user:
            self._create_external_user(user_id, domain_id)

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
    @append_query_filter(['user_id', 'role_id'])
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

        project_group_id = params['project_group_id']
        domain_id = params['domain_id']
        include_parent_member = params.get('include_parent_member', False)

        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

        query = params.get('query', {})
        query['filter'] = query.get('filter', [])

        if include_parent_member:
            project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
            parent_project_group_vos = self._get_parents(project_group_vo.parent_project_group, [])
            query['filter'].append({
                'k': 'project_group',
                'v': parent_project_group_vos + [project_group_vo],
                'o': 'in'
            })
            query['filter'].append({
                'k': 'role_type',
                'v': 'PROJECT',
                'o': 'eq'
            })
        else:
            query['filter'].append({
                'k': 'project_group_id',
                'v': project_group_id,
                'o': 'eq'
            })

        return role_binding_mgr.list_role_bindings(query)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['project_group_id', 'domain_id'])
    @change_only_key({'project_group_info': 'project_group'}, key_path='query.only')
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

        role_type = self.transaction.get_meta('authorization.role_type')
        user_projects = self.transaction.get_meta('authorization.projects')
        project_group_id = params['project_group_id']
        domain_id = params['domain_id']
        recursive = params.get('recursive', False)
        query = params.get('query', {})

        if 'only' in query and 'project_group' in query['only']:
            query['only'].append('project_group_id')

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

        if role_type == 'PROJECT':
            query['filter'].append({
                'k': 'user_projects',
                'v': user_projects,
                'o': 'in'
            })

        project_vos, total_count = project_mgr.list_projects(query)

        return project_vos, total_count, self._get_project_groups_info(project_vos)

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
            raise ERROR_NOT_FOUND(key='parent_project_group_id', value=parent_project_group_id)

        return parent_project_group_vos[0]

    def _append_user_project_group_filter(self, query, projects, project_groups, domain_id):
        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')
        query['filter'] = query.get('filter', [])
        if projects or project_groups:
            all_user_project_path = project_groups[:]
            for project_id in projects:
                if project_id is not None:
                    all_user_project_path += self.project_mgr.get_project_path(project_id, None, domain_id) or []

            for project_group_id in project_groups:
                if project_group_id is not None:
                    all_user_project_path += self.project_mgr.get_project_path(None, project_group_id, domain_id) or []

            query['filter'].append({
                'k': 'user_project_groups',
                'v': list(set(all_user_project_path)),
                'o': 'in'
            })

        return query

    def _get_parents(self, project_group_vo: ProjectGroup, parent_project_group_vos):
        parent_project_group_vos.append(project_group_vo)

        if project_group_vo.parent_project_group:
            return self._get_parents(project_group_vo.parent_project_group, parent_project_group_vos)
        else:
            return parent_project_group_vos

    def _create_external_user(self, user_id, domain_id):
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')

        user_vos = user_mgr.filter_users(user_id=user_id, domain_id=domain_id)

        if user_vos.count() == 0:
            domain_vo = domain_mgr.get_domain(domain_id)
            user_mgr.create_user({
                'user_id': user_id,
                'user_type': 'USER',
                'backend': 'EXTERNAL',
                'domain_id': domain_id
            }, domain_vo)

    def _get_project_groups_info(self, project_vos):
        project_groups_info = {}
        project_group_ids = []
        for project_vo in project_vos:
            if project_vo.project_group_id:
                project_group_ids.append(project_vo.project_group_id)

        pg_vos = self.project_group_mgr.filter_project_groups(project_group_id=project_group_ids)
        for pg_vo in pg_vos:
            project_groups_info[pg_vo.project_group_id] = pg_vo

        return project_groups_info

    def _get_parent_project_groups_info(self, project_group_vos):
        parent_project_groups_info = {}
        parent_project_group_ids = []
        for project_group_vo in project_group_vos:
            if project_group_vo.parent_project_group_id:
                parent_project_group_ids.append(project_group_vo.parent_project_group_id)

        if len(parent_project_group_ids) > 0:
            parent_pg_vos = self.project_group_mgr.filter_project_groups(project_group_id=parent_project_group_ids)
            for parent_pg_vo in parent_pg_vos:
                parent_project_groups_info[parent_pg_vo.project_group_id] = parent_pg_vo

        return parent_project_groups_info
