import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.role.request import *
from spaceone.identity.model.role.response import *

_LOGGER = logging.getLogger(__name__)


class RoleService(BaseService):
    @transaction
    @convert_model
    def create(self, params: RoleCreateRequest) -> Union[RoleResponse, dict]:
        """ create role

         Args:
            params (RoleCreateRequest): {
                'name': 'str',                          # required
                'role_type': 'list',                    # required
                'policies': 'list',                     # required
                'page_permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'                      # required
            }

        Returns:
            RoleResponse:
        """
        return {}

    @transaction
    @convert_model
    def update(self, params: RoleUpdateRequest) -> Union[RoleResponse, dict]:
        """ update role

         Args:
            params (RoleUpdateRequest): {
                'role_id': 'str',                       # required
                'name': 'str',
                'policies': 'list',
                'page_permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'                      # required
            }

        Returns:
            RoleResponse:
        """
        return {}

    @transaction
    @convert_model
    def delete(self, params: RoleDeleteRequest) -> None:
        """ delete role

         Args:
            params (RoleDeleteRequest): {
                'role_id': 'str',               # required
                'domain_id': 'str',             # required
            }

        Returns:
            None
        """
        pass

    @transaction
    @convert_model
    def get(self, params: RoleGetRequest) -> Union[RoleResponse, dict]:
        """ get role

         Args:
            params (RoleGetRequest): {
                'role_id': 'str',               # required
                'domain_id': 'str',             # required
            }

        Returns:
             RoleResponse:
        """
        return {}

    @transaction
    @convert_model
    def list(self, params: RoleSearchQueryRequest) -> Union[RolesResponse, dict]:
        """ list roles

        Args:
            params (RoleSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_id': 'str',
                'role_type': 'str',
                'policy_id': 'str',
                'domain_id': 'str',                     # required
            }

        Returns:
            RolesResponse:
        """
        return {}

    @transaction
    @convert_model
    def stat(self, params: RoleStatQueryRequest) -> dict:
        """ stat roles

        Args:
            params (PolicyStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # required
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        return {}
