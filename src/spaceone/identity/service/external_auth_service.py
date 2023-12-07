import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.external_auth_manager import ExternalAuthManager
from spaceone.identity.model.external_auth.request import *
from spaceone.identity.model.external_auth.response import *

_LOGGER = logging.getLogger(__name__)


class ExternalAuthService(BaseService):

    service = "identity"
    resource = "ExternalAuth"
    permission_group = "DOMAIN"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.external_auth_mgr = ExternalAuthManager()

    @transaction(scope='domain_admin:write')
    @convert_model
    def set(self, params: ExternalAuthSetRequest) -> Union[ExternalAuthResponse, dict]:
        """Set external auth info
        Args:
            params (dict): {
                'domain_id': 'str',
                'plugin_info': 'dict'
            }
        Returns:
            ExternalAuthResponse:
        """

        domain_mgr = DomainManager()
        domain_vo = domain_mgr.get_domain(params.domain_id)

        external_auth_vo = self.external_auth_mgr.set_external_auth(
            params.dict(), domain_vo
        )

        return ExternalAuthResponse(**external_auth_vo.to_dict())

    @transaction(scope='domain_admin:write')
    @convert_model
    def unset(
        self, params: ExternalAuthUnsetRequest
    ) -> Union[ExternalAuthResponse, dict]:
        """Unset external auth info
        Args:
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            ExternalAuthResponse:
        """

        return {}

    @transaction(scope='domain_admin:read')
    @convert_model
    def get(self, params: ExternalAuthGetRequest) -> Union[ExternalAuthResponse, dict]:
        """Get external auth info
        Args:
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            ExternalAuthResponse:
        """

        external_auth_vo = self.external_auth_mgr.get_external_auth(params.domain_id)
        return ExternalAuthResponse(**external_auth_vo.to_dict())
