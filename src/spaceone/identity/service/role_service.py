import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.role_request import *
from spaceone.identity.model.role_response import *

_LOGGER = logging.getLogger(__name__)


class RoleService(BaseService):
    @transaction
    @convert_model
    def create(self, params: RoleCreateRequest) -> Union[RoleResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: RoleUpdateRequest) -> Union[RoleResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: RoleDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: RoleGetRequest) -> Union[RoleResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: RoleSearchQueryRequest) -> Union[RolesResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: RoleStatQueryRequest) -> dict:
        return {}
