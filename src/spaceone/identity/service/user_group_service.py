import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.user_group_request import *
from spaceone.identity.model.user_group_response import *

_LOGGER = logging.getLogger(__name__)


class UserGroupService(BaseService):
    @transaction
    @convert_model
    def create(self, params: UserGroupCreateRequest) -> Union[UserGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: UserGroupUpdateRequest) -> Union[UserGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: UserGroupDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def add_users(
        self, params: UserGroupAddUsersRequest
    ) -> Union[UserGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def remove_users(
        self, params: UserGroupRemoveUsersRequest
    ) -> Union[UserGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get(self, params: UserGroupGetRequest) -> Union[UserGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: UserGroupSearchQueryRequest
    ) -> Union[UserGroupsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: UserGroupStatQueryRequest) -> dict:
        return {}
