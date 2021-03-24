import logging
from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.error.error_role import *
from spaceone.identity.model.role_binding_model import *
from spaceone.identity.manager import RoleManager, ProjectManager, ProjectGroupManager, UserManager

_LOGGER = logging.getLogger(__name__)
_SUPPORTED_RESOURCE_TYPES = ['identity.User']


class RoleBindingManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_binding_model: RoleBinding = self.locator.get_model('RoleBinding')

    def create_role_binding(self, params):
        def _rollback(role_binding_vo):
            _LOGGER.info(f'[create_role_binding._rollback] Delete role binding : {role_binding_vo.name} ({role_binding_vo.role_binding_id})')
            role_binding_vo.delete()

        resource_type = params['resource_type']
        resource_id = params['resource_id']
        role_id = params['role_id']
        project_id = params.get('project_id')
        project_group_id = params.get('project_group_id')
        domain_id = params['domain_id']

        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')
        project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')
        user_mgr: UserManager = self.locator.get_manager('UserManager')

        self._check_resource_type(resource_type)
        if resource_type == 'identity.User':
            params['user'] = user_mgr.get_user(resource_id, domain_id)

        role_vo = role_mgr.get_role(role_id, domain_id)
        self._check_role_type(role_vo.role_type, resource_type, resource_id, domain_id)
        params['role'] = role_vo

        if role_vo.role_type == 'PROJECT':
            if project_id:
                project_vo = project_mgr.get_project(project_id, domain_id)
                self._check_duplicate_project_role(resource_type, resource_id, project_vo, project_id)
                params['project'] = project_vo

            elif project_group_id:
                project_group_vo = project_group_mgr.get_project_group(project_group_id, domain_id)
                self._check_duplicate_project_group_role(resource_type, resource_id, project_group_vo, project_group_id)
                params['project_group'] = project_group_vo
            else:
                raise ERROR_REQUIRED_PROJECT_OR_PROJECT_GROUP()
        else:
            self._check_duplicate_domain_or_system_role(resource_type, resource_id, role_vo, role_id)
            if project_id:
                raise ERROR_NOT_ALLOWED_PROJECT_ID()
            elif project_group_id:
                raise ERROR_NOT_ALLOWED_PROJECT_GROUP_ID()

        role_binding_vo = self.role_binding_model.create(params)
        self.transaction.add_rollback(_rollback, role_binding_vo)

        cache.delete_pattern(f'role-bindings:{domain_id}:{resource_id}*')
        cache.delete_pattern(f'user-permissions:{domain_id}:{resource_id}*')
        cache.delete_pattern(f'user-scopes:{domain_id}:{resource_id}*')

        return role_binding_vo

    def update_role_binding(self, params):
        role_binding_vo = self.get_role_binding(params['role_binding_id'], params['domain_id'])
        return self.update_role_binding_by_vo(params, role_binding_vo)

    def update_role_binding_by_vo(self, params, role_binding_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_role_binding._rollback] Revert Data : {old_data["role_binding_id"]}')
            role_binding_vo.update(old_data)

        self.transaction.add_rollback(_rollback, role_binding_vo.to_dict())

        return role_binding_vo.update(params)

    def delete_role_binding(self, role_binding_id, domain_id):
        role_binding_vo = self.get_role_binding(role_binding_id, domain_id)
        self.delete_role_binding_by_vo(role_binding_vo)

    def delete_role_binding_by_vo(self, role_binding_vo):
        resource_id = role_binding_vo.resource_id
        domain_id = role_binding_vo.domain_id

        role_binding_vo.delete()

        cache.delete_pattern(f'role-bindings:{domain_id}:{resource_id}*')
        cache.delete_pattern(f'user-permissions:{domain_id}:{resource_id}*')
        cache.delete_pattern(f'user-scopes:{domain_id}:{resource_id}*')

    def get_role_binding(self, role_binding_id, domain_id, only=None):
        return self.role_binding_model.get(role_binding_id=role_binding_id, domain_id=domain_id, only=only)

    def get_project_role_binding(self, resource_type, resource_id, domain_id, project_vo=None, project_group_vo=None):
        return self.role_binding_model.filter(resource_type=resource_type, resource_id=resource_id, domain_id=domain_id,
                                              project=project_vo, project_group=project_group_vo)

    def get_user_role_bindings(self, user_id, domain_id):
        return self.role_binding_model.filter(resource_type='identity.User', resource_id=user_id, domain_id=domain_id)

    def list_role_bindings(self, query):
        return self.role_binding_model.query(**query)

    def stat_role_bindings(self, query):
        return self.role_binding_model.stat(**query)

    @staticmethod
    def _check_resource_type(resource_type):
        if resource_type not in _SUPPORTED_RESOURCE_TYPES:
            raise ERROR_INVALID_PARAMETER(
                key='resource_type', reason=f'resource_type is not supported. (support = {_SUPPORTED_RESOURCE_TYPES})')

    def _check_role_type(self, role_type, resource_type, resource_id, domain_id):
        role_binding_vos = self.role_binding_model.filter(resource_type=resource_type,
                                                          resource_id=resource_id, domain_id=domain_id)
        for role_binding_vo in role_binding_vos:
            if role_type == 'SYSTEM':
                if role_binding_vo.role.role_type in ['PROJECT', 'DOMAIN']:
                    raise ERROR_NOT_ALLOWED_ROLE_TYPE()
            else:
                if role_binding_vo.role.role_type == 'SYSTEM':
                    raise ERROR_NOT_ALLOWED_ROLE_TYPE()

    def _check_duplicate_domain_or_system_role(self, resource_type, resource_id, role_vo, role_id):
        rb_vos = self.role_binding_model.filter(resource_type=resource_type, resource_id=resource_id, role=role_vo)

        if rb_vos.count() > 0:
            raise ERROR_DUPLICATE_ROLE_BOUND(role_id=role_id, resource_id=resource_id)

    def _check_duplicate_project_role(self, resource_type, resource_id, project_vo, project_id):
        project_rb_vos = self.role_binding_model.filter(resource_type=resource_type, resource_id=resource_id,
                                                        project=project_vo)

        if project_rb_vos.count() > 0:
            raise ERROR_DUPLICATE_RESOURCE_IN_PROJECT(project_id=project_id, resource_id=resource_id)

    def _check_duplicate_project_group_role(self, resource_type, resource_id, project_group_vo, project_group_id):
        pg_rb_vos = self.role_binding_model.filter(resource_type=resource_type, resource_id=resource_id,
                                                   project_group=project_group_vo)

        if pg_rb_vos.count() > 0:
            raise ERROR_DUPLICATE_RESOURCE_IN_PROJECT_GROUP(project_group_id=project_group_id,
                                                            resource_id=resource_id)
