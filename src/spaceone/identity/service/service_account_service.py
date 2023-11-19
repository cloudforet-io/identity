import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.service_account_request import *
from spaceone.identity.model.service_account_response import *

_LOGGER = logging.getLogger(__name__)


class ServiceAccountService(BaseService):
    @transaction
    @convert_model
    def create(
        self, params: ServiceAccountCreateRequest
    ) -> Union[ServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(
        self, params: ServiceAccountUpdateRequest
    ) -> Union[ServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def change_trusted_service_account(
        self, params: ServiceAccountChangeTrustedServiceAccountRequest
    ) -> Union[ServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def change_project(
        self, params: ServiceAccountChangeProjectRequest
    ) -> Union[ServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: ServiceAccountDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(
        self, params: ServiceAccountGetRequest
    ) -> Union[ServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: ServiceAccountSearchQueryRequest
    ) -> Union[ServiceAccountsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: ServiceAccountStatQueryRequest) -> dict:
        return {}
