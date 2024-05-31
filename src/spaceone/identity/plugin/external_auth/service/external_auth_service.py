import logging
from typing import Union

from spaceone.core.service import BaseService, transaction
from spaceone.core.service.utils import convert_model

from spaceone.identity.plugin.external_auth.model.external_auth_request import (
    ExternalAuthAuthorizeRequest,
    ExternalAuthInitRequest,
)
from spaceone.identity.plugin.external_auth.model.external_auth_response import (
    PluginResponse,
    UserResponse,
)

_LOGGER = logging.getLogger(__name__)


class ExternalAuthService(BaseService):
    resource = "ExternalAuth"

    @transaction
    @convert_model
    def init(self, params: ExternalAuthInitRequest) -> Union[PluginResponse, dict]:
        """Init external auth data

        Args:
            params (ExternalAuthInitRequest): {
                'options': 'dict',          # Required
                'domain_id': 'str'          # Required
            }

        Returns:
            Generator[PluginResponse, None, None]
            {
                'metadata': 'dict'
            }
        """

        func = self.get_plugin_method("init")
        response = func(params.dict())
        return PluginResponse(**response)

    @transaction
    @convert_model
    def authorize(
        self, params: ExternalAuthAuthorizeRequest
    ) -> Union[UserResponse, dict]:
        """Authorize external auth data

        Args:
            params (ExternalAuthAuthorizeRequest): {
                'options': 'dict',          # Required
                'schema_id': 'str',
                'secret_data': 'dict',      # Required
                'credentials': 'dict',      # Required
                'domain_id': 'str'          # Required
            }

        Returns:
            UserResponse: {
                'state': 'str',
                'user_id': 'str',
                'name': 'str',
                'email': 'str',
                'mobile': 'str',
                'group': 'str',
            }
        """

        func = self.get_plugin_method("authorize")
        response = func(params.dict())
        return UserResponse(**response)
