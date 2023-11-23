import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.role_binding.request import *
from spaceone.identity.model.role_binding.response import *

_LOGGER = logging.getLogger(__name__)


class RoleBindingService(BaseService):
    @transaction
    @convert_model
    def create(self, params: RoleBindingCreateRequest) -> Union[RoleBindingResponse, dict]:
        """ create role binding

         Args:
            params (RoleBindingCreateRequest): {
                'user_id': 'str',                   # required
                'role_id': 'str',                   # required
                'scope': 'str',                     # required
                'workspace_id': 'str',
                'domain_id': 'str'                  # required
            }

        Returns:
            RoleBindingResponse:
        """
        return {}

    @transaction
    @convert_model
    def update_role(self, params: RoleBindingUpdateRoleRequest) -> Union[RoleBindingResponse, dict]:
        """ update role of role binding

         Args:
            params (RoleBindingUpdateRoleRequest): {
                'role_binding_id': 'str',           # required
                'role_id': 'str',                   # required
                'workspace_id': 'str',
                'domain_id': 'str',                 # required
            }

        Returns:
            RoleBindingResponse:
        """
        return {}

    @transaction
    @convert_model
    def delete(self, params: RoleBindingDeleteRequest) -> None:
        """ delete role binding

         Args:
            params (RoleBindingDeleteRequest): {
                'role_binding_id': 'str',       # required
                'workspace_id': 'str',
                'domain_id': 'str',             # required
            }

        Returns:
            None
        """
        pass

    @transaction
    @convert_model
    def get(self, params: RoleBindingGetRequest) -> Union[RoleBindingResponse, dict]:
        """ get role binding

         Args:
            params (RoleBindingGetRequest): {
                'role_binding_id': 'str',       # required
                'workspace_id': 'str',
                'domain_id': 'str',             # required
            }

        Returns:
             RoleBindingResponse:
        """
        return {}

    @transaction
    @convert_model
    def list(self, params: RoleBindingSearchQueryRequest) -> Union[RoleBindingsResponse, dict]:
        """ list role bindings

        Args:
            params (RoleBindingSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_binding_id': 'str',
                'scope': 'str',
                'user_id': 'str',
                'role_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',                     # required
            }

        Returns:
            RoleBindingsResponse:
        """
        return {}

    @transaction
    @convert_model
    def stat(self, params: RoleBindingStatQueryRequest) -> dict:
        """ stat role bindings

        Args:
            params (RoleBindingStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        return {}
