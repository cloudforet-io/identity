import logging
from spaceone.core.service import *
from spaceone.identity.error.error_project import *
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.error.custom import *
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@event_handler
class ProjectGroupService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')

    @transaction
    @check_required(['name', 'domain_id'])
    def create(self, params):
        """ Create project group

        Args:
            params (dict): {
                'name': 'str',
                'template_id': 'str',
                'tags': 'dict',
                'parent_project_group_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_group_vo
        """

        params['created_by'] = self.transaction.get_meta('user_id')

        if 'parent_project_group_id' in params:
            params['parent_project_group'] = self._get_parent_project_group(params['parent_project_group_id'],
                                                                            params['domain_id'])
        else:
            params['parent_project_group'] = None

        if 'template_id' in params:
            # TODO: Template service is NOT be implemented yet
            pass

        return self.project_group_mgr.create_project_group(params)

    @transaction
    @check_required(['project_group_id', 'domain_id'])
    def update(self, params):
        """ Update project group

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'template_id': 'str',
                'tags': 'dict',
                'release_parent_project_group': 'bool',
                'parent_project_group_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_vo
        """

        domain_id = params['domain_id']
        release_parent_project_group = params.get('release_parent_project_group', False)

        project_group_vo = self.project_group_mgr.get_project_group(params['project_group_id'], domain_id)

        if release_parent_project_group:
            params['parent_project_group'] = None
        else:
            if 'parent_project_group_id' in params:
                params['parent_project_group'] = self._get_parent_project_group(
                    params['parent_project_group_id'], params['domain_id'], params['project_group_id'])

        if 'template_id' in params:
            # TODO: Template service is NOT be implemented yet
            pass

        return self.project_group_mgr.update_project_group_by_vo(params, project_group_vo)

    @transaction
    @check_required(['project_group_id', 'domain_id'])
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

        project_group_id = params['project_group_id']
        domain_id = params['domain_id']
        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)

        self.project_group_mgr.delete_project_group_by_vo(project_group_vo)

    @transaction
    @check_required(['project_group_id', 'domain_id', 'user_id'])
    def add_member(self, params):
        """ Add project group member

        Args:
            params (dict): {
                'project_group_id': 'str',
                'user_id': 'str',
                'roles': 'list',
                'labels': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_group_member_vo
        """

        domain_id = params['domain_id']
        project_group_id = params['project_group_id']

        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)

        user_vo = self._get_user(params['user_id'], domain_id)

        self._check_not_exist_member(project_group_vo, user_vo)

        roles = self._get_roles(params.get('roles', []), domain_id)
        labels = list(set(params.get('labels', [])))

        self._check_role_type(user_vo.roles, roles)

        return self.project_group_mgr.add_member(project_group_vo, user_vo, roles, labels)

    @transaction
    @check_required(['project_group_id', 'user_id', 'domain_id'])
    def modify_member(self, params):
        """ Modify project member

        Args:
            params (dict): {
                'project_group_id': 'str',
                'user_id': 'str',
                'roles': 'list',
                'labels': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_group_member_vo
        """

        domain_id = params['domain_id']
        project_group_id = params['project_group_id']

        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
        user_vo = self._get_user(params['user_id'], domain_id)

        project_group_member_vo = self._get_project_group_member(project_group_vo, user_vo)

        roles = self._get_roles(params.get('roles', []), domain_id)
        labels = list(set(params.get('labels', [])))

        self._check_role_type(user_vo.roles, roles)

        self.project_group_mgr.remove_member(project_group_vo, project_group_member_vo)
        return self.project_group_mgr.add_member(project_group_vo, user_vo, roles, labels)

    @transaction
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
            project_group_member_vo
        """

        domain_id = params['domain_id']
        project_group_id = params['project_group_id']

        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
        user_vo = self._get_user(params['user_id'], domain_id)

        project_group_member_vo = self._get_project_group_member(project_group_vo, user_vo)
        self.project_group_mgr.remove_member(project_group_vo, project_group_member_vo)

    @transaction
    @check_required(['project_group_id', 'domain_id'])
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

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['project_group_id', 'name', 'parent_project_group_id', 'template_id', 'domain_id'])
    @append_keyword_filter(['project_group_id', 'name'])
    def list(self, params):
        """ List projects

        Args:
            params (dict): {
                'project_group_id': 'str',
                'name': 'str',
                'parent_project_group_id': 'str',
                'template_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            project_group_vos
        """

        return self.project_group_mgr.list_project_groups(params.get('query', {}))

    @transaction
    @check_required(['project_group_id', 'domain_id'])
    @append_query_filter(['user_id'])
    @append_keyword_filter(['user_id', 'user_name', 'email', 'mobile'])
    def list_members(self, params):
        query = params.get('query', {})

        project_group_vo = self.project_group_mgr.get_project_group(params['project_group_id'], params['domain_id'])

        if 'filter' not in query:
            query['filter'] = []

        query['filter'].append({
            'k': 'project_group',
            'v': project_group_vo,
            'o': 'eq'
        })

        return self.project_group_mgr.list_project_group_members(query)

    @transaction
    @check_required(['project_group_id', 'domain_id'])
    @append_keyword_filter(['project_id', 'name'])
    def list_projects(self, params):
        project_group_id = params['project_group_id']
        domain_id = params['domain_id']
        recursive = params.get('recursive', False)
        query = params.get('query', {})

        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')

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

        return self.project_mgr.list_projects(query)

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
        return self.project_group_mgr.stat_project_groups(query)

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

    def _get_roles(self, role_ids, domain_id):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        role_vos, total_count = role_mgr.list_roles({
            'filter': [{
                'k': 'role_id',
                'v': role_ids,
                'o': 'in'
            }, {
                'k': 'domain_id',
                'v': domain_id,
                'o': 'eq'
            }]
        })

        if len(role_ids) != total_count:
            raise ERROR_NOT_FOUND(key='roles', value=str(role_ids))

        return role_vos

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

    def _get_user(self, user_id, domain_id):
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        return user_mgr.get_user(user_id, domain_id)

    def _check_not_exist_member(self, project_group_vo, user_vo):
        project_group_member_vos, total_count = self._list_project_group_members(project_group_vo, user_vo)

        if total_count > 0:
            raise ERROR_ALREADY_EXIST_USER_IN_PROJECT_GROUP(user_id=user_vo.user_id,
                                                            project_group_id=project_group_vo.project_id)

    def _get_project_group_member(self, project_group_vo, user_vo):
        project_group_member_vos, total_count = self._list_project_group_members(project_group_vo, user_vo)

        if total_count == 0:
            raise ERROR_NOT_FOUND_USER_IN_PROJECT_GROUP(user_id=user_vo.user_id,
                                                        project_group_id=project_group_vo.project_id)

        return project_group_member_vos[0]

    def _list_project_group_members(self, project_group_vo, user_vo):
        query = {
            'filter': [
                {'k': 'project_group', 'v': project_group_vo, 'o': 'eq'},
                {'k': 'user', 'v': user_vo, 'o': 'eq'}
            ]
        }

        return self.project_group_mgr.list_project_group_members(query)

    @staticmethod
    def _check_role_type(user_role_vos, project_group_role_vos):
        for role_vo in user_role_vos:
            if role_vo.role_type == 'SYSTEM':
                raise ERROR_SYSTEM_ROLE_USER()

        for role_vo in project_group_role_vos:
            if role_vo.role_type != 'PROJECT':
                raise ERROR_ONLY_PROJECT_ROLE_TYPE_ALLOWED()
