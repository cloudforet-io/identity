import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.workspace_user_manager import WorkspaceUserManager
from spaceone.identity.model.workspace_user.request import *
from spaceone.identity.model.workspace_user.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class WorkspaceUserService(BaseService):
    resource = "WorkspaceUser"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_user_mgr = WorkspaceUserManager()

    @transaction(
        permission="identity:WorkspaceUser.write", role_types=["WORKSPACE_OWNER"]
    )
    @convert_model
    def create(
        self, params: WorkspaceUserCreateRequest
    ) -> Union[WorkspaceUserResponse, dict]:
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
                'role_id': 'str',           # required
                'domain_id': 'str',         # injected from auth (required)
                'workspace_id': 'str',      # injected from auth (required)
            }
        Returns:
            WorkspaceUserResponse:
        """

        user_vo = self.workspace_user_mgr.create_workspace_user(params.dict())
        return WorkspaceUserResponse(**user_vo.to_dict())

    @transaction(
        permission="identity:WorkspaceUser.write",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def find(
        self, params: WorkspaceUserFindRequest
    ) -> Union[UsersSummaryResponse, dict]:
        """Find user
        Args:
            params (UserFindRequest): {
                'keyword': 'str',           # required
                'state': 'str',
                'page': 'dict (spaceone.api.core.v1.Page)',
                'domain_id': 'str',         # injected from auth (required)
                'workspace_id': 'str',      # injected from auth (required)
            }
        Returns:
            UsersSummaryResponse:
        """

        user_mgr = UserManager()
        rb_mgr = RoleBindingManager()
        rb_vos = rb_mgr.filter_role_bindings(
            workspace_id=params.workspace_id, domain_id=params.domain_id
        )
        workspace_user_ids = list(set([rb.user_id for rb in rb_vos]))

        # default query
        query = {
            "filter": [
                {"k": "domain_id", "v": params.domain_id, "o": "eq"},
                {"k": "user_id", "v": workspace_user_ids, "o": "not_in"},
            ],
            "sort": [{"key": "user_id"}],
            "page": params.page,
            "only": ["user_id", "name", "state"],
        }

        # append keyword filter
        if params.keyword:
            query["filter_or"] = [
                {"k": "user_id", "v": params.keyword, "o": "contain"},
                {"k": "name", "v": params.keyword, "o": "contain"},
            ]

        # append state filter
        if params.state:
            query["filter"].append({"k": "state", "v": params.state, "o": "eq"})

        user_vos, total_count = user_mgr.list_users(query)

        users_info = [user_vo.to_dict() for user_vo in user_vos]
        return UsersSummaryResponse(results=users_info, total_count=total_count)

    @transaction(
        permission="identity:WorkspaceUser.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(
        self, params: WorkspaceUserGetRequest
    ) -> Union[WorkspaceUserResponse, dict]:
        """Get user in workspace

        Args:
            params (WorkspaceUserGetRequest): {
                'user_id': 'str',       # required
                'domain_id': 'str',     # injected from auth (required)
                'workspace_id': 'str'   # injected from auth (required)
            }

        Returns:
            WorkspaceUserResponse (object)
        """

        user_info = self.workspace_user_mgr.get_workspace_user(
            params.user_id, params.workspace_id, params.domain_id
        )
        return WorkspaceUserResponse(**user_info)

    @transaction(
        permission="identity:WorkspaceUser.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        ["user_id", "name", "state", "email", "auth_type", "domain_id"]
    )
    @append_keyword_filter(["user_id", "name", "email"])
    @convert_model
    def list(
        self, params: WorkspaceUserSearchQueryRequest
    ) -> Union[WorkspaceUsersResponse, dict]:
        """List users in workspace
        Args:
            params (WorkspaceUserSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_id': 'str',
                'name': 'str',
                'state': 'str',
                'email': 'str',
                'auth_type': 'str',
                'role_type': 'str',
                'domain_id': 'str',     # injected from auth (required)
                'workspace_id': 'str'   # injected from auth (required)
            }
        Returns:
            UsersResponse:
        """

        query = params.query or {}
        users_info, total_count = self.workspace_user_mgr.list_workspace_users(
            query, params.domain_id, params.workspace_id, params.role_type
        )

        return WorkspaceUsersResponse(results=users_info, total_count=total_count)

    @transaction(
        permission="identity:WorkspaceUser.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["domain_id"])
    @convert_model
    def stat(self, params: WorkspaceUserStatQueryRequest) -> dict:
        """stat users in workspace

        Args:
            params (WorkspaceUserStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # injected from auth (required)
                'workspace_id': 'str'       # injected from auth (required)
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }

        """

        query = params.query or {}

        return self.workspace_user_mgr.stat_workspace_users(
            query, params.domain_id, params.workspace_id
        )
