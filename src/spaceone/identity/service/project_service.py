import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.project_request import *
from spaceone.identity.model.project_response import *

_LOGGER = logging.getLogger(__name__)


class ProjectService(BaseService):
    @transaction
    @convert_model
    def create(self, params: ProjectCreateRequest) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: ProjectUpdateRequest) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update_project_type(
        self, params: ProjectUpdateProjectTypeRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def change_project_group(
        self, params: ProjectChangeProjectGroupRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: ProjectDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def add_users(self, params: ProjectAddUsersRequest) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def remove_users(
        self, params: ProjectRemoveUsersRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def add_user_groups(
        self, params: ProjectAddUserGroupsRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def remove_user_groups(
        self, params: ProjectRemoveUserGroupsRequest
    ) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get(self, params: ProjectGetRequest) -> Union[ProjectResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: ProjectSearchQueryRequest) -> Union[ProjectsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: ProjectStatQueryRequest) -> dict:
        return {}
