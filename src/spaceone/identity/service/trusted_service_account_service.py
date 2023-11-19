import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.trusted_service_account_request import *
from spaceone.identity.model.trusted_service_account_response import *

_LOGGER = logging.getLogger(__name__)


class TrustedServiceAccountService(BaseService):
    @transaction
    @convert_model
    def create(
        self, params: TrustedServiceAccountCreateRequest
    ) -> Union[TrustedServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(
        self, params: TrustedServiceAccountUpdateRequest
    ) -> Union[TrustedServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: TrustedServiceAccountDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(
        self, params: TrustedServiceAccountGetRequest
    ) -> Union[TrustedServiceAccountResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: TrustedServiceAccountSearchQueryRequest
    ) -> Union[TrustedServiceAccountsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: TrustedServiceAccountStatQueryRequest) -> dict:
        return {}
