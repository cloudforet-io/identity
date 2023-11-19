import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.token_request import *
from spaceone.identity.model.token_response import *


_LOGGER = logging.getLogger(__name__)


class TokenService(BaseService):
    @transaction
    @convert_model
    def issue(self, params: TokenIssueRequest) -> Union[TokenResponse, dict]:
        return {}

    @transaction
    @convert_model
    def refresh(self, params: dict) -> Union[TokenResponse, dict]:
        return {}

