import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.api_key.request import *
from spaceone.identity.model.api_key.response import *

_LOGGER = logging.getLogger(__name__)


class APIKeyService(BaseService):
    @transaction
    @convert_model
    def create(self, params: APIKeyCreateRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: APIKeyUpdateRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def enable(self, params: APIKeyEnableRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def disable(self, params: APIKeyDisableRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: APIKeyDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: APIKeyGetRequest) -> Union[APIKeyResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: APIKeySearchQueryRequest) -> Union[APIKeysResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: APIKeyStatQueryRequest) -> dict:
        return {}
