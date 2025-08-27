import logging
from typing import Union

from spaceone.core.error import *
from spaceone.core.service import *
from spaceone.core.service.utils import *

from spaceone.identity.error.custom import ERROR_ROLE_IN_USED_AT_ROLE_BINDING
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.model.role.request import *
from spaceone.identity.model.role.request import BasicRoleSearchQueryRequest
from spaceone.identity.model.role.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class RoleService(BaseService):
    resource = "Role"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_mgr = RoleManager()
        self.rb_mgr = RoleBindingManager()

    @transaction(permission="identity:Role.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def create(self, params: RoleCreateRequest) -> Union[RoleResponse, dict]:
        """create role

         Args:
            params (RoleCreateRequest): {
                'name': 'str',                          # required
                'role_type': 'list',                    # required
                'permissions': 'list',
                'page_access': 'list',
                'tags': 'dict',
                'domain_id': 'str'                      # injected from auth (required)
            }

        Returns:
            RoleResponse:
        """

        role_vo = self.role_mgr.create_role(params.dict())
        return RoleResponse(**role_vo.to_dict())

    @transaction(permission="identity:Role.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def update(self, params: RoleUpdateRequest) -> Union[RoleResponse, dict]:
        """update role

         Args:
            params (RoleUpdateRequest): {
                'role_id': 'str',           # required
                'name': 'str',
                'permissions': 'list',
                'page_access': 'list',
                'tags': 'dict',
                'domain_id': 'str'          # injected from auth (required)
            }

        Returns:
            RoleResponse:
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        if role_vo.is_managed:
            raise ERROR_PERMISSION_DENIED()

        role_vo = self.role_mgr.update_role_by_vo(
            params.dict(exclude_unset=True), role_vo
        )

        return RoleResponse(**role_vo.to_dict())

    @transaction(permission="identity:Role.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def enable(self, params: RoleEnableRequest) -> Union[RoleResponse, dict]:
        """enable role

         Args:
            params (RoleEnableRequest): {
                'role_id': 'str',           # required
                'domain_id': 'str',         # injected from auth (required)
            }
        Returns:
            RoleResponse:
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        role_vo = self.role_mgr.enable_role_by_vo(role_vo)

        return RoleResponse(**role_vo.to_dict())

    @transaction(permission="identity:Role.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def disable(self, params: RoleDisableRequest) -> Union[RoleResponse, dict]:
        """disable role

         Args:
            params (RoleDisableRequest): {
                'role_id': 'str',           # required
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
            RoleResponse:
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)

        rb_vos = self.rb_mgr.filter_role_bindings(
            role_id=role_vo.role_id, domain_id=role_vo.domain_id
        )

        if rb_vos.count() > 0:
            raise ERROR_ROLE_IN_USED_AT_ROLE_BINDING(role_id=role_vo.role_id)

        role_vo = self.role_mgr.disable_role_by_vo(role_vo)

        return RoleResponse(**role_vo.to_dict())

    @transaction(permission="identity:Role.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def delete(self, params: RoleDeleteRequest) -> None:
        """delete role

         Args:
            params (RoleDeleteRequest): {
                'role_id': 'str',       # required
                'domain_id': 'str',     # injected from auth (required)
            }

        Returns:
            None
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        if role_vo.is_managed:
            raise ERROR_PERMISSION_DENIED()

        rb_vos = self.rb_mgr.filter_role_bindings(
            role_id=role_vo.role_id, domain_id=role_vo.domain_id
        )

        if rb_vos.count() > 0:
            raise ERROR_ROLE_IN_USED_AT_ROLE_BINDING(role_id=role_vo.role_id)

        self.role_mgr.delete_role_by_vo(role_vo)

    @transaction(
        permission="identity:Role.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: RoleGetRequest) -> Union[RoleResponse, dict]:
        """get role

         Args:
            params (RoleGetRequest): {
                'role_id': 'str',           # required
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
             RoleResponse:
        """

        role_vo = self.role_mgr.get_role(params.role_id, params.domain_id)
        return RoleResponse(**role_vo.to_dict())

    @transaction(
        permission="identity:Role.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["role_id", "name", "state", "role_type", "domain_id"])
    @append_keyword_filter(["role_id", "name"])
    @convert_model
    def list(self, params: RoleSearchQueryRequest) -> Union[RolesResponse, dict]:
        """list roles

        Args:
            params (RoleSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_id': 'str',
                'name': 'str',
                'state': 'str',
                'role_type': 'str',
                'domain_id': 'str',             # injected from auth (required)
            }

        Returns:
            RolesResponse:
        """

        query = params.query or {}
        role_vos, total_count = self.role_mgr.list_roles(query, params.domain_id)

        roles_info = [role_vo.to_dict() for role_vo in role_vos]
        return RolesResponse(results=roles_info, total_count=total_count)

    @transaction(
        permission="identity:Role.read",
        role_types=["USER"],
    )
    @append_query_filter(["role_id", "name", "state", "role_type", "domain_id"])
    @append_keyword_filter(["role_id", "name"])
    @convert_model
    def list_basic_role(
        self, params: BasicRoleSearchQueryRequest
    ) -> Union[BasicRolesResponse, dict]:
        """list basic roles

        Args:
            params (RoleSearchQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'role_id': 'str',
                'name': 'str',
                'state': 'str',
                'role_type': 'str',
                'domain_id': 'str',        # injected from auth (required)
            }

        Returns:
            BasicRolesResponse:
        """

        query = params.query or {}
        role_vos, total_count = self.role_mgr.list_roles(query, params.domain_id)

        basic_roles_info = [role_vo.to_dict() for role_vo in role_vos]
        return BasicRolesResponse(results=basic_roles_info, total_count=total_count)

    @transaction(
        permission="identity:Role.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["role_id", "name"])
    @convert_model
    def stat(self, params: RoleStatQueryRequest) -> dict:
        """stat roles

        Args:
            params (PolicyStatQueryRequest): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)', # required
                'domain_id': 'str',         # injected from auth (required)
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.role_mgr.stat_roles(query)
