import logging
from typing import Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.identity.model.authorization_request import *
from spaceone.identity.model.authorization_response import *

_LOGGER = logging.getLogger(__name__)


class AuthorizationService(BaseService):
    @transaction
    @convert_model
    def verify(
        self, params: AuthorizationVerifyRequest
    ) -> Union[AuthorizationResponse, dict]:
        return {}
