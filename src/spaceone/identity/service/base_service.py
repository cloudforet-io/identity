import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.domain_request import *
from spaceone.identity.model.domain_response import *

_LOGGER = logging.getLogger(__name__)


class BaseService(BaseService):
    @transaction
    @convert_model
    def create(self, params: DomainCreateRequest) -> Union[DomainResponse, dict]:
        return {}

    @transaction
    @convert_model
    def update(self, params: DomainUpdateRequest) -> Union[DomainResponse, dict]:
        return {}

    @transaction
    @convert_model
    def delete(self, params: DomainRequest) -> None:
        pass

    @transaction
    @convert_model
    def get(self, params: DomainRequest) -> Union[DomainResponse, dict]:
        return {}

    @transaction
    @convert_model
    def list(self, params: DomainSearchQueryRequest) -> Union[DomainsResponse, dict]:
        return {}

    @transaction
    @convert_model
    def stat(self, params: DomainStatQuery) -> dict:
        return {}
