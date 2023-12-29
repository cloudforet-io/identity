import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.external_auth_manager import ExternalAuthManager
from spaceone.identity.model.external_auth.request import *
from spaceone.identity.model.external_auth.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ExternalAuthService(BaseService):
    resource = "ExternalAuth"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.external_auth_mgr = ExternalAuthManager()

    @transaction(permission="identity:ExternalAuth.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def set(self, params: ExternalAuthSetRequest) -> Union[ExternalAuthResponse, dict]:
        """Set external auth info
        Args:
            params (dict): {
                'domain_id': 'str',    # injected from auth (required)
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

    @transaction(permission="identity:ExternalAuth.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def unset(
        self, params: ExternalAuthUnsetRequest
    ) -> Union[ExternalAuthResponse, dict]:
        """Unset external auth info
        Args:
            params (dict): {
                'domain_id': 'str'  # injected from auth (required)
            }
        Returns:
            ExternalAuthResponse:
        """

        external_auth_vo = self.external_auth_mgr.get_external_auth(params.domain_id)
        self.external_auth_mgr.delete_external_auth_by_vo(external_auth_vo)

        return {"domain_id": params.domain_id, "state": "DISABLED"}

    @transaction(permission="identity:ExternalAuth.read", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def get(self, params: ExternalAuthGetRequest) -> Union[ExternalAuthResponse, dict]:
        """Get external auth info
        Args:
            params (dict): {
                'domain_id': 'str' # injected from auth (required)
            }
        Returns:
            ExternalAuthResponse:
        """

        external_auth_vos = self.external_auth_mgr.filter_external_auth(
            domain_id=params.domain_id
        )
        if external_auth_vos.count() > 0:
            external_auth_vo = external_auth_vos[0]
            return ExternalAuthResponse(**external_auth_vo.to_dict())
        else:
            return {"domain_id": params.domain_id, "state": "DISABLED"}
