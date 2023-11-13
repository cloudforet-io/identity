import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.policy_request import *
from spaceone.identity.model.policy_response import *

_LOGGER = logging.getLogger(__name__)


class PolicyService(BaseService):
    @transaction
    @convert_model
    def create(self, params: PolicyCreateRequest) -> Union[PolicyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: PolicyUpdateRequest) -> Union[PolicyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: PolicyDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: PolicyGetRequest) -> Union[PolicyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: PolicySearchQueryRequest) -> Union[PoliciesResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: PolicyStatQueryRequest) -> dict:
        return {}
