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
            params (dict): {
                'name': 'str',
                'admin': 'dict',
                'tags': 'dict'
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.create_domain(params.dict())

        # create domain secret
        self.domain_secret_mgr.create_domain_secret(domain_vo.domain_id)

        # create admin user with policy and role
        admin = params.admin
        admin["auth_type"] = "LOCAL"
        admin["user_type"] = "USER"
        admin["domain_id"] = domain_vo.domain_id

        user_vo = self.user_mgr.create_user(admin)
        role_vos, total_counts = self.role_manager.list_roles(
            {"domain_id": domain_vo.domain_id}
        )
        for role_vo in role_vos:
            if role_vo.role_type == "DOMAIN_ADMIN":
                role_binding_mgr = RoleBindingManager()
                params_rb = {
                    "user_id": user_vo.user_id,
                    "role_id": role_vo.role_id,
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
            params (dict): {
                'domain_id': 'str',
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
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            Empty:
        """
        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        self.domain_mgr.delete_domain_by_vo(domain_vo)

    @transaction
    @convert_model
    def enable(self, params: DomainEnableRequest) -> Union[DomainResponse, dict]:
        """Enable Domain
        Args:
            params (dict): {
                'domain_id': 'str'
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
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            DomainResponse:
        """
        domain_vo = self.domain_mgr.disable_domain(params.domain_id)
        return DomainResponse(**domain_vo.to_dict())

    @transaction
    @convert_model
    def get(self, params: DomainGetRequest) -> Union[DomainResponse, dict]:
        """Get Domain
        Args:
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            DomainResponse:
        """

        domain_vo = self.domain_mgr.get_domain(params.domain_id)
        return DomainResponse(**domain_vo.to_dict())

    @transaction
    @convert_model
    def get_metadata(
        self, params: DomainGetMetadataRequest
    ) -> Union[DomainMetadataResponse, dict]:
        """GetMetadata domain
        Args:
            params (dict): {
                'name': 'str'
            }
        Returns:
            DomainMetadataResponse:
        """
        domain_vo = self.domain_mgr.get_domain_by_name(params.name)
        external_auth_mgr = ExternalAuthManager()
        try:
            external_auth_vo = external_auth_mgr.get_external_auth(domain_vo.domain_id)
            params = {
                "domain_id": domain_vo.domain_id,
                "name": domain_vo.name,
                "external_auth_state": external_auth_vo.state,
                "metadata": external_auth_vo.plugin_info.get("metadata", {}),
            }
        except Exception as e:
            params = {
                "domain_id": domain_vo.domain_id,
                "name": domain_vo.name,
                "external_auth_state": "DISABLED",
                "metadata": {},
            }

        return DomainMetadataResponse(**params)

    @transaction
    @convert_model
    def get_public_key(
        self, params: DomainGetPublicKeyRequest
    ) -> Union[DomainSecretResponse, dict]:
        """GetPublicKey domain
        Args:
            params (dict): {
                'domain_id': 'str'
            }
        Returns:
            DomainSecretResponse:
        """
        pub_jwk = self.domain_secret_mgr.get_domain_public_key(params.domain_id)
        return DomainSecretResponse(
            **{
                "public_key": str(pub_jwk),
                "domain_id": params.domain_id,
            }
        )

    @transaction
    @append_query_filter(["domain_id", "name", "state"])
    @append_keyword_filter(["domain_id", "name"])
    @convert_model
    def list(self, params: DomainSearchQueryRequest) -> Union[DomainsResponse, dict]:
        """List domain
        Args:
            params (dict): {
                'query': 'dict',
                'domain_id': 'str',
                'name': 'str',
                'state': 'str'
            }
        Returns:
            DomainsResponse:
        """

        query = params.dict().get("query", {})

        # todo : remove when spacectl template is modified
        only = [field for field in query.get("only", []) if "plugin_info" not in field]
        query["only"] = only

        domain_vos, total_count = self.domain_mgr.list_domains(query)
        domains_info = [domain_vo.to_dict() for domain_vo in domain_vos]
        return DomainsResponse(results=domains_info, total_count=total_count)

    @transaction
    @convert_model
    def stat(self, params: DomainStatQueryRequest) -> dict:
        """Stat domain
        Args:
            params (dict): {
                'query': 'dict'
            }
        Returns:
            dict:
        """
        query = params.dict().get("query", {})

        return self.domain_mgr.stat_domains(query)
