import logging

from spaceone.core import cache
from spaceone.core.service import *
from spaceone.core.error import *
from spaceone.identity.manager.authorization_manager import AuthorizationManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.role_manager import RoleManager

_LOGGER = logging.getLogger(__name__)

@authentication_handler
@event_handler
class AuthorizationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.auth_mgr: AuthorizationManager = self.locator.get_manager('AuthorizationManager')

    @transaction
    @check_required(['service', 'api_class', 'method', 'parameter'])
    def verify(self, params):
        user_id = self.transaction.get_meta('user_id')
        domain_id = self.transaction.get_meta('domain_id')
        service = params['service']
        api_class = params['api_class']
        method = params['method']
        parameter = params['parameter']

        role_type, user_roles = self._get_user_roles(user_id, domain_id)

        if 'project_id' in parameter:
            # TODO : Get User Project's Roles (Cache)
            pass

        user_permissions = self._get_permissions(user_roles, domain_id)

        self.auth_mgr.check_permissions(user_permissions, service, api_class, method, user_id)

        # TODO : Get User All Projects (Cached)
        projects = []

        changed_parameter = self.auth_mgr.change_parameter(role_type, parameter, user_id, domain_id, projects)

        return {
            'role_type': role_type,
            'changed_parameter': changed_parameter
        }

    @cache.cacheable(key='user-roles:{domain_id}:{user_id}', expire=86400)
    def _get_user_roles(self, user_id, domain_id):
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        user_vo = user_mgr.get_user(user_id, domain_id)

        role_type = None

        if user_vo.state == 'DISABLED':
            _LOGGER.debug(f'[_get_user_roles] User has been disabled. (user_id={user_id})')
            raise ERROR_PERMISSION_DENIED()

        user_roles = []
        for role in user_vo.roles:
            role_type = role.role_type
            user_roles.append(role.role_id)

        return role_type, user_roles

    def _get_permissions(self, roles, domain_id):
        permissions = []

        for role_id in roles:
            permissions += self._get_role_permissions(role_id, domain_id)

        return permissions

    @cache.cacheable(key='role:{domain_id}:{role_id}', expire=86400)
    def _get_role_permissions(self, role_id, domain_id):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        role_vo = role_mgr.get_role(role_id, domain_id)
        role_permissions = []

        for role_policy in role_vo.policies:
            if role_policy.policy_type == 'CUSTOM':
                role_permissions += role_policy.policy.permissions

            elif role_policy.policy_type == 'MANAGED':
                role_policy += self._get_managed_policy_permissions(role_policy.url)

        return role_permissions

    # TODO: Managed Policy Cache
    def _get_managed_policy_permissions(self, policy_url):
        return []