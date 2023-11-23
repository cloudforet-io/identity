import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model, append_query_filter, append_keyword_filter
from spaceone.core.error import *
from spaceone.identity.model.role_binding.request import *
from spaceone.identity.model.role_binding.response import *
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.error.error_role import ERROR_NOT_ALLOWED_ROLE_TYPE

_LOGGER = logging.getLogger(__name__)


class RoleBindingService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_binding_manager = RoleBindingManager()

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
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

        # Check Scope
        if params.scope == 'DOMAIN':
            params.workspace_id = None
        else:
            if not params.workspace_id:
                raise ERROR_REQUIRED_PARAMETER(key='workspace_id')

        # Check user
        user_mgr = UserManager()
        user_mgr.get_user(params.user_id, params.domain_id)

        # Check role
        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(params.role_id, params.domain_id)

        if params.scope == 'DOMAIN':
            if role_vo.role_type not in ['DOMAIN_ADMIN', 'SYSTEM_ADMIN']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['DOMAIN_ADMIN'])
        elif params.scope == 'WORKSPACE':
            if role_vo.role_type not in ['WORKSPACE_ADMIN', 'WORKSPACE_MEMBER']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['WORKSPACE_ADMIN', 'WORKSPACE_MEMBER'])

        params.role_type = role_vo.role_type

        rb_vo = self.role_binding_manager.create_role_binding(params.dict())
        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
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

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        # Check role
        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(params.role_id, params.domain_id)

        if rb_vo.role_type in ['WORKSPACE_OWNER', 'WORKSPACE_MEMBER']:
            if role_vo.role_type not in ['WORKSPACE_OWNER', 'WORKSPACE_MEMBER']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['WORKSPACE_OWNER', 'WORKSPACE_MEMBER'])
        elif rb_vo.role_type != role_vo.role_type:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=[rb_vo.role_type])

        rb_vo = self.role_binding_manager.update_role_binding_by_vo(
            {
                'role_id': params.role_id,
                'role_type': role_vo.role_type
            },
            rb_vo
        )

        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE'})
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

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        self.role_binding_manager.delete_role_binding_by_vo(rb_vo)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
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

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter([
        'role_binding_id', 'user_id', 'role_id', 'scope', 'workspace_id', 'domain_id', 'user_workspaces'
    ])
    @append_keyword_filter(['role_binding_id', 'user_id', 'role_id'])
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
                'user_workspaces': 'list'               # from meta
            }

        Returns:
            RoleBindingsResponse:
        """

        query = params.query or {}
        rb_vos, total_count = self.role_binding_manager.list_role_bindings(query)

        rbs_info = [rb_vo.to_dict() for rb_vo in rb_vos]
        return RoleBindingsResponse(results=rbs_info, total_count=total_count)

    @transaction(append_meta={'authorization.scope': 'DOMAIN_OR_WORKSPACE_READ'})
    @append_query_filter(['domain_id', 'workspace_id', 'user_workspaces'])
    @append_keyword_filter(['role_binding_id', 'user_id', 'role_id'])
    @convert_model
    def stat(self, params: RoleBindingStatQueryRequest) -> dict:
        """ stat role bindings

        Args:
            params (RoleBindingStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'workspace_id': 'str',
                'domain_id': 'str',         # required
                'user_workspaces': 'list'   # from meta
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.role_binding_manager.stat_role_bindings(query)
