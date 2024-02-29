import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.core import utils
from spaceone.core.auth.jwt import JWTAuthenticator

from spaceone.identity.manager.external_auth_manager import ExternalAuthManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.manager.config_manager import ConfigManager
from spaceone.identity.manager.system_manager import SystemManager
from spaceone.identity.model.domain.request import *
from spaceone.identity.model.domain.response import *
from spaceone.identity.error.error_domain import *
from spaceone.identity.service.user_service import UserService

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class DomainService(BaseService):
    resource = "Domain"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.user_mgr = UserManager()
        self.role_manager = RoleManager()

    @transaction(permission="identity:Domain.write", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def create(self, params: DomainCreateRequest) -> Union[DomainResponse, dict]:
        """Create Domain
        Args:
            params (DomainCreateRequest): {
                'name': 'str',      # required
                'admin': 'dict',    # required
                'tags': 'dict'
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.create_domain(params.dict())

        # create domain secret
        self.domain_secret_mgr.create_domain_secret(domain_vo)

        # create default role
        role_mgr = RoleManager()
        role_mgr.list_roles({}, domain_vo.domain_id)
        role_vos = self.role_manager.filter_roles(
            domain_id=domain_vo.domain_id, role_type="DOMAIN_ADMIN"
        )

        if len(role_vos) == 0:
            raise ERROR_DOMAIN_ADMIN_ROLE_IS_NOT_DEFINED()

        # create admin user
        params_admin = params.admin.dict()
        params_admin["auth_type"] = "LOCAL"
        params_admin["domain_id"] = domain_vo.domain_id
        params_admin["role_type"] = "DOMAIN_ADMIN"
        params_admin["role_id"] = "managed-domain-admin"
        params_admin["reset_password"] = params_admin.get("reset_password", True)
        if params_admin.get("email") is None:
            params_admin["email"] = params_admin["user_id"]

        user_service = UserService()
        user_vo = user_service.create_user(params_admin)

        # create role binding
        role_binding_mgr = RoleBindingManager()
        params_rb = {
            "user_id": user_vo.user_id,
            "role_id": role_vos[0].role_id,
            "scope": "DOMAIN",
            "domain_id": user_vo.domain_id,
            "role_type": role_vos[0].role_type,
        }
        role_binding_mgr.create_role_binding(params_rb)

        return DomainResponse(**domain_vo.to_dict())

    @transaction(permission="identity:Domain.write", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def update(self, params: DomainUpdateRequest) -> Union[DomainResponse, dict]:
        """Update domain
        Args:
            params (DomainUpdateRequest): {
                'domain_id': 'str',     # required
                'name': 'str',
                'tags': 'dict'
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        domain_vo = self.domain_mgr.update_domain_by_vo(
            params.dict(exclude_unset=True), domain_vo
        )
        return DomainResponse(**domain_vo.to_dict())

    @transaction(permission="identity:Domain.write", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def delete(self, params: DomainDeleteRequest) -> None:
        """Delete Domain
        Args:
            params (DomainCreateRequest): {
                'domain_id': 'str'      # required
            }
        Returns:
            None
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        if domain_vo.domain_id == SystemManager.get_root_domain_id():
            raise ERROR_PERMISSION_DENIED()

        self.domain_mgr.delete_domain_by_vo(domain_vo)

    @transaction(permission="identity:Domain.write", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def enable(self, params: DomainEnableRequest) -> Union[DomainResponse, dict]:
        """Enable Domain
        Args:
            params (DomainEnableRequest): {
                'domain_id': 'str'      # required
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        if domain_vo.domain_id == SystemManager.get_root_domain_id():
            raise ERROR_PERMISSION_DENIED()

        domain_vo = self.domain_mgr.enable_domain(domain_vo)
        return DomainResponse(**domain_vo.to_dict())

    @transaction(permission="identity:Domain.write", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def disable(self, params: DomainDisableRequest) -> Union[DomainResponse, dict]:
        """Disable Domain
        Args:
            params (DomainDisableRequest): {
                'domain_id': 'str'      # required
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)

        if domain_vo.domain_id == SystemManager.get_root_domain_id():
            raise ERROR_PERMISSION_DENIED()

        domain_vo = self.domain_mgr.disable_domain(domain_vo)
        return DomainResponse(**domain_vo.to_dict())

    @transaction(permission="identity:Domain.read", role_types=["SYSTEM_ADMIN"])
    @convert_model
    def get(self, params: DomainGetRequest) -> Union[DomainResponse, dict]:
        """Get Domain
        Args:
            params (DomainGetRequest): {
                'domain_id': 'str'      # required
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        return DomainResponse(**domain_vo.to_dict())

    @transaction(exclude=["authentication", "authorization", "mutation"])
    @convert_model
    def get_auth_info(
        self, params: DomainGetAuthInfoRequest
    ) -> Union[DomainAuthInfoResponse, dict]:
        """GetMetadata domain
        Args:
            params (DomainGetAuthInfoRequest): {
                'name': 'str'       # required
            }
        Returns:
            DomainAuthInfoResponse:
        """

        domain_vo = self.domain_mgr.get_domain_by_name(params.name)
        external_auth_mgr = ExternalAuthManager()
        external_auth_info = external_auth_mgr.get_auth_info(domain_vo)

        config_mgr = ConfigManager()
        external_auth_info["config"] = config_mgr.get_auth_config(domain_vo.domain_id)

        return DomainAuthInfoResponse(**external_auth_info)

    @transaction(exclude=["authentication", "authorization", "mutation"])
    @convert_model
    def get_public_key(
        self, params: DomainGetPublicKeyRequest
    ) -> Union[DomainSecretResponse, dict]:
        """GetPublicKey domain
        Args:
            params (DomainGetPublicKeyRequest): {
                'domain_id': 'str'      # required
            }
        Returns:
            DomainSecretResponse:
        """

        # Check System Token
        try:
            token = self.transaction.get_meta("token")
            if token is None:
                raise ERROR_UNKNOWN(message="Empty Token provided.")
            root_domain_id = SystemManager.get_root_domain_id()
            root_pub_jwk = self.domain_secret_mgr.get_domain_public_key(root_domain_id)
            JWTAuthenticator(root_pub_jwk).validate(token)
        except Exception as e:
            raise ERROR_UNKNOWN(message="Invalid System Token")

        # Get Public Key from Domain
        pub_jwk = self.domain_secret_mgr.get_domain_public_key(params.domain_id)
        return DomainSecretResponse(
            public_key=utils.dump_json(pub_jwk), domain_id=params.domain_id
        )

    @transaction(permission="identity:Domain.read", role_types=["SYSTEM_ADMIN"])
    @append_query_filter(["domain_id", "name", "state"])
    @append_keyword_filter(["domain_id", "name"])
    @convert_model
    def list(self, params: DomainSearchQueryRequest) -> Union[DomainsResponse, dict]:
        """List domains
        Args:
            params (DomainSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'domain_id': 'str',
                'name': 'str',
                'state': 'str'
            }
        Returns:
            DomainsResponse:
        """

        query = params.query or {}
        domain_vos, total_count = self.domain_mgr.list_domains(query)

        domains_info = [domain_vo.to_dict() for domain_vo in domain_vos]
        return DomainsResponse(results=domains_info, total_count=total_count)

    @transaction(permission="identity:Domain.read", role_types=["SYSTEM_ADMIN"])
    @append_keyword_filter(["domain_id", "name"])
    @convert_model
    def stat(self, params: DomainStatQueryRequest) -> dict:
        """Stat domains
        Args:
            params (DomainStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.domain_mgr.stat_domains(query)
