import logging
from spaceone.core.service import *
from spaceone.identity.error.error_project import *
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@event_handler
class ProjectService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')

    @transaction
    @check_required(['name', 'project_group_id', 'domain_id'])
    def create(self, params):
        """ Create project

        Args:
            params (dict): {
                'name': 'str',
                'template_data': 'dict',
                'tags': 'dict',
                'project_group_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_vo
        """

        params['created_by'] = self.transaction.get_meta('user_id')

        if 'project_group_id' in params:
            project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')
            params['project_group'] = project_group_mgr.get_project_group(params['project_group_id'],
                                                                          params['domain_id'])

        if 'template_data' in params:
            # TODO: Template service is NOT be implemented yet
            pass

        return self.project_mgr.create_project(params)

    @transaction
    @check_required(['project_id', 'domain_id'])
    def update(self, params):
        """ Update project

        Args:
            params (dict): {
                'project_id': 'str',
                'name': 'str',
                'template_data': 'dict',
                'tags': 'dict',
                'project_group_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_vo
        """

        domain_id = params['domain_id']

        project_vo = self.project_mgr.get_project(params['project_id'], domain_id)

        if 'project_group_id' in params:
            project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')
            params['project_group'] = project_group_mgr.get_project_group(params['project_group_id'], domain_id)

        if 'template_id' in params:
            # TODO: Template service is NOT be implemented yet
            pass

        return self.project_mgr.update_project_by_vo(params, project_vo)

    @transaction
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

        self._check_exist_resource(params)
        self.project_mgr.delete_project_by_vo(project_vo)

    @transaction
    @check_required(['project_id', 'user_id', 'domain_id'])
    def add_member(self, params):
        """ Add project member

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'roles': 'list',
                'labels': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_member_vo
        """

        domain_id = params['domain_id']
        project_id = params['project_id']
        user_id = params['user_id']

        project_vo = self.project_mgr.get_project(project_id, domain_id)

        user_vo = self._get_user(user_id, domain_id)

        self._check_not_exist_member(project_vo, user_vo)

        roles = self._get_roles(params.get('roles', []), domain_id)
        labels = list(set(params.get('labels', [])))

        self._check_role_type(user_vo.roles, roles)

        return self.project_mgr.add_member(project_vo, user_vo, roles, labels)

    @transaction
    @check_required(['project_id', 'user_id', 'domain_id'])
    def modify_member(self, params):
        """ Modify project member

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'roles': 'list',
                'labels': 'list',
                'domain_id': 'str'
            }

        Returns:
            project_member_vo
        """

        domain_id = params['domain_id']
        project_id = params['project_id']
        user_id = params['user_id']

        project_vo = self.project_mgr.get_project(project_id, domain_id)
        user_vo = self._get_user(user_id, domain_id)

        project_member_vo = self._get_project_member(project_vo, user_vo)

        roles = self._get_roles(params.get('roles', []), domain_id)
        labels = list(set(params.get('labels', [])))

        self._check_role_type(user_vo.roles, roles)

        self.project_mgr.remove_member(project_vo, project_member_vo)
        return self.project_mgr.add_member(project_vo, user_vo, roles, labels)

    @transaction
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
            project_member_vo
        """

        domain_id = params['domain_id']
        project_id = params['project_id']
        user_id = params['user_id']

        project_vo = self.project_mgr.get_project(project_id, domain_id)
        user_vo = self._get_user(user_id, domain_id)

        project_member_vo = self._get_project_member(project_vo, user_vo)
        self.project_mgr.remove_member(project_vo, project_member_vo)

    @transaction
    @check_required(['project_id', 'domain_id'])
    def get(self, params):
        """ Get project

        Args:
            params (dict): {
                'project_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            project_vo
        """

        return self.project_mgr.get_project(params['project_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['project_id', 'name', 'project_group_id', 'domain_id'])
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
            project_vos
        """

        return self.project_mgr.list_projects(params.get('query', {}))

    @transaction
    @check_required(['project_id', 'domain_id'])
    @append_query_filter(['user_id'])
    @append_keyword_filter(['user_id', 'user_name', 'email', 'mobile'])
    def list_members(self, params):
        """ List project members

        Args:
            params (dict): {
                'project_id': 'str',
                'user_id': 'str',
                'query': 'dict',
                'domain_id': 'str'
            }

        Returns:
            project_member_vos
        """

        query = params.get('query', {})

        project_vo = self.project_mgr.get_project(params['project_id'], params['domain_id'])

        if 'filter' not in query:
            query['filter'] = []

        query['filter'].append({
            'k': 'project',
            'v': project_vo,
            'o': 'eq'
        })

        return self.project_mgr.list_project_members(query)

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
        return self.project_mgr.stat_projects(query)

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

    def _check_exist_resource(self, params):
        # TODO: Check exist resource in project group
        pass

    def _get_user(self, user_id, domain_id):
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        return user_mgr.get_user(user_id, domain_id)

    def _check_not_exist_member(self, project_vo, user_vo):
        project_member_vos, total_count = self._list_project_members(project_vo, user_vo)

        if total_count > 0:
            raise ERROR_ALREADY_EXIST_USER_IN_PROJECT(user_id=user_vo.user_id,
                                                      project_id=project_vo.project_id)

    def _get_project_member(self, project_vo, user_vo):
        project_member_vos, total_count = self._list_project_members(project_vo, user_vo)

        if total_count == 0:
            raise ERROR_NOT_FOUND_USER_IN_PROJECT(user_id=user_vo.user_id,
                                                  project_id=project_vo.project_id)

        return project_member_vos[0]

    def _list_project_members(self, project_vo, user_vo):
        query = {
            'filter': [
                {'k': 'project', 'v': project_vo, 'o': 'eq'},
                {'k': 'user', 'v': user_vo, 'o': 'eq'}
            ]
        }

        return self.project_mgr.list_project_members(query)

    @staticmethod
    def _check_role_type(user_role_vos, project_role_vos):
        for role_vo in user_role_vos:
            if role_vo.role_type == 'SYSTEM':
                raise ERROR_SYSTEM_ROLE_USER()

        for role_vo in project_role_vos:
            if role_vo.role_type != 'PROJECT':
                raise ERROR_ONLY_PROJECT_ROLE_TYPE_ALLOWED()
