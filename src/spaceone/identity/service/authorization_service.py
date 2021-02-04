import logging

from spaceone.core import cache
from spaceone.core.service import *
from spaceone.core.error import *
from spaceone.identity.manager.authorization_manager import AuthorizationManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.project_group_manager import ProjectGroupManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.policy_manager import PolicyManager
from spaceone.identity.conf.permissions_conf import DEFAULT_PERMISSIONS

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@event_handler
class AuthorizationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.auth_mgr: AuthorizationManager = self.locator.get_manager('AuthorizationManager')
        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')
        self.project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')

    @transaction(append_meta={'authorization.scope': 'SYSTEM'})
    @check_required(['service', 'resource', 'verb', 'scope'])
    def verify(self, params):
        """ Verify authority

        Args:
            params (dict): {
                'service': 'str',
                'resource': 'str',
                'verb': 'str',
                'scope': 'str',
                'domain_id': 'str',
                'project_id': 'str',
                'project_group_id': 'str',
                'user_id': 'str',
                'require_project_id': 'bool',
                'require_project_group_id': 'bool'
            }

        Returns:
            domain_owner_vo (object)
        """
        user_id = self.transaction.get_meta('user_id')
        domain_id = self.transaction.get_meta('domain_id')
        service = params['service']
        resource = params['resource']
        verb = params['verb']
        scope = params['scope']
        request_domain_id = params.get('domain_id')
        request_project_id = params.get('project_id')
        request_project_group_id = params.get('project_group_id')
        request_user_id = params.get('user_id')
        require_project_id = params.get('require_project_id', False)
        require_project_group_id = params.get('require_project_group_id', False)

        self._check_user_state(user_id, domain_id)
        self._check_domain_state(domain_id)

        project_path = self._get_project_path(request_project_id, request_project_group_id, domain_id)
        role_type, request_roles, projects, project_groups = \
            self._get_user_roles_and_projects_from_role_bindings(user_id, domain_id, scope, project_path)

        projects, project_groups = self._get_all_projects_and_project_groups(projects, project_groups, domain_id)

        user_permissions = self._get_permissions(role_type, request_roles, domain_id)

        self.auth_mgr.check_permissions(user_id, domain_id, user_permissions, service, resource, verb, request_roles)
        self.auth_mgr.check_scope_by_role_type(user_id, domain_id, scope, role_type, projects, project_groups,
                                               request_domain_id, request_project_id, request_project_group_id,
                                               request_user_id, require_project_id, require_project_group_id)

        return {
            'role_type': role_type,
            'projects': projects,
            'project_groups': project_groups
        }

    @cache.cacheable(key='user-state:{domain_id}:{user_id}', expire=3600)
    def _check_user_state(self, user_id, domain_id):
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        try:
            user_vo = user_mgr.get_user(user_id, domain_id)
        except Exception as e:
            _LOGGER.error(f'[_check_user_state] Get User Error: {e}')
            raise ERROR_PERMISSION_DENIED()

        if user_vo.state == 'DISABLED':
            _LOGGER.error(f'[_check_user_state] User has been disabled. (user_id={user_id}, domain_id={domain_id})')
            raise ERROR_PERMISSION_DENIED()

    @cache.cacheable(key='domain-state:{domain_id}', expire=3600)
    def _check_domain_state(self, domain_id):
        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        try:
            domain_vo = domain_mgr.get_domain(domain_id)
        except Exception as e:
            _LOGGER.error(f'[_check_user_state] Get Domain Error: {e}')
            raise ERROR_PERMISSION_DENIED()

        if domain_vo.state == 'DISABLED':
            _LOGGER.error(f'[_check_domain_state] Domain has been disabled. (domain_id={domain_id})')
            raise ERROR_PERMISSION_DENIED()

    @cache.cacheable(key='project-path:{domain_id}:{request_project_id}:{request_project_group_id}', expire=3600)
    def _get_project_path(self, request_project_id, request_project_group_id, domain_id):
        project_path = []
        if request_project_id:
            try:
                project_vo = self.project_mgr.get_project(request_project_id, domain_id)
                project_path = [request_project_id]
                project_path += self._get_parent_project_path(project_vo.project_group, [])
            except Exception:
                _LOGGER.debug(f'[_get_project_path] Project could not be found. (project_id={request_project_id})')

        elif request_project_group_id:
            try:
                project_group_vo = self.project_group_mgr.get_project_group(request_project_group_id, domain_id)
                project_path = [request_project_group_id]
                project_path += self._get_parent_project_path(project_group_vo.parent_project_group, [])
            except Exception:
                _LOGGER.debug(f'[_get_project_path] Project group could not be found. (project_group_id={request_project_group_id})')

        return project_path

    def _get_parent_project_path(self, project_group_vo, project_path):
        project_group_id = project_group_vo.project_group_id
        project_path.append(project_group_id)

        if project_group_vo.parent_project_group:
            project_path = self._get_parent_project_path(project_group_vo.parent_project_group, project_path)

        return project_path

    @cache.cacheable(key='role-bindings:{domain_id}:{user_id}:{scope}:{project_path}', expire=3600)
    def _get_user_roles_and_projects_from_role_bindings(self, user_id, domain_id, scope, project_path):
        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

        role_binding_vos = role_binding_mgr.get_user_role_bindings(user_id, domain_id)

        role_type = None
        user_roles = {
            'SYSTEM': [],
            'DOMAIN': [],
            'PROJECT': {}
        }
        projects = []
        project_groups = []
        for role_binding_vo in role_binding_vos:
            rb_role_type = role_binding_vo.role.role_type
            rb_role_id = role_binding_vo.role_id
            if role_type is None:
                role_type = rb_role_type
            else:
                if rb_role_type != 'PROJECT':
                    role_type = rb_role_type

            if rb_role_type == 'PROJECT':
                if role_binding_vo.project_id:
                    project_id = role_binding_vo.project_id
                    projects.append(project_id)
                    user_roles[rb_role_type][project_id] = [rb_role_id]
                elif role_binding_vo.project_group_id:
                    project_group_id = role_binding_vo.project_group_id
                    project_groups.append(project_group_id)
                    user_roles[rb_role_type][project_group_id] = [rb_role_id]
            else:
                user_roles[rb_role_type].append(rb_role_id)

        request_roles = self._get_request_roles_by_scope(role_type, user_roles, scope, project_path)

        return role_type or 'USER', list(set(request_roles)), list(set(projects)), list(set(project_groups))

    def _get_request_roles_by_scope(self, user_role_type, user_roles, scope, project_path):
        if user_role_type == 'SYSTEM':
            return user_roles['SYSTEM']
        elif user_role_type == 'DOMAIN':
            if scope == 'PROJECT':
                for project_or_project_group_id in project_path:
                    if project_or_project_group_id in user_roles['PROJECT']:
                        return user_roles['PROJECT'][project_or_project_group_id]

            return user_roles['DOMAIN']

        elif user_role_type == 'PROJECT':
            if scope == 'PROJECT':
                if len(project_path) > 0:
                    for project_or_project_group_id in project_path:
                        if project_or_project_group_id in user_roles['PROJECT']:
                            return user_roles['PROJECT'][project_or_project_group_id]

                    raise ERROR_PERMISSION_DENIED()

            project_roles = []
            for project_or_project_group_id, roles in user_roles['PROJECT'].items():
                project_roles += roles

            return project_roles
        else:
            return []

    def _get_all_projects_and_project_groups(self, projects, project_groups, domain_id):
        for project_group_id in project_groups[:]:
            child_projects, child_project_groups = self._get_children_in_project_group(project_group_id, domain_id)
            projects += child_projects
            project_groups += child_project_groups

        return projects, project_groups

    @cache.cacheable(key='project-group-children:{domain_id}:{project_group_id}', expire=3600)
    def _get_children_in_project_group(self, project_group_id, domain_id):
        project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
        related_project_groups = self._get_related_project_group(project_group_vo, [project_group_vo])

        project_vos, total_count = self.project_mgr.list_projects({
            'filter': [{'k': 'project_group', 'v': related_project_groups, 'o': 'in'}]
        })
        project_group_vos, total_count = self.project_group_mgr.list_project_groups({
            'filter': [{'k': 'parent_project_group', 'v': related_project_groups, 'o': 'in'}]
        })

        projects = [project_vo.project_id for project_vo in project_vos]
        project_groups = [project_group_vo.project_group_id for project_group_vo in project_group_vos]

        return projects, project_groups

    def _get_related_project_group(self, project_group_vo, related_project_groups):
        project_group_vos = self.project_group_mgr.filter_project_groups(parent_project_group=project_group_vo)

        if project_group_vos.count() > 0:
            related_project_groups += project_group_vos
            for pg_vo in project_group_vos:
                related_project_groups = self._get_related_project_group(pg_vo, related_project_groups)

        return related_project_groups

    @cache.cacheable(key='role-permissions:{domain_id}:{role_id}', expire=3600)
    def _get_role_permissions(self, role_id, domain_id):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')
        role_vo = role_mgr.get_role(role_id, domain_id)
        permissions = []

        for role_policy in role_vo.policies:
            if role_policy.policy_type == 'MANAGED':
                policy_vo = policy_mgr.get_managed_policy(role_policy.policy.policy_id, domain_id)
                permissions += policy_vo.permissions

            elif role_policy.policy_type == 'CUSTOM':
                permissions += role_policy.policy.permissions

        return permissions

    def _get_permissions(self, user_role_type, roles, domain_id):
        if user_role_type == 'USER':
            return DEFAULT_PERMISSIONS
        else:
            permissions = []

            for role_id in roles:
                permissions += self._get_role_permissions(role_id, domain_id)

            return permissions
