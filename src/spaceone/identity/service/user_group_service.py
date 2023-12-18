import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.error_user_group import *
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.user_group_manager import UserGroupManager
from spaceone.identity.model.user_group.request import *
from spaceone.identity.model.user_group.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class UserGroupService(BaseService):
    resource = "UserGroup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_group_mgr = UserGroupManager()

    @transaction(permission="identity:UserGroup.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def create(self, params: UserGroupCreateRequest) -> Union[UserGroupResponse, dict]:
        """Create user group
        Args:
            params (dict): {
                'name': 'str',          # required
                'tags': 'dict',         # required
                'workspace_id': 'str',  # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }
        """
        user_group_vo = self.user_group_mgr.create_user_group(params.dict())
        return UserGroupResponse(**user_group_vo.to_dict())

    @transaction(permission="identity:UserGroup.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def update(self, params: UserGroupUpdateRequest) -> Union[UserGroupResponse, dict]:
        """Update user group
        Args:
            params (dict): {
                'user_group_id': 'str', # required
                'name': 'str',
                'tags': 'dict',
                'workspace_id': 'str',  # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }
        """
        user_group_vo = self.user_group_mgr.get_user_group(
            params.user_group_id,
            params.domain_id,
            params.workspace_id,
        )

        user_group_vo = self.user_group_mgr.update_user_group_by_vo(
            params.dict(exclude_unset=True), user_group_vo
        )

        return UserGroupResponse(**user_group_vo.to_dict())

    @transaction(permission="identity:UserGroup.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def delete(self, params: UserGroupDeleteRequest) -> None:
        """Delete user group
        Args:
            params (dict): {
                'user_group_id': 'str', # required
                'workspace_id': 'str',  # injected from auth (required)
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            None
        """

        user_group_vo = self.user_group_mgr.get_user_group(
            params.user_group_id,
            params.domain_id,
            params.workspace_id,
        )
        self.user_group_mgr.delete_user_group_by_vo(user_group_vo)

    @transaction(permission="identity:UserGroup.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def add_users(
        self, params: UserGroupAddUsersRequest
    ) -> Union[UserGroupResponse, dict]:
        """Add users to user group
        Args:
            params (dict): {
                'user_group_id': 'str',     # required
                'users': 'list(str)',       # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            UserGroupResponse:
        """
        user_group_vo = self.user_group_mgr.get_user_group(
            params.user_group_id,
            params.domain_id,
            params.workspace_id,
        )

        user_mgr = UserManager()
        users_vo = user_mgr.filter_users(
            user_id=params.users,
            domain_id=params.domain_id,
            workspace_id=params.workspace_id,
        )

        if users_vo.count() != len(params.users):
            raise ERROR_USERS_NOT_FOUND(
                users=list(set(params.users) - set(users_vo.values_list("user_id")))
            )

        params.users = list(set(user_group_vo.users + params.users))

        user_group_vo = self.user_group_mgr.update_user_group_by_vo(
            params.dict(exclude_unset=True), user_group_vo
        )

        return UserGroupResponse(**user_group_vo.to_dict())

    @transaction(permission="identity:UserGroup.write", role_types=["WORKSPACE_OWNER"])
    @convert_model
    def remove_users(
        self, params: UserGroupRemoveUsersRequest
    ) -> Union[UserGroupResponse, dict]:
        """Remove users from user group
        Args:
            params (dict): {
                'user_group_id': 'str',     # required
                'users': 'list(str)',       # required
                'workspace_id': 'str',      # injected from auth (required)
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            UserGroupResponse:
        """
        user_group_vo = self.user_group_mgr.get_user_group(
            params.user_group_id,
            params.domain_id,
            params.workspace_id,
        )

        user_mgr = UserManager()
        params.users = list(set(user_group_vo.users) - set(params.users))
        users_vo = self.user_group_mgr.update_user_group_by_vo(
            params.dict(exclude_unset=True), user_group_vo
        )
        return UserGroupResponse(**users_vo.to_dict())

    @transaction(
        permission="identity:UserGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: UserGroupGetRequest) -> Union[UserGroupResponse, dict]:
        """Get user group
        Args:
            params (dict): {
                'user_group_id': 'str', # required
                'workspace_id': 'str',  # injected from auth
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            UserGroupResponse:
        """

        user_group_vo = self.user_group_mgr.get_user_group(
            params.user_group_id,
            params.domain_id,
            params.workspace_id,
        )
        return UserGroupResponse(**user_group_vo.to_dict())

    @transaction(
        permission="identity:UserGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "user_group_id",
            "name",
            "user_id",
            "workspace_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["trusted_account_id", "name"])
    @convert_model
    def list(
        self, params: UserGroupSearchQueryRequest
    ) -> Union[UserGroupsResponse, dict]:
        """List user groups
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_group_id': 'str',
                'name': 'str',
                'user_id': 'str',
                'workspace_id': 'str',  # injected from auth
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            UserGroupsResponse:
        """
        query = params.query or {}
        user_group_vos, total_count = self.user_group_mgr.list_user_groups(query)

        user_groups_info = [user_group_vo.to_dict() for user_group_vo in user_group_vos]
        return UserGroupsResponse(results=user_groups_info, total_count=total_count)

    @transaction(
        permission="identity:UserGroup.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["workspace_id", "domain_id"])
    @append_keyword_filter(["user_group_id", "name"])
    @convert_model
    def stat(self, params: UserGroupStatQueryRequest) -> dict:
        """Stat user groups
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'workspace_id': 'str',  # injected from auth
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """
        query = params.query or {}
        return self.user_group_mgr.stat_user_group(query)
