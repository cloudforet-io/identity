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

_LOGGER = logging.getLogger(__name__)


# @authentication_handler
# @authorization_handler
@event_handler
class AuthorizationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.auth_mgr: AuthorizationManager = self.locator.get_manager('AuthorizationManager')
        self.project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')
        self.project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')

    @transaction
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
                'project_group_id': 'str'
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

        self._check_user_state(user_id, domain_id)
        self._check_domain_state(domain_id)

        user_role_type, user_roles, user_projects, user_project_groups = \
            self._get_user_role_bindings(user_id, domain_id)

        for project_group_id in user_project_groups[:]:
            child_projects, child_project_groups = self._get_children_in_project_group(project_group_id, domain_id)
            user_projects += child_projects
            user_project_groups += child_project_groups

        user_projects = sorted(list(set(user_projects)))
        user_project_groups = sorted(list(set(user_project_groups)))
        user_roles = sorted(list(set(user_roles)))
        user_projects_str = ','.join(user_projects)
        user_project_groups_str = ','.join(user_project_groups)
        user_roles_str = ','.join(user_project_groups)

        user_permissions = self._get_permissions(user_roles, domain_id)

        self.auth_mgr.check_permissions(user_id, domain_id, user_permissions, service, resource, verb, user_roles_str)
        self.auth_mgr.check_scope_by_role_type(user_id, domain_id, scope, user_role_type, user_projects,
                                               user_project_groups, request_domain_id, request_project_id,
                                               request_project_group_id, user_projects_str, user_project_groups_str)

        return {
            'role_type': user_role_type,
            'projects': user_projects,
            'project_groups': user_project_groups
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

    @cache.cacheable(key='role-bindings:{domain_id}:{user_id}', expire=3600)
    def _get_user_role_bindings(self, user_id, domain_id):
        role_binding_mgr: RoleBindingManager = self.locator.get_manager('RoleBindingManager')

        role_binding_vos = role_binding_mgr.get_user_role_bindings(user_id, domain_id)

        role_type = None
        user_roles = {
            'SYSTEM': [],
            'DOMAIN': [],
            'PROJECT': []
        }
        user_projects = []
        user_project_groups = []
        for role_binding_vo in role_binding_vos:
            rb_role_type = role_binding_vo.role.role_type
            rb_role_id = role_binding_vo.role.role_id
            if role_type is None:
                role_type = rb_role_type
            else:
                if rb_role_type != 'PROJECT':
                    role_type = rb_role_type

            if rb_role_type == 'PROJECT':
                if role_binding_vo.project:
                    user_projects.append(role_binding_vo.project.project_id)
                if role_binding_vo.project_group:
                    user_project_groups.append(role_binding_vo.project_group.project_group_id)

            user_roles[rb_role_type].append(rb_role_id)

        if role_type:
            return role_type, user_roles[role_type], user_projects, user_project_groups
        else:
            _LOGGER.debug(f'[_get_user_role_bindings] User dose not have roles. (user_id={user_id}, domain_id={domain_id})')
            raise ERROR_PERMISSION_DENIED()

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

    def _get_permissions(self, roles, domain_id):
        permissions = []

        for role_id in roles:
            permissions += self._get_role_permissions(role_id, domain_id)

        return permissions

    @cache.cacheable(key='role-permissions:{domain_id}:{role_id}', expire=3600)
    def _get_role_permissions(self, role_id, domain_id):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        policy_mgr: PolicyManager = self.locator.get_manager('PolicyManager')
        role_vo = role_mgr.get_role(role_id, domain_id)
        role_permissions = []

        for role_policy in role_vo.policies:
            if role_policy.policy_type == 'MANAGED':
                policy_vo = policy_mgr.get_managed_policy(role_policy.policy.policy_id, domain_id)
                role_permissions += policy_vo.permissions

            elif role_policy.policy_type == 'CUSTOM':
                role_permissions += role_policy.policy.permissions

        return role_permissions
