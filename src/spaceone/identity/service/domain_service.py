import logging
from typing import Union, List

from spaceone.core.service import (
    BaseService,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.domain_manager import DomainManager
from spaceone.identity.manager.user_manager import UserManager

# from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.model.domain_request import *
from spaceone.identity.model.domain_response import *

_LOGGER = logging.getLogger(__name__)


class DomainService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_mgr = DomainManager()
        self.user_mgr = UserManager()
        # self.role_manager = RoleManager()

    @transaction
    @convert_model
    def create(self, params: DomainCreateRequest) -> Union[DomainResponse, dict]:
        """
        Args:
        :param params:
        :return:
        """

        domain_vo = self.domain_mgr.create_domain(params.dict())
        admin = params.admin
        admin["auth_type"] = "LOCAL"
        admin["user_type"] = "USER"
        admin["domain_id"] = domain_vo.domain_id

        # create admin user with policy and role
        self.user_mgr.create_user(params=admin)
        return DomainResponse.from_orm(domain_vo)

    @transaction
    @convert_model
    def update(self, params: DomainUpdateRequest) -> Union[DomainResponse, dict]:
        domain_vo = self.domain_mgr.update_domain(params.dict())
        return DomainResponse.from_orm(domain_vo)

    @transaction
    @convert_model
    def delete(self, params: DomainRequest) -> None:
        self.domain_mgr.delete_domain(params.dict().get("domain_id"))

    @transaction
    @convert_model
    def enable(self, params: DomainRequest) -> Union[DomainResponse, dict]:
        domain_vo = self.domain_mgr.enable_domain(params.dict().get("domain_id"))
        return DomainResponse.from_orm(domain_vo)

    @transaction
    @convert_model
    def disable(self, params: DomainRequest) -> Union[DomainResponse, dict]:
        domain_vo = self.domain_mgr.disable_domain(params.dict().get("domain_id"))
        return DomainResponse.from_orm(domain_vo)

    @transaction
    @convert_model
    def get(self, params: DomainRequest) -> Union[DomainResponse, dict]:
        domain_vo = self.domain_mgr.get_domain(params.dict().get("domain_id"))
        return DomainResponse.from_orm(domain_vo)

    @transaction
    @convert_model
    def get_metadata(
        self, params: DomainGetMetadataRequest
    ) -> Union[DomainMetadataResponse, dict]:
        return {}

    @transaction
    @convert_model
    def get_public_key(
        self, params: DomainRequest
    ) -> Union[DomainSecretResponse, dict]:
        return {}

    @transaction
    # @append_query_filter(["domain_id", "name"])
    # @append_keyword_filter(["domain_id", "name"])
    @convert_model
    def list(self, params: DomainSearchQueryRequest) -> Union[DomainsResponse, dict]:
        query = params.dict().get("query", {})

        # todo : remove when spacectl template is modified
        only = [field for field in query.get("only", []) if "plugin_info" not in field]
        query["only"] = only

        domain_vos, total_count = self.domain_mgr.list_domains(query)

        return DomainsResponse(results=list(domain_vos), total_count=total_count)

    @transaction
    @convert_model
    def stat(self, params: DomainStatQueryRequest) -> dict:
        query = params.dict().get("query", {})

        return self.domain_mgr.stat_domains(query)
