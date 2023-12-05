import logging
from typing import Union

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)
from spaceone.core.error import *

from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.model.workspace_user.request import *
from spaceone.identity.model.workspace_user.response import *
from spaceone.identity.service.user_service import UserService
from spaceone.identity.service.role_binding_service import RoleBindingService

_LOGGER = logging.getLogger(__name__)


class WorkspaceUserService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mgr = UserManager()
        self.rb_mgr = RoleBindingManager()

    @transaction(append_meta={"authorization.scope": "DOMAIN_OR_WORKSPACE"})
    @convert_model
    def create(self, params: WorkspaceUserCreateRequest) -> Union[WorkspaceUserResponse, dict]:
        """Create user with role binding
        Args:
            params (WorkspaceUserCreateRequest): {
                'user_id': 'str',           # required
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'auth_type': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'dict',
                'reset_password': 'bool',
                'domain_id': 'str',         # required
                'workspace_id': 'str',      # required
                'role_id': 'str',           # required
            }
        Returns:
            WorkspaceUserResponse:
        """

        user_svc = UserService()
        rb_svc = RoleBindingService()

        user_vo = user_svc.create_user(params.dict())

        rb_svc.create_role_binding(
            {
                "user_id": params.user_id,
                "role_id": params.role_id,
                "permission_group": "WORKSPACE",
                "workspace_id": params.workspace_id,
                "domain_id": params.domain_id,
            }
        )

        return WorkspaceUserResponse(**user_vo.to_dict())

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @convert_model
    def get(self, params: WorkspaceUserGetRequest) -> Union[WorkspaceUserResponse, dict]:
        """Get user in workspace

        Args:
            params (WorkspaceUserGetRequest): {
                'user_id': 'str',       # required
                'domain_id': 'str',     # required
                'workspace_id': 'str'   # required
            }

        Returns:
            WorkspaceUserResponse (object)
        """

        user_rb_map = self._get_role_bindings_in_workspace(params.workspace_id, params.domain_id)
        workspace_user_ids = list(user_rb_map.keys())

        if params.user_id not in workspace_user_ids:
            raise ERROR_NOT_FOUND(key='user_id', value=params.user_id)

        user_vo = self.user_mgr.get_user(params.user_id, params.domain_id)
        user_info = user_vo.to_dict()
        user_info["role_binding_info"] = user_rb_map[params.user_id].to_dict()

        return WorkspaceUserResponse(**user_info)

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @append_query_filter(
        [
            "user_id",
            "name",
            "state",
            "email",
            "user_type",
            "auth_type",
            "domain_id",
        ]
    )
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def list(self, params: WorkspaceUserSearchQueryRequest) -> Union[WorkspaceUsersResponse, dict]:
        """List users in workspace
        Args:
            params (WorkspaceUserSearchQueryRequest): {
                'query': 'dict',
                'user_id': 'str',
                'name': 'str',
                'state': 'str',
                'email': 'str',
                'auth_type': 'str',
                'domain_id': 'str',     # required
                'workspace_id': 'str'
            }
        Returns:
            UsersResponse:
        """

        query = params.query or {}
        user_rb_map = None

        if params.workspace_id:
            user_rb_map = self._get_role_bindings_in_workspace(params.workspace_id, params.domain_id)
            workspace_user_ids = list(user_rb_map.keys())
            query["filter"].append({"k": "user_id", "v": workspace_user_ids, "o": "in"})

        user_vos, total_count = self.user_mgr.list_users(query)

        users_info = []
        for user_vo in user_vos:
            user_info = user_vo.to_dict()

            if user_rb_map:
                user_info["role_binding_info"] = user_rb_map[user_vo.user_id].to_dict()

            users_info.append(user_info)

        return WorkspaceUsersResponse(results=users_info, total_count=total_count)

    @transaction(append_meta={"authorization.scope": "DOMAIN_READ"})
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def stat(self, params: WorkspaceUserStatQueryRequest) -> dict:
        """ stat users in workspace

        Args:
            params (WorkspaceUserStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # required
                'workspace_id': 'str'
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}

        if params.workspace_id:
            user_rb_map = self._get_role_bindings_in_workspace(params.workspace_id, params.domain_id)
            workspace_user_ids = list(user_rb_map.keys())
            query["filter"].append({"k": "user_id", "v": workspace_user_ids, "o": "in"})

        return self.user_mgr.stat_users(query)

    def _get_role_bindings_in_workspace(self, workspace_id: str, domain_id: str) -> dict:
        user_rb_map = {}
        rb_vos = self.rb_mgr.filter_role_bindings(
            domain_id=domain_id,
            workspace_id=[workspace_id, '*'],
            role_type=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"]
        )

        for rb_vo in rb_vos:
            user_rb_map[rb_vo.user_id] = rb_vo

        return user_rb_map
