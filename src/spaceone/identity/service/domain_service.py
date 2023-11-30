import logging
from typing import Union

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.external_auth_manager import ExternalAuthManager
from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.domain_secret_manager import DomainSecretManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.user_manager import UserManager
from spaceone.identity.model.domain.request import *
from spaceone.identity.model.domain.response import *
from spaceone.identity.error.error_domain import *

_LOGGER = logging.getLogger(__name__)


class DomainService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.domain_secret_mgr = DomainSecretManager()
        self.user_mgr = UserManager()
        self.role_manager = RoleManager()

    @transaction
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

        # create admin user with policy and role
        params_admin = params.admin
        params_admin["auth_type"] = "LOCAL"
        params_admin["user_type"] = "USER"
        params_admin["domain_id"] = domain_vo.domain_id

        user_vo = self.user_mgr.create_user(params_admin)
        role_vos = self.role_manager.filter_roles(domain_id=domain_vo.domain_id, role_type="DOMAIN_ADMIN")

        if len(role_vos) == 0:
            raise ERROR_NOT_DEFINED_DOMAIN_ADMIN()

        role_binding_mgr = RoleBindingManager()
        params_rb = {
            "user_id": user_vo.user_id,
            "role_id": role_vos[0].role_id,
            "scope": "DOMAIN",
            "domain_id": user_vo.domain_id,
        }
        role_binding_mgr.create_role_binding(params_rb)

        return DomainResponse(**domain_vo.to_dict())

    @transaction
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

    @transaction
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
        self.domain_mgr.delete_domain_by_vo(domain_vo)

    @transaction
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
        domain_vo = self.domain_mgr.enable_domain(domain_vo)
        return DomainResponse(**domain_vo.to_dict())

    @transaction
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
        domain_vo = self.domain_mgr.disable_domain(domain_vo)
        return DomainResponse(**domain_vo.to_dict())

    @transaction
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

    @transaction
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
        external_auth_vos = external_auth_mgr.filter_external_auth(domain_id=domain_vo.domain_id)

        if external_auth_vos.count() == 0:
            response = {
                "domain_id": domain_vo.domain_id,
                "name": domain_vo.name,
                "external_auth_state": "DISABLED",
                "metadata": {},
            }
        else:
            response = {
                "domain_id": domain_vo.domain_id,
                "name": domain_vo.name,
                "external_auth_state": "ENABLED",
                "metadata": external_auth_vos[0].plugin_info.get("metadata", {}),
            }

        return DomainAuthInfoResponse(**response)

    @transaction
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

        pub_jwk = self.domain_secret_mgr.get_domain_public_key(params.domain_id)
        return DomainSecretResponse(public_key=str(pub_jwk), domain_id=params.domain_id)

    @transaction
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

    @transaction
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
