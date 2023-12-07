import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.model.role_binding.request import *
from spaceone.identity.model.role_binding.response import *
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.error.error_role import ERROR_NOT_ALLOWED_ROLE_TYPE

_LOGGER = logging.getLogger(__name__)


class RoleBindingService(BaseService):

    service = "identity"
    resource = "RoleBinding"
    permission_group = "COMPOUND"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_binding_manager = RoleBindingManager()
        self.user_mgr = UserManager()

    @transaction(scope="workspace_owner:write")
    @convert_model
    def create(self, params: RoleBindingCreateRequest) -> Union[RoleBindingResponse, dict]:
        """ create role binding

         Args:
            params (RoleBindingCreateRequest): {
                'user_id': 'str',                   # required
                'role_id': 'str',                   # required
                'permission_group': 'str',          # required
                'workspace_id': 'str',
                'domain_id': 'str'                  # required
            }

        Returns:
            RoleBindingResponse:
        """

        rb_vo = self.create_role_binding(params.dict())
        return RoleBindingResponse(**rb_vo.to_dict())

    def create_role_binding(self, params: dict):
        user_id = params['user_id']
        role_id = params['role_id']
        permission_group = params['permission_group']
        domain_id = params['domain_id']
        workspace_id = params.get('workspace_id')

        # Check user
        user_vo = self.user_mgr.get_user(user_id, domain_id)

        # Check workspace
        if permission_group == 'WORKSPACE':
            if workspace_id != '*':
                workspace_mgr = WorkspaceManager()
                workspace_mgr.get_workspace(workspace_id, domain_id)
        else:
            params['workspace_id'] = '*'

        # Check role
        role_mgr = RoleManager()
        role_vo = role_mgr.get_role(role_id, domain_id)

        if permission_group == 'DOMAIN':
            if role_vo.role_type not in ['SYSTEM_ADMIN', 'DOMAIN_ADMIN']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['DOMAIN_ADMIN'])
        else:
            if role_vo.role_type not in ['WORKSPACE_OWNER', 'WORKSPACE_MEMBER']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['WORKSPACE_OWNER', 'WORKSPACE_MEMBER'])

        # TODO: check duplication of role_binding

        params['role_type'] = role_vo.role_type

        # Update user role type
        latest_role_type = self._get_latest_role_type(user_vo.role_type, role_vo.role_type)
        self.user_mgr.update_user_by_vo({'role_type': latest_role_type}, user_vo)

        # Create role binding
        return self.role_binding_manager.create_role_binding(params)

    @transaction(scope="workspace_owner:write")
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

        request_user_id = self.transaction.get_meta('user_id')

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        # TODO: check request_user_id is same with user_id of role_binding
        # TODO: check this user is last admin of domain or system

        # Check role
        role_mgr = RoleManager()
        new_role_vo = role_mgr.get_role(params.role_id, params.domain_id)

        if rb_vo.role_type in ['WORKSPACE_OWNER', 'WORKSPACE_MEMBER']:
            if new_role_vo.role_type not in ['WORKSPACE_OWNER', 'WORKSPACE_MEMBER']:
                raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=['WORKSPACE_OWNER', 'WORKSPACE_MEMBER'])
        elif rb_vo.role_type != new_role_vo.role_type:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE(supported_role_type=[rb_vo.role_type])

        user_vo = self.user_mgr.get_user(rb_vo.user_id, rb_vo.domain_id)

        latest_role_type = self._get_latest_role_type(rb_vo.role_type, new_role_vo.role_type)
        self.user_mgr.update_user_by_vo({'role_type': latest_role_type}, user_vo)

        rb_vo = self.role_binding_manager.update_role_binding_by_vo(
            {
                'role_id': params.role_id,
                'role_type': new_role_vo.role_type
            },
            rb_vo
        )

        return RoleBindingResponse(**rb_vo.to_dict())

    @transaction(scope="workspace_owner:write")
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

    @transaction(scope="workspace_owner:write")
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

        request_user_id = self.transaction.get_meta('user_id')

        rb_vo = self.role_binding_manager.get_role_binding(
            params.role_binding_id, params.domain_id, params.workspace_id
        )

        # TODO: check request_user_id is same with user_id of role_binding
        # TODO: check this user is last admin of domain or system

        # Update user role type
        remain_rb_vos = self.role_binding_manager.filter_role_bindings(
            domain_id=params.domain_id,
            user_id=rb_vo.user_id
        )

        latest_role_type = 'USER'
        for remain_rb_vo in remain_rb_vos:
            if remain_rb_vo.role_binding_id == params.role_binding_id:
                continue

            latest_role_type = self._get_latest_role_type(latest_role_type, remain_rb_vo.role_type)

        user_vo = self.user_mgr.get_user(rb_vo.user_id, rb_vo.domain_id)
        self.user_mgr.update_user_by_vo({'role_type': latest_role_type}, user_vo)

        self.role_binding_manager.delete_role_binding_by_vo(rb_vo)

    @transaction(scope="workspace_owner:read")
    @append_query_filter([
        'role_binding_id', 'user_id', 'role_id', 'scope', 'workspace_id', 'domain_id'
    ])
    @append_keyword_filter(['role_binding_id', 'user_id', 'role_id'])
    @convert_model
    def list(self, params: RoleBindingSearchQueryRequest) -> Union[RoleBindingsResponse, dict]:
        """ list role bindings

        Args:
            params (RoleBindingSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_binding_id': 'str',
                'role_type': 'str',
                'user_id': 'str',
                'role_id': 'str',
                'permission_group': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',                     # required
            }

        Returns:
            RoleBindingsResponse:
        """

        query = params.query or {}
        rb_vos, total_count = self.role_binding_manager.list_role_bindings(query)

        rbs_info = [rb_vo.to_dict() for rb_vo in rb_vos]
        return RoleBindingsResponse(results=rbs_info, total_count=total_count)

    @transaction(scope="workspace_owner:read")
    @append_query_filter(['workspace_id', 'domain_id'])
    @append_keyword_filter(['role_binding_id', 'user_id', 'role_id'])
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

        query = params.query or {}
        return self.role_binding_manager.stat_role_bindings(query)

    @staticmethod
    def _get_latest_role_type(before: str, after: str) -> str:
        priority = {
            'SYSTEM': 1,
            'SYSTEM_ADMIN': 2,
            'DOMAIN_ADMIN': 3,
            'WORKSPACE_OWNER': 4,
            'WORKSPACE_MEMBER': 5,
            'USER': 6
        }

        before_priority = priority.get(before, 6)
        after_priority = priority.get(after, 6)

        if before_priority < after_priority:
            return before
        else:
            return after
