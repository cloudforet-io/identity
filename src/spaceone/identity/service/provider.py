import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.provider_request import *
from spaceone.identity.model.provider_response import *

_LOGGER = logging.getLogger(__name__)


class Provider(BaseService):
    @transaction
    @convert_model
    def create(self, params: ProviderCreateRequest) -> Union[ProviderResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: ProviderUpdateRequest) -> Union[ProviderResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: ProviderDeleteRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: ProviderGetRequest) -> Union[ProviderResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(
        self, params: ProviderSearchQueryRequest
    ) -> Union[ProvidersResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: ProviderStatQueryRequest) -> dict:
        return {}
