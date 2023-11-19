import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.external_auth_request import *
from spaceone.identity.model.external_auth_response import *

_LOGGER = logging.getLogger(__name__)


class ExternalAuthService(BaseService):
    @transaction
    @convert_model
    def set(self, params: ExternalAuthSetRequest) -> Union[ExternalAuthResponse, dict]:
        return {}

    @transaction
    @convert_model
    def unset(
        self, params: ExternalAuthUnsetRequest
    ) -> Union[ExternalAuthResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get(self, params: ExternalAuthGetRequest) -> Union[ExternalAuthResponse, dict]:
        return {}
