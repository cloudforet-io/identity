import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.role_binding_request import *
from spaceone.identity.model.role_binding_response import *

_LOGGER = logging.getLogger(__name__)


class RoleBindingService(BaseService):
    @transaction
    @convert_model
    def create(
        self, params: RoleBindingCreateRequest
    ) -> Union[RoleBindingResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update_role(
        self, params: RoleBindingUpdateRoleRequest
    ) -> Union[RoleBindingResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: RoleBindingDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: RoleBindingGetRequest) -> Union[RoleBindingResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: RoleBindingSearchQueryRequest
    ) -> Union[RoleBindingsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: RoleBindingStatQueryRequest) -> dict:
        return {}
