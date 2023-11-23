import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.project_group.request import *
from spaceone.identity.model.project_group.response import *

_LOGGER = logging.getLogger(__name__)


class ProjectGroupService(BaseService):
    @transaction
    @convert_model
    def create(
        self, params: ProjectGroupCreateRequest
    ) -> Union[ProjectGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(
        self, params: ProjectGroupUpdateRequest
    ) -> Union[ProjectGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def change_parent_group(
        self, params: ProjectChangeParentGroupRequest
    ) -> Union[ProjectGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: ProjectGroupDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: ProjectGroupGetRequest) -> Union[ProjectGroupResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: ProjectGroupSearchQueryRequest
    ) -> Union[ProjectGroupsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: ProjectGroupStatQueryRequest) -> dict:
        return {}
