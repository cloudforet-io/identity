import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.identity.model.role.request import *
from spaceone.identity.model.role.response import *
from spaceone.identity.manager.role_manager import RoleManager

_LOGGER = logging.getLogger(__name__)


class RoleService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_mgr = RoleManager()

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @convert_model
    def create(self, params: RoleCreateRequest) -> Union[RoleResponse, dict]:
        """ create role

         Args:
            params (RoleCreateRequest): {
                'name': 'str',                          # required
                'role_type': 'list',                    # required
                'api_permissions': 'list',              # required
                'page_permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'                      # required
            }

        Returns:
            RoleResponse:
        """

        # Check API Permissions

        role_vo = self.role_mgr.create_role(params.dict())
        return RoleResponse(**role_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @convert_model
    def update(self, params: RoleUpdateRequest) -> Union[RoleResponse, dict]:
        """ update role

         Args:
            params (RoleUpdateRequest): {
                'role_id': 'str',                       # required
                'name': 'str',
                'api_permissions': 'list',
                'page_permissions': 'list',
                'tags': 'dict',
                'domain_id': 'str'                      # required
            }

        Returns:
            RoleResponse:
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)

        if params.api_permissions:
            # Check API Permissions
            pass

        role_vo = self.role_mgr.update_role_by_vo(
            params.dict(exclude_unset=True), role_vo
        )

        return RoleResponse(**role_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
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

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        self.role_mgr.delete_role_by_vo(role_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
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

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        return RoleResponse(**role_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @append_query_filter(['role_id', 'role_type', 'domain_id'])
    @append_keyword_filter(['role_id', 'name'])
    @convert_model
    def list(self, params: RoleSearchQueryRequest) -> Union[RolesResponse, dict]:
        """ list roles

        Args:
            params (RoleSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_id': 'str',
                'role_type': 'str',
                'domain_id': 'str',                     # required
            }

        Returns:
            RolesResponse:
        """

        query = params.query or {}
        role_vos, total_count = self.role_mgr.list_roles(query)

        roles_info = [role_vo.to_dict() for role_vo in role_vos]
        return RolesResponse(results=roles_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_READ'})
    @append_query_filter(['domain_id'])
    @append_keyword_filter(['role_id', 'name'])
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

        query = params.query or {}
        return self.role_mgr.stat_roles(query)
