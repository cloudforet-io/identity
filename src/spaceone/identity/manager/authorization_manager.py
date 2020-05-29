import fnmatch
import functools
import logging

from spaceone.core.manager import BaseManager
from spaceone.core.error import *


_LOGGER = logging.getLogger(__name__)


class AuthorizationManager(BaseManager):

    def __init__(self, transaction):
        super().__init__(transaction)

    def change_parameter(self, role_type, parameter, user_id, domain_id, projects):
        # if role_type == 'DOMAIN':
        if role_type in ['DOMAIN', 'PROJECT']:
            domain_id_param = parameter.get('domain_id')
            if domain_id_param is None:
                parameter['domain_id'] = domain_id
            else:
                self._check_domain_id(domain_id_param, user_id, domain_id)

        # elif role_type == 'PROJECT':
        #     project_id_param = parameter.get('project_id')
        #     if project_id_param is None:
        #         parameter['project_id'] = projects
        #     else:
        #         self._check_project_id(project_id_param, user_id, projects)

        return parameter

    def check_permissions(self, permissions, service, api_class, method, user_id):
        try:
            next(filter(functools.partial(
                self._match_permission, service, api_class, method), permissions))
        except:
            _LOGGER.debug(f'[verify] Not matched permissions. '
                          f'(user_id={user_id}, api={service}.{api_class}.{method})')
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _check_domain_id(domain_id_param, user_id, domain_id):
        if domain_id_param != domain_id:
            _LOGGER.debug(f'[_check_domain_id] domain_id is not allowed.'
                          f' (user_id={user_id}, domain_id={domain_id_param})')
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _check_project_id(project_id_param, user_id, projects):
        if project_id_param not in projects:
            _LOGGER.debug(f'[_check_project_id] project_id is not allowed.'
                          f' (user_id={user_id}, project_id={project_id_param})')
            raise ERROR_PERMISSION_DENIED()

    @staticmethod
    def _match_permission(service, api_class, method, permission):
        if fnmatch.fnmatch(f'{service}.{api_class}.{method}', permission):
            return True
        else:
            return False