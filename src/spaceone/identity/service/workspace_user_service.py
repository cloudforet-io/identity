import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.workspace_user_manager import WorkspaceUserManager
from spaceone.identity.model.workspace_user.request import *
from spaceone.identity.model.workspace_user.response import *

_LOGGER = logging.getLogger(__name__)


class WorkspaceUserService(BaseService):

    service = "identity"
    resource = "WorkspaceUser"
    permission_group = "WORKSPACE"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_user_mgr = WorkspaceUserManager()

    @transaction(scope="workspace_owner:write")
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

        user_vo = self.workspace_user_mgr.create_workspace_user(params.dict())
        return WorkspaceUserResponse(**user_vo.to_dict())

    @transaction(scope="workspace_member:read")
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

        user_info = self.workspace_user_mgr.get_workspace_user(
            params.user_id, params.workspace_id, params.domain_id
        )
        return WorkspaceUserResponse(**user_info)

    @transaction(scope="workspace_member:read")
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
                'query': 'dict (spaceone.api.core.v1.Query)',
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
        users_info, total_count = self.workspace_user_mgr.list_workspace_users(
            query, params.domain_id, params.workspace_id
        )

        return WorkspaceUsersResponse(results=users_info, total_count=total_count)

    @transaction(scope="workspace_member:read")
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

        return self.workspace_user_mgr.stat_workspace_users(
            query, params.domain_id, params.workspace_id
        )
