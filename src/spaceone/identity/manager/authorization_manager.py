import fnmatch
import functools
import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.core.error import *

_LOGGER = logging.getLogger(__name__)


class AuthorizationManager(BaseManager):

    def __init__(self, transaction):
        super().__init__(transaction)

    @cache.cacheable(key='user-permissions:{domain_id}:{user_id}:{service}:{resource}:{verb}:{request_roles}',
                     expire=3600)
    def check_permissions(self, user_id, domain_id, permissions, service, resource, verb, request_roles):
        try:
            next(filter(functools.partial(
                self._match_permission, service, resource, verb), permissions))
        except Exception as e:
            _LOGGER.debug(f'[verify] Not matched permissions. '
                          f'(user_id={user_id}, api={service}.{resource}.{verb})')
            raise ERROR_PERMISSION_DENIED()

    @cache.cacheable(key='user-scopes:{domain_id}:{user_id}:{scope}:{role_type}:{request_domain_id}:'
                         '{request_project_id}:{request_project_group_id}:{projects}:{project_groups}:'
                         '{request_user_id}:{require_project_id}:{require_project_group_id}', expire=3600)
    def check_scope_by_role_type(self, user_id, domain_id, scope, role_type, projects, project_groups,
                                 request_domain_id, request_project_id, request_project_group_id, request_user_id,
                                 require_project_id, require_project_group_id):

        if role_type == 'USER':
            self._check_domain_scope(user_id, domain_id, role_type, request_domain_id)
            self._check_user_scope(user_id, domain_id, request_user_id)
        else:
            if scope == 'SYSTEM':
                # Excluding system api checking process
                # self._check_system_scope(user_id, domain_id, role_type)
                pass
            elif scope == 'DOMAIN':
                self._check_domain_scope(user_id, domain_id, role_type, request_domain_id)
            elif scope == 'PROJECT':
                self._check_domain_scope(user_id, domain_id, role_type, request_domain_id)
                self._check_project_scope(user_id, domain_id, role_type, projects, project_groups,
                                          request_project_id, request_project_group_id,
                                          require_project_id, require_project_group_id)

    @staticmethod
    def _check_user_scope(user_id, domain_id, request_user_id):
        if user_id != request_user_id:
            _LOGGER.debug(f'[_check_user_scope] user role_type can only access self resource.'
                          f' (user_id = {user_id}, user_domain_id = {domain_id},'
                          f' request_user_id = {request_user_id})')
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _check_system_scope(user_id, domain_id, role_type):
        if role_type != 'SYSTEM':
            _LOGGER.debug(f'[_check_system_scope] system api is not allowed.'
                          f' (user_id = {user_id}, user_domain_id = {domain_id})')
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _check_domain_scope(user_id, domain_id, role_type, request_domain_id):
        if role_type in ['DOMAIN', 'PROJECT']:
            if request_domain_id and request_domain_id != domain_id:
                _LOGGER.debug(f'[_check_domain_scope] domain_id is not allowed.'
                              f' (user_id = {user_id}, user_domain_id = {domain_id},'
                              f' request_domain_id = {request_domain_id})')
                raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _check_project_scope(user_id, domain_id, role_type, projects, project_groups,
                             request_project_id, request_project_group_id,
                             require_project_id, require_project_group_id):
        if role_type == 'PROJECT':
            if require_project_id and request_project_id is None:
                _LOGGER.debug(f'[_check_project_scope] project_id is required.'
                              f' (user_id = {user_id}, user_domain_id = {domain_id},'
                              f' request_project_id = {request_project_id})')
                raise ERROR_PERMISSION_DENIED()

            if require_project_group_id and request_project_group_id is None:
                _LOGGER.debug(f'[_check_project_scope] project_group_id is required.'
                              f' (user_id = {user_id}, user_domain_id = {domain_id},'
                              f' request_project_group_id = {request_project_group_id})')
                raise ERROR_PERMISSION_DENIED()

            if request_project_id and request_project_id not in projects:
                _LOGGER.debug(f'[_check_project_scope] project_id is not allowed.'
                              f' (user_id = {user_id}, user_domain_id = {domain_id},'
                              f' request_project_id = {request_project_id})')
                raise ERROR_PERMISSION_DENIED()

            if request_project_group_id and request_project_group_id not in project_groups:
                _LOGGER.debug(f'[_check_project_scope] project_group_id is not allowed.'
                              f' (user_id = {user_id}, user_domain_id = {domain_id},'
                              f' request_project_group_id = {request_project_group_id})')
                raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _match_permission(service, api_class, method, permission):
        if fnmatch.fnmatch(f'{service}.{api_class}.{method}', permission):
            return True
        else:
            return False
